"""Prueba local del paquete completo sin modificar proyectos del usuario."""
import json
import math
from dataclasses import replace
from pathlib import Path
import tempfile

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from socavacion_ll.dominio.modelos import PuntoTerreno, proyecto_ejemplo
from socavacion_ll.presentacion.ventana import VentanaPrincipal
from .proyectos import abrir_proyecto, guardar_proyecto
from .reportes import exportar_pdf, exportar_word

_aplicacion = None


def comprobar_instalacion(directorio):
    """Crear evidencia en una subcarpeta única; devolver la ruta del informe JSON."""
    global _aplicacion
    destino = Path(directorio)
    destino.mkdir(parents=True, exist_ok=True)
    carpeta = Path(tempfile.mkdtemp(prefix="comprobacion-", dir=destino))
    _aplicacion = QApplication.instance() or QApplication([])
    for nombre in ("segoeui.ttf", "segoeuib.ttf", "seguisym.ttf"):
        fuente = Path("C:/Windows/Fonts") / nombre
        if fuente.exists():
            QFontDatabase.addApplicationFont(str(fuente))
    ventana = VentanaPrincipal()
    try:
        proyecto = proyecto_ejemplo()
        ventana.pagina_ingreso.cargar(proyecto)
        # Usar servicio directamente: un error debe salir, nunca abrir diálogo modal.
        ventana.sesion.actualizar(proyecto)
        ventana.sesion.calcular()
        ventana.controlador.mostrar_resultado()
        ventana.controlador.actualizar_titulo()
        ventana.navegacion.setCurrentRow(2)
        resultado = ventana.sesion.resultado
        profundidad = resultado.puntos[0].profundidad_hs_m
        if not math.isclose(profundidad, 4.736513861635, rel_tol=0, abs_tol=1e-9):
            raise RuntimeError("El ejemplo no coincide con la referencia manual.")
        guardar_proyecto(carpeta / "ejemplo.ll.json", proyecto)
        recuperado = abrir_proyecto(carpeta / "ejemplo.ll.json") == proyecto
        if not recuperado:
            raise RuntimeError("El proyecto no se recuperó íntegramente.")
        interpolado = replace(proyecto, sin_obstaculos=False, luz_libre_m=27.)
        ventana.sesion.actualizar(interpolado)
        resultado_interpolado = ventana.sesion.calcular()
        if (not math.isclose(resultado_interpolado.mu, .974, rel_tol=0, abs_tol=1e-15)
                or not math.isclose(resultado_interpolado.puntos[0].profundidad_hs_m,
                                    4.826485283163771, rel_tol=0, abs_tol=1e-12)):
            raise RuntimeError("La interpolación de luz libre no coincide con la referencia manual.")
        ventana.controlador.mostrar_resultado()
        guardar_proyecto(carpeta / "interpolacion.ll.json", interpolado)
        exportar_word(carpeta / "memoria.docx", resultado_interpolado)
        exportar_pdf(carpeta / "memoria.pdf", resultado_interpolado)
        irregular = replace(
            proyecto, nombre="Comprobación de sección irregular",
            tipo_seccion="irregular", numero_franjas=4,
            puntos_terreno=(PuntoTerreno(0.0, 104.0), PuntoTerreno(10.0, 100.0),
                             PuntoTerreno(20.0, 104.0)),
        )
        ventana.sesion.actualizar(irregular)
        resultado_irregular = ventana.sesion.calcular()
        if (not math.isclose(resultado_irregular.area_m2, 22.5, rel_tol=0, abs_tol=1e-12)
                or not math.isclose(resultado_irregular.ancho_mojado_m, 15.0,
                                    rel_tol=0, abs_tol=1e-12)
                or not math.isclose(resultado_irregular.cierre_caudal_m3s, 0.0,
                                    rel_tol=0, abs_tol=1e-12)):
            raise RuntimeError("La sección irregular no coincide con la referencia verificada.")
        ventana.controlador.mostrar_resultado()
        guardar_proyecto(carpeta / "irregular.ll.json", irregular)
        exportar_word(carpeta / "memoria_irregular.docx", resultado_irregular)
        exportar_pdf(carpeta / "memoria_irregular.pdf", resultado_irregular)
        ventana.show()
        _aplicacion.processEvents()
        if not ventana.grab().save(str(carpeta / "interfaz.png")):
            raise RuntimeError("No se pudo guardar la captura de comprobación.")
        informe = carpeta / "informe.json"
        informe.write_text(json.dumps({
            "hs_m": profundidad,
            "sg_m": resultado.puntos[0].socavacion_m,
            "mu_interpolado": resultado_interpolado.mu,
            "hs_interpolado_m": resultado_interpolado.puntos[0].profundidad_hs_m,
            "area_irregular_m2": resultado_irregular.area_m2,
            "ancho_mojado_irregular_m": resultado_irregular.ancho_mojado_m,
            "cierre_irregular_m3s": resultado_irregular.cierre_caudal_m3s,
            "franjas_irregulares": resultado_irregular.numero_franjas,
            "proyecto_recuperado": recuperado,
            "estado": "correcto",
            "alcance": "Comprobación local; no certifica Windows limpio ni validez para obra.",
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return informe
    finally:
        ventana.sesion.modificado = False
        ventana.close()
        ventana.deleteLater()
        _aplicacion.processEvents()
