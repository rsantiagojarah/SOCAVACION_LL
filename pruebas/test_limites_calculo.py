"""Límites del contrato público; no fabricar coeficientes ni alterar las ecuaciones."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from socavacion_ll.calculo.coeficientes import obtener_mu
from socavacion_ll.calculo.motor import calcular_proyecto
from socavacion_ll.dominio.modelos import proyecto_ejemplo
from socavacion_ll.dominio.validacion import validar_estructura


class PruebasLimitesCalculo(unittest.TestCase):
    def test_tipo_de_proyecto_no_se_convierte_implicitamente(self):
        for invalido in (None, {}, "proyecto", 1):
            with self.subTest(invalido=invalido), self.assertRaisesRegex(ValueError, "Proyecto"):
                validar_estructura(invalido)

    def test_obstaculos_exigen_booleano_y_luz_positiva(self):
        for condicion in (0, 1, None, "sí"):
            with self.subTest(condicion=condicion), self.assertRaisesRegex(ValueError, "obstáculos"):
                obtener_mu(condicion, 2, 30)
        for cambios in ({"luz_libre_m": -1},
                        {"sin_obstaculos": False, "luz_libre_m": 0}):
            with self.subTest(cambios=cambios), self.assertRaisesRegex(ValueError, "luz libre"):
                calcular_proyecto(replace(proyecto_ejemplo(), **cambios))

    def test_desbordamiento_de_potencia_bloquea_salida(self):
        # h=1e200 es finito pero h^(5/3) desborda; no debe devolver nan/inf.
        with self.assertRaisesRegex(ValueError, "intervalo numérico"):
            calcular_proyecto(replace(proyecto_ejemplo(), cota_agua_m=1e200,
                                     cota_fondo_m=0, ancho_m=1))

    def test_dos_puntos_incluyen_los_extremos_del_ancho(self):
        resultado = calcular_proyecto(replace(proyecto_ejemplo(), numero_puntos=2))
        self.assertEqual(tuple(p.abscisa_m for p in resultado.puntos), (0, 20))
        self.assertAlmostEqual(resultado.puntos[1].profundidad_hs_m, 4.736513861635, places=9)


if __name__ == "__main__":
    unittest.main()
