"""Coordina acciones de escritorio, sesión y representación del resultado."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from socavacion_ll import __version__

from socavacion_ll.dominio.modelos import proyecto_ejemplo
from socavacion_ll.infraestructura.proyectos import abrir_proyecto
from socavacion_ll.infraestructura.reportes import exportar_pdf, exportar_word
from .dialogos import confirmar_cambios, elegir_destino


class ControladorVentana:
    def __init__(self, ventana):
        self.ventana = ventana
        self.sesion = ventana.sesion
        self.ingreso = ventana.pagina_ingreso
        self.ingreso.cambiado.connect(self.datos_editados)

    def datos_editados(self):
        # Invalidar incluso texto incompleto: no depende de poder construir Proyecto.
        self.sesion.resultado = None
        self.sesion.modificado = True
        self.mostrar_resultado()
        self.actualizar_titulo()

    def actualizar_titulo(self):
        nombre = self.ingreso.campos["nombre"].text() or "Nuevo proyecto"
        marca = " *" if self.sesion.modificado else ""
        self.ventana.setWindowTitle(f"{nombre}{marca} · Socavación LL {__version__}")
        self.ventana.titulo_proyecto.setText(nombre + marca)

    def mostrar_resultado(self):
        resultado = self.sesion.resultado
        self.ventana.pagina_nucleo.mostrar(resultado)
        self.ventana.pagina_resultados.mostrar(resultado)
        self.ventana.pagina_reportes.mostrar(resultado)
        for nombre in ("Word", "PDF"):
            self.ventana.acciones[nombre].setEnabled(resultado is not None)

    def _sincronizar(self):
        self.sesion.actualizar(self.ingreso.obtener_proyecto())

    def _mostrar_error(self, titulo, error):
        QMessageBox.warning(self.ventana, titulo, str(error))

    def calcular(self):
        self.sesion.resultado = None
        self.mostrar_resultado()
        try:
            self._sincronizar()
            self.sesion.calcular()
            self.mostrar_resultado()
        except (ValueError, ArithmeticError) as error:
            self._mostrar_error("No se pudo calcular", error)
            return False
        self.actualizar_titulo()
        self.ventana.navegacion.setCurrentRow(2)
        self.ventana.statusBar().showMessage("Cálculo completado · revisa las advertencias y las fuentes.")
        return True

    def guardar(self, como=False):
        try:
            self._sincronizar()
            destino = self.sesion.ruta
            if destino is None or como:
                destino = elegir_destino(
                    self.ventana, "Guardar proyecto", destino or "Proyecto.ll.json", ".ll.json"
                )
                if destino is None:
                    return False
            self.sesion.guardar(destino)
        except (ValueError, OSError) as error:
            self._mostrar_error("No se pudo guardar", error)
            return False
        self.actualizar_titulo()
        self.ventana.statusBar().showMessage(f"Proyecto guardado: {destino}")
        return True

    def abrir(self):
        nombre, _ = QFileDialog.getOpenFileName(
            self.ventana, "Abrir proyecto", "", "Proyectos LL (*.ll.json);;JSON (*.json)"
        )
        if not nombre:
            return False
        try:
            # Validar antes de preguntar por cambios; archivo inválido conserva el trabajo.
            abrir_proyecto(nombre)
        except (ValueError, OSError) as error:
            self._mostrar_error("No se pudo abrir", error)
            return False
        if not confirmar_cambios(self.ventana, self.guardar):
            return False
        try:
            # Guardar pudo modificar el archivo elegido; releer evita cargar una copia vieja.
            self.sesion.abrir(nombre)
        except (ValueError, OSError) as error:
            self._mostrar_error("No se pudo abrir", error)
            return False
        self._cargar_formulario()
        return True

    def nuevo(self):
        if confirmar_cambios(self.ventana, self.guardar):
            self.sesion.nuevo()
            self._cargar_formulario()

    def cargar_ejemplo(self):
        if confirmar_cambios(self.ventana, self.guardar):
            self.sesion.nuevo(proyecto_ejemplo())
            self._cargar_formulario()

    def _cargar_formulario(self):
        self.ingreso.cargar(self.sesion.proyecto)
        self.mostrar_resultado()
        self.actualizar_titulo()
        self.ventana.navegacion.setCurrentRow(0)

    def exportar(self, formato):
        resultado = self.sesion.resultado
        if resultado is None:
            self._mostrar_error("Cálculo requerido", "Calcula con los datos actuales antes de exportar.")
            return False
        extension = ".docx" if formato == "Word" else ".pdf"
        destino = elegir_destino(self.ventana, f"Exportar {formato}", "Memoria_LL" + extension, extension)
        if destino is None:
            return False
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            exportador = exportar_word if formato == "Word" else exportar_pdf
            exportador(destino, resultado)
        except (OSError, ValueError, RuntimeError) as error:
            self._mostrar_error("No se pudo exportar", error)
            return False
        finally:
            QApplication.restoreOverrideCursor()
        self.ventana.statusBar().showMessage(f"Memoria {formato} generada: {destino}")
        return True

    def puede_cerrar(self):
        return confirmar_cambios(self.ventana, self.guardar)
