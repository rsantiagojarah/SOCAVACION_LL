"""Referencias aritméticas independientes y límites de la primera versión."""
from dataclasses import replace
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from socavacion_ll.calculo.coeficientes import (
    LUCES_M, TABLA_MU, obtener_beta, obtener_z, obtener_mu, seleccionar_mu,
)
from socavacion_ll.calculo.motor import calcular_proyecto
from socavacion_ll.dominio.modelos import Proyecto, proyecto_ejemplo
from socavacion_ll.dominio.validacion import validar_estructura, validar_proyecto


class PruebasCoeficientes(unittest.TestCase):
    def test_mu_fila_mayor_cuatro_contra_original_mtc_p107(self):
        # Relectura visual del PDF original: L25=0.94 y L30=0.95.
        luces = (10, 13, 16, 18, 21, 25, 30, 42, 52, 63, 106, 124, 200)
        valores = (.85, .89, .91, .92, .93, .94, .95, .96, .97, .98, .99, .99, .99)
        for luz, esperado in zip(luces, valores):
            with self.subTest(luz=luz):
                self.assertEqual(obtener_mu(False, 4.1, luz), esperado)

    def test_beta_literal_sin_interpolacion(self):
        for periodo, esperado in ((2, .82), (5, .86), (10, .90), (20, .94),
                                  (50, .97), (100, 1), (500, 1.05), (1000, 1.07)):
            self.assertEqual(obtener_beta(periodo), esperado)
        for periodo in (1, 25, 2000, math.nan, True, 10 ** 1000):
            with self.subTest(periodo=periodo), self.assertRaises(ValueError):
                obtener_beta(periodo)

    def test_z_literal_no_exponente_inverso(self):
        diametros = (.05, .15, .5, 1, 1.5, 2.5, 4, 6, 8, 10, 15, 20,
                     25, 40, 60, 90, 140, 190, 250, 310, 370, 450, 570, 750)
        valores = (.43, .42, .41, .40, .39, .38, .37, .36, .35, .34, .33, .32,
                   .31, .30, .29, .28, .27, .26, .25, .24, .23, .22, .21, .20)
        for diametro, esperado in zip(diametros, valores):
            self.assertEqual(obtener_z(diametro), esperado)
        for diametro in (.01, .64, 1000, math.inf, True):
            with self.subTest(diametro=diametro), self.assertRaises(ValueError):
                obtener_z(diametro)

    def test_mu_celdas_y_condiciones_literales(self):
        self.assertEqual(obtener_mu(True, 2, 0), 1)
        self.assertEqual(obtener_mu(False, 2, 30), .98)
        self.assertEqual(obtener_mu(False, .7, 10), 1)
        # Corregida transcripción previa .945 al releer MTC p.107: celda literal .94.
        self.assertEqual(obtener_mu(False, 4.1, 25), .94)
        self.assertEqual(obtener_mu(False, 1, 13), .97)
        for velocidad, luz in ((4, 25), (3.75, 25), (2.1, 30)):
            with self.subTest(velocidad=velocidad, luz=luz), self.assertRaises(ValueError):
                obtener_mu(False, velocidad, luz)

    def test_mu_interpola_linealmente_solo_luz_libre(self):
        try:
            valor = obtener_mu(False, 2, 27)
        except ValueError:
            valor = "luz bloqueada"
        self.assertEqual(valor, .974)
        seleccion = seleccionar_mu(False, 2, 27)
        for texto in ("25", "0.97", "30", "0.98", "27", "0.974", "usuario", "no publicada"):
            self.assertIn(texto, seleccion.detalle)
        self.assertEqual(obtener_mu(False, 2, 10), .93)
        self.assertEqual(obtener_mu(False, 2, 200), 1.)
        for luz in (9.999, 200.001, math.inf, math.nan, True):
            with self.subTest(luz=luz), self.assertRaises(ValueError):
                obtener_mu(False, 2, luz)

    def test_mu_preserva_todas_las_celdas_publicadas(self):
        for fila, valores in TABLA_MU.items():
            velocidad = .5 if fila == "<1" else 4.1 if fila == ">4" else fila
            for luz, esperado in zip(LUCES_M, valores):
                with self.subTest(fila=fila, luz=luz):
                    self.assertEqual(obtener_mu(False, velocidad, luz), esperado)

    def test_resultado_conserva_detalle_de_interpolacion(self):
        resultado = calcular_proyecto(replace(proyecto_ejemplo(), sin_obstaculos=False,
                                              luz_libre_m=27))
        self.assertAlmostEqual(resultado.mu, .974, places=15)
        self.assertIn("mu = 0.97 +", resultado.detalle_mu)


class PruebasCalculo(unittest.TestCase):
    def test_ejemplo_manual_rectangular(self):
        resultado = calcular_proyecto(proyecto_ejemplo())
        self.assertAlmostEqual(resultado.alpha, .961499713538, places=11)
        self.assertEqual((resultado.beta, resultado.mu, resultado.phi, resultado.z),
                         (1, 1, 1, .4))
        self.assertEqual(resultado.area_m2, 60)
        self.assertEqual(resultado.velocidad_control_m_s, 2)
        self.assertAlmostEqual(resultado.numerador, 6, places=12)
        self.assertEqual(resultado.denominador, .68)
        self.assertAlmostEqual(resultado.exponente, .7142857142857143, places=14)
        self.assertEqual(len(resultado.puntos), 11)
        self.assertEqual(resultado.puntos[0].abscisa_m, 0)
        self.assertEqual(resultado.puntos[-1].abscisa_m, 20)
        for punto in resultado.puntos:
            self.assertAlmostEqual(punto.profundidad_hs_m, 4.736513861635, places=9)
            self.assertAlmostEqual(punto.socavacion_m, 1.736513861635, places=9)
            self.assertAlmostEqual(punto.cota_ll_m, 98.263486138365, places=9)

    def test_equilibrio_velocidad_independiente(self):
        resultado = calcular_proyecto(proyecto_ejemplo())
        profundidad = resultado.puntos[0].profundidad_hs_m
        velocidad_real = 120 / (20 * profundidad)
        velocidad_erosiva = .68 * profundidad ** .4
        self.assertAlmostEqual(velocidad_real, velocidad_erosiva, places=12)

    def test_contraccion_se_aplica_una_sola_vez(self):
        resultado = calcular_proyecto(replace(proyecto_ejemplo(), sin_obstaculos=False,
                                              luz_libre_m=13))
        self.assertEqual(resultado.mu, .94)
        self.assertAlmostEqual(resultado.alpha, .961499713538, places=11)
        self.assertAlmostEqual(resultado.puntos[0].profundidad_hs_m,
                               (6 / (.68 * .94)) ** (1 / 1.4), places=12)

    def test_ejemplo_manual_con_contraccion(self):
        resultado = calcular_proyecto(replace(proyecto_ejemplo(), sin_obstaculos=False,
                                              luz_libre_m=30))
        self.assertEqual(resultado.mu, .98)
        self.assertAlmostEqual(resultado.denominador, .6664, places=12)
        punto = resultado.puntos[0]
        self.assertAlmostEqual(punto.profundidad_hs_m, 4.805359695054269, places=12)
        self.assertAlmostEqual(punto.socavacion_m, 1.805359695054269, places=12)
        self.assertAlmostEqual(punto.cota_ll_m, 98.19464030494573, places=12)

    def test_socavacion_negativa_se_conserva_sin_deposicion(self):
        resultado = calcular_proyecto(replace(proyecto_ejemplo(), caudal_m3s=1,
                                              velocidad_m_s=1 / 60))
        punto = resultado.puntos[0]
        self.assertLess(punto.socavacion_m, 0)
        self.assertGreater(punto.cota_ll_m, punto.cota_fondo_m)
        self.assertEqual(punto.cota_perfil_m, punto.cota_fondo_m)
        self.assertTrue(any("sedimentación" in aviso for aviso in resultado.advertencias))

    def test_velocidad_discrepante_se_advierte_sin_cambiarla(self):
        resultado = calcular_proyecto(replace(proyecto_ejemplo(), velocidad_m_s=3))
        self.assertEqual(resultado.proyecto.velocidad_m_s, 3)
        self.assertTrue(any("Q/A" in aviso for aviso in resultado.advertencias))

    def test_entradas_invalidas_no_producen_resultado(self):
        casos = dict(caudal_m3s=(0, -1, math.nan, True, "120", 10 ** 1000),
                     ancho_m=(0, -1, math.inf), velocidad_m_s=(0, -2),
                     pendiente_m_m=(-.1, math.nan), diametro_medio_mm=(0, .64),
                     periodo_retorno_anios=(25,), cota_agua_m=(100, 99, math.nan),
                     no_cohesivo=(False, 1), agua_clara=(False,),
                     numero_puntos=(1, 202, 2.5, True), nombre=("", 3))
        for campo, valores in casos.items():
            for valor in valores:
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    calcular_proyecto(replace(proyecto_ejemplo(), **{campo: valor}))

    def test_geometria_extrema_rechazada_y_maximo_puntos_valido(self):
        with self.assertRaises(ValueError):
            calcular_proyecto(replace(proyecto_ejemplo(), cota_fondo_m=-1e308,
                                     cota_agua_m=1e308))
        with self.assertRaises(ValueError):
            calcular_proyecto(replace(proyecto_ejemplo(), caudal_m3s=1e308,
                                     ancho_m=1e-308))
        resultado = calcular_proyecto(replace(proyecto_ejemplo(), numero_puntos=201))
        self.assertEqual(len(resultado.puntos), 201)
        self.assertTrue(resultado.fuentes)
        self.assertIsNone(validar_proyecto(proyecto_ejemplo()))

    def test_borrador_es_serializable_sin_ser_calculable(self):
        self.assertIsNone(validar_estructura(Proyecto()))
        with self.assertRaises(ValueError):
            validar_proyecto(Proyecto())

    def test_estructura_rechaza_textos_inseguros_y_tipos_incorrectos(self):
        for cambio in ({"nombre": "a\x00b"}, {"notas": "\ud800"},
                       {"nombre": "a" * 501}, {"notas": "a" * 20001},
                       {"sin_obstaculos": 1}, {"numero_puntos": 2.0},
                       {"cota_fondo_m": float("inf")}, {"ubicacion": None}):
            with self.subTest(cambio=cambio), self.assertRaises(ValueError):
                validar_estructura(replace(proyecto_ejemplo(), **cambio))


if __name__ == "__main__":
    unittest.main()
