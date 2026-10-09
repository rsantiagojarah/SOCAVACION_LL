"""Persistencia real, lectura estricta y recuperación ante fallo de guardado."""
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from socavacion_ll.dominio.modelos import Proyecto, proyecto_ejemplo
from socavacion_ll.infraestructura.proyectos import abrir_proyecto, guardar_proyecto


class PruebasProyectos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name) / "proyecto.ll.json"
        self.proyecto = replace(proyecto_ejemplo(), nombre="Río español ñ", notas="Línea\n2")

    def documento(self):
        datos = asdict(self.proyecto)
        datos["puntos_terreno"] = list(datos["puntos_terreno"])
        return {"formato": "socavacion-ll", "version": 2, "proyecto": datos}

    def escribir(self, documento):
        self.ruta.write_text(json.dumps(documento, ensure_ascii=False), encoding="utf-8")

    def test_ida_y_vuelta_con_todos_los_campos(self):
        guardar_proyecto(self.ruta, self.proyecto)
        self.assertTrue(self.ruta.is_file())
        self.assertEqual(abrir_proyecto(self.ruta), self.proyecto)
        contenido = json.loads(self.ruta.read_text(encoding="utf-8"))
        self.assertEqual(contenido, self.documento())

    def test_borrador_no_calculable_se_puede_guardar(self):
        guardar_proyecto(self.ruta, Proyecto())
        self.assertEqual(abrir_proyecto(self.ruta), Proyecto())

    def test_version_y_formato_desconocidos_se_rechazan(self):
        for campo, valor in (("version", 3), ("version", True), ("formato", "otro")):
            with self.subTest(campo=campo, valor=valor):
                documento = self.documento()
                documento[campo] = valor
                self.escribir(documento)
                with self.assertRaises(ValueError):
                    abrir_proyecto(self.ruta)

    def test_campos_extra_o_faltantes_se_rechazan(self):
        for nivel in ("envoltorio", "proyecto"):
            for operacion in ("agregar", "quitar"):
                with self.subTest(nivel=nivel, operacion=operacion):
                    documento = self.documento()
                    campos = documento if nivel == "envoltorio" else documento["proyecto"]
                    if operacion == "agregar":
                        campos["resultado"] = 4.7
                    else:
                        campos.pop(next(iter(campos)))
                    self.escribir(documento)
                    with self.assertRaises(ValueError):
                        abrir_proyecto(self.ruta)

    def test_json_malformado_o_raiz_invalida_se_rechaza(self):
        for texto in ("{", "[]", "null", '{"version": 1, "version": 1}'):
            with self.subTest(texto=texto):
                self.ruta.write_text(texto, encoding="utf-8")
                with self.assertRaises(ValueError):
                    abrir_proyecto(self.ruta)

    def test_tipos_incorrectos_no_se_convierten(self):
        for campo, valor in (("caudal_m3s", True), ("caudal_m3s", "120"),
                             ("numero_puntos", 11.0), ("no_cohesivo", 1),
                             ("nombre", []), ("caudal_m3s", None)):
            with self.subTest(campo=campo, valor=valor):
                documento = self.documento()
                documento["proyecto"][campo] = valor
                self.escribir(documento)
                with self.assertRaises(ValueError):
                    abrir_proyecto(self.ruta)

    def test_no_finitos_no_entran_ni_salen(self):
        for valor in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(valor=valor):
                documento = self.documento()
                documento["proyecto"]["caudal_m3s"] = valor
                self.escribir(documento)
                with self.assertRaises(ValueError):
                    abrir_proyecto(self.ruta)
                with self.assertRaises(ValueError):
                    guardar_proyecto(self.ruta, replace(self.proyecto, caudal_m3s=valor))

    def test_fallo_reemplazo_conserva_original_y_limpia_temporal(self):
        guardar_proyecto(self.ruta, self.proyecto)
        original = self.ruta.read_bytes()
        with patch("socavacion_ll.infraestructura.proyectos.os.replace", side_effect=OSError("Fallo")):
            with self.assertRaises(OSError):
                guardar_proyecto(self.ruta, replace(self.proyecto, nombre="Cambio"))
        self.assertEqual(self.ruta.read_bytes(), original)
        self.assertEqual(list(self.ruta.parent.iterdir()), [self.ruta])

    def test_archivo_ausente_informa_error(self):
        with self.assertRaises(OSError):
            abrir_proyecto(self.ruta)

    def test_tamano_excesivo_y_anidamiento_abusivo_se_rechazan(self):
        for contenido in (b" " * (1_048_576 + 1), b"[" * 2000 + b"]" * 2000):
            with self.subTest(longitud=len(contenido)):
                self.ruta.write_bytes(contenido)
                with self.assertRaises(ValueError):
                    abrir_proyecto(self.ruta)

    def test_utf8_invalido_se_rechaza(self):
        self.ruta.write_bytes(b"\xff\xfe")
        with self.assertRaises(ValueError):
            abrir_proyecto(self.ruta)

    def test_campo_duplicado_con_documento_por_lo_demas_valido(self):
        texto = json.dumps(self.documento()).replace('"version": 2', '"version": 2, "version": 2')
        self.ruta.write_text(texto, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "repite"):
            abrir_proyecto(self.ruta)


if __name__ == "__main__":
    unittest.main()
