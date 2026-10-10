"""Pruebas TDD de la ampliación de sección transversal irregular."""
from dataclasses import asdict, replace
import json
import importlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from socavacion_ll.dominio import modelos
from socavacion_ll.dominio.ejemplo_irregular import proyecto_ejemplo_irregular
from socavacion_ll.dominio.modelos import proyecto_ejemplo
from socavacion_ll.dominio.validacion import validar_estructura
from socavacion_ll.infraestructura.proyectos import abrir_proyecto, guardar_proyecto
from socavacion_ll.calculo.motor import calcular_proyecto


class PruebasModeloPersistencia(unittest.TestCase):
    def test_modelo_irregular_inmutable_y_json_v2(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno", None)
        self.assertIsNotNone(PuntoTerreno, "Falta el modelo PuntoTerreno")
        puntos = (PuntoTerreno(0.0, 104.0), PuntoTerreno(10.0, 100.0),
                  PuntoTerreno(20.0, 104.0))
        proyecto = replace(
            proyecto_ejemplo(), tipo_seccion="irregular",
            puntos_terreno=puntos, numero_franjas=24,
        )
        self.assertIsNone(validar_estructura(proyecto))
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "irregular.ll.json"
            guardar_proyecto(ruta, proyecto)
            documento = json.loads(ruta.read_text(encoding="utf-8"))
            self.assertEqual(documento["version"], 2)
            self.assertEqual(documento["proyecto"]["puntos_terreno"][1],
                             {"abscisa_m": 10.0, "cota_m": 100.0})
            self.assertEqual(abrir_proyecto(ruta), proyecto)

    def test_lector_migra_documento_v1_rectangular(self):
        proyecto = proyecto_ejemplo()
        campos_v1 = {
            clave: valor for clave, valor in asdict(proyecto).items()
            if clave not in {"tipo_seccion", "puntos_terreno", "numero_franjas"}
        }
        documento = {"formato": "socavacion-ll", "version": 1, "proyecto": campos_v1}
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "anterior.ll.json"
            ruta.write_text(json.dumps(documento), encoding="utf-8")
            migrado = abrir_proyecto(ruta)
        self.assertEqual(migrado.tipo_seccion, "rectangular")
        self.assertEqual(migrado.puntos_terreno, ())
        self.assertEqual(migrado.numero_franjas, 20)
        self.assertEqual(migrado.caudal_m3s, proyecto.caudal_m3s)

    def test_estructura_rechaza_tipo_puntos_y_resolucion_invalidos(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno", None)
        self.assertIsNotNone(PuntoTerreno, "Falta el modelo PuntoTerreno")
        base = proyecto_ejemplo()
        casos = (
            replace(base, tipo_seccion="trapecio"),
            replace(base, puntos_terreno=[PuntoTerreno(0.0, 1.0)]),
            replace(base, puntos_terreno=(PuntoTerreno(float("nan"), 1.0),)),
            replace(base, numero_franjas=1),
            replace(base, numero_franjas=201),
        )
        for proyecto in casos:
            with self.subTest(proyecto=proyecto), self.assertRaises(ValueError):
                validar_estructura(proyecto)

    def test_enteros_desmesurados_se_rechazan_como_error_de_validacion(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        enorme = 10 ** 1000
        for proyecto in (
            replace(proyecto_ejemplo(), caudal_m3s=enorme),
            replace(proyecto_ejemplo(), puntos_terreno=(PuntoTerreno(enorme, 1.0),)),
        ):
            with self.subTest(proyecto=proyecto), self.assertRaises(ValueError):
                validar_estructura(proyecto)


class PruebasGeometriaIrregular(unittest.TestCase):
    def formar(self, puntos, agua, divisiones):
        try:
            modulo = importlib.import_module("socavacion_ll.calculo.geometria_irregular")
        except ModuleNotFoundError:
            self.fail("Falta el módulo de geometría irregular")
        return modulo.formar_franjas(puntos, agua, divisiones)

    def test_triangulo_produce_areas_trapezoidales_exactas(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        puntos = (PuntoTerreno(0.0, 5.0), PuntoTerreno(5.0, 0.0),
                  PuntoTerreno(10.0, 5.0))
        franjas = self.formar(puntos, agua=4.0, divisiones=2)
        self.assertEqual(len(franjas), 2)
        self.assertEqual([(f.x_inicio_m, f.x_fin_m) for f in franjas], [(1.0, 5.0), (5.0, 9.0)])
        for franja in franjas:
            self.assertAlmostEqual(franja.ancho_m, 4.0, places=12)
            self.assertAlmostEqual(franja.area_m2, 8.0, places=12)
            self.assertAlmostEqual(franja.tirante_m, 2.0, places=12)
            self.assertAlmostEqual(franja.cota_centro_m, 2.0, places=12)

    def test_incorpora_vertices_para_no_integrar_sobre_un_quiebre(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        puntos = (PuntoTerreno(0.0, 5.0), PuntoTerreno(2.0, 1.0),
                  PuntoTerreno(10.0, 5.0))
        franjas = self.formar(puntos, agua=4.0, divisiones=2)
        limites = {franjas[0].x_inicio_m}
        limites.update(f.x_fin_m for f in franjas)
        self.assertIn(2.0, limites)
        self.assertAlmostEqual(sum(f.area_m2 for f in franjas), 11.25, places=12)

    def test_trasladar_abscisas_no_cambia_areas_ni_elimina_limites(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        origen = 10 ** 13
        puntos = (PuntoTerreno(origen, 5.0), PuntoTerreno(origen + 2.0, 1.0),
                  PuntoTerreno(origen + 10.0, 5.0))
        franjas = self.formar(puntos, agua=4.0, divisiones=2)
        self.assertGreaterEqual(len(franjas), 3)
        self.assertAlmostEqual(sum(f.area_m2 for f in franjas), 11.25, places=9)

    def test_no_colapsa_abscisas_finitas_distintas(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        puntos = (PuntoTerreno(0.0, 5.0), PuntoTerreno(1e-13, 0.0),
                  PuntoTerreno(2e-13, 5.0))
        franjas = self.formar(puntos, agua=4.0, divisiones=2)
        self.assertEqual(len(franjas), 2)
        self.assertAlmostEqual(sum(f.area_m2 for f in franjas), 3.2e-13, places=25)

    def test_tramo_vertical_conserva_los_limites_laterales(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        puntos = (PuntoTerreno(0.0, 5.0), PuntoTerreno(5.0, 3.0),
                  PuntoTerreno(5.0, 1.0), PuntoTerreno(10.0, 5.0))
        franjas = self.formar(puntos, agua=4.0, divisiones=2)
        self.assertAlmostEqual(sum(f.area_m2 for f in franjas), 6.875, places=12)

    def test_rechaza_dos_ramas_un_toque_y_ausencia_de_agua(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        perfiles = (
            (PuntoTerreno(0.0, 5.0), PuntoTerreno(2.0, 0.0),
             PuntoTerreno(4.0, 5.0), PuntoTerreno(6.0, 0.0), PuntoTerreno(8.0, 5.0)),
            (PuntoTerreno(0.0, 5.0), PuntoTerreno(2.0, 0.0),
             PuntoTerreno(4.0, 4.0), PuntoTerreno(6.0, 0.0), PuntoTerreno(8.0, 5.0)),
            (PuntoTerreno(0.0, 5.0), PuntoTerreno(10.0, 6.0)),
        )
        for puntos in perfiles:
            with self.subTest(puntos=puntos), self.assertRaises(ValueError):
                self.formar(puntos, agua=4.0, divisiones=4)

    def test_rechaza_estructura_numeros_y_orden_invalidos(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        validos = (PuntoTerreno(0.0, 5.0), PuntoTerreno(10.0, 0.0))
        casos = (
            (list(validos), 4.0, 2),
            (validos, 4.0, True),
            (validos, float("nan"), 2),
            ((PuntoTerreno(0.0, 5.0), object()), 4.0, 2),
            ((PuntoTerreno(0.0, 5.0), PuntoTerreno(10.0, float("inf"))), 4.0, 2),
            ((PuntoTerreno(0.0, 5.0), PuntoTerreno(-1.0, 0.0)), 4.0, 2),
            ((PuntoTerreno(0.0, 5.0), PuntoTerreno(0.0, 5.0)), 4.0, 2),
        )
        for puntos, agua, divisiones in casos:
            with self.subTest(puntos=puntos, agua=agua, divisiones=divisiones), \
                 self.assertRaises(ValueError):
                self.formar(puntos, agua, divisiones)


class PruebasCalculoIrregular(unittest.TestCase):
    def test_ejemplo_manual_independiente_de_dos_franjas(self):
        try:
            geometria = importlib.import_module("socavacion_ll.calculo.geometria_irregular")
            irregular = importlib.import_module("socavacion_ll.calculo.irregular")
        except ModuleNotFoundError:
            self.fail("Falta el núcleo LL para franjas irregulares")
        Franja = geometria.FranjaMojada
        franjas = (
            Franja(0.0, 10.0, 5.0, 10.0, 20.0, 2.0, 8.0),
            Franja(10.0, 20.0, 15.0, 10.0, 40.0, 4.0, 6.0),
        )
        resultado = irregular.evaluar_franjas(
            franjas, caudal_m3s=120.0, diametro_medio_mm=1.0,
            beta=1.0, mu=1.0, z=0.4, cota_agua_m=10.0,
        )
        self.assertAlmostEqual(resultado.suma_reparto, 132.541705030954, places=9)
        self.assertAlmostEqual(resultado.alpha, 0.905375405967315, places=12)
        esperados = (
            (2.8743877437173, 28.743877437173, 2.80006998011794, 0.80006998011794),
            (9.1256122562827, 91.256122562827, 6.39054545023344, 2.39054545023344),
        )
        for punto, esperado in zip(resultado.puntos, esperados):
            self.assertAlmostEqual(punto.caudal_unitario_m2s, esperado[0], places=11)
            self.assertAlmostEqual(punto.caudal_franja_m3s, esperado[1], places=10)
            self.assertAlmostEqual(punto.profundidad_hs_m, esperado[2], places=11)
            self.assertAlmostEqual(punto.socavacion_m, esperado[3], places=11)
        self.assertAlmostEqual(resultado.cierre_caudal_m3s, 0.0, places=12)

    def test_motor_irregular_usa_malla_refinada_y_cierra_caudal(self):
        PuntoTerreno = getattr(modelos, "PuntoTerreno")
        proyecto = replace(
            proyecto_ejemplo(), tipo_seccion="irregular", numero_franjas=4,
            puntos_terreno=(PuntoTerreno(0.0, 104.0), PuntoTerreno(10.0, 100.0),
                             PuntoTerreno(20.0, 104.0)),
        )
        resultado = calcular_proyecto(proyecto)
        self.assertEqual(resultado.tipo_seccion, "irregular")
        self.assertGreaterEqual(resultado.numero_franjas, 8)
        self.assertAlmostEqual(resultado.area_m2, 22.5, places=12)
        self.assertAlmostEqual(resultado.ancho_mojado_m, 15.0, places=12)
        self.assertAlmostEqual(resultado.cierre_caudal_m3s, 0.0, places=12)
        self.assertGreaterEqual(resultado.error_refinamiento_relativo, 0.0)
        self.assertTrue(all(p.ancho_franja_m > 0 and p.caudal_franja_m3s > 0
                            for p in resultado.puntos))

    def test_mu_no_entra_en_alpha_y_se_aplica_una_sola_vez(self):
        geometria = importlib.import_module("socavacion_ll.calculo.geometria_irregular")
        try:
            irregular = importlib.import_module("socavacion_ll.calculo.irregular")
        except ModuleNotFoundError:
            self.fail("Falta el núcleo LL para franjas irregulares")
        franja = geometria.FranjaMojada(0, 10, 5, 10, 20, 2, 8)
        base = irregular.evaluar_franjas((franja,), 20, 1, 1, 1, .4, 10)
        contraido = irregular.evaluar_franjas((franja,), 20, 1, 1, .5, .4, 10)
        self.assertEqual(base.alpha, contraido.alpha)
        esperado = (base.puntos[0].caudal_unitario_m2s / (.68 * .5)) ** (1 / 1.4)
        self.assertAlmostEqual(contraido.puntos[0].profundidad_hs_m, esperado, places=12)

    def test_ejemplo_terreno_variable_una_rama_y_velocidad_coincidente(self):
        proyecto = proyecto_ejemplo_irregular()
        cotas = [punto.cota_m for punto in proyecto.puntos_terreno]
        self.assertGreater(len(cotas), 3)
        self.assertGreater(cotas[0], proyecto.cota_agua_m)
        self.assertGreater(cotas[-1], proyecto.cota_agua_m)
        self.assertTrue(any(
            cotas[indice - 1] < cotas[indice] > cotas[indice + 1]
            for indice in range(1, len(cotas) - 1)
        ))
        resultado = calcular_proyecto(proyecto)
        profundidades = [punto.profundidad_hs_m for punto in resultado.puntos]
        self.assertGreater(max(profundidades) - min(profundidades), 2)
        self.assertAlmostEqual(resultado.velocidad_control_m_s, proyecto.velocidad_m_s, places=9)
        self.assertLess(resultado.error_refinamiento_relativo, 1e-3)
        self.assertFalse(any("difiere de Q/A" in aviso for aviso in resultado.advertencias))

if __name__ == "__main__":
    unittest.main()
