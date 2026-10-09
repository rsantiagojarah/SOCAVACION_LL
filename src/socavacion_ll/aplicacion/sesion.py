"""Estado de edición y evaluación vigente de un proyecto."""
from socavacion_ll.dominio.modelos import Proyecto
from pathlib import Path

from socavacion_ll.calculo.motor import calcular_proyecto
from socavacion_ll.dominio.validacion import validar_estructura
from socavacion_ll.infraestructura.proyectos import abrir_proyecto, guardar_proyecto


class SesionProyecto:
    def __init__(self, proyecto=None):
        self.nuevo(proyecto)

    def actualizar(self, proyecto):
        """Actualiza los datos e invalida la evaluación anterior."""
        validar_estructura(proyecto)
        if proyecto != self.proyecto:
            self.proyecto = proyecto
            self.resultado = None
            self.modificado = True

    def nuevo(self, proyecto=None):
        """Inicia un borrador; un ejemplo cargado necesita ser guardado."""
        datos = Proyecto() if proyecto is None else proyecto
        validar_estructura(datos)
        self.proyecto = datos
        self.resultado = None
        self.ruta = None
        self.modificado = proyecto is not None

    def abrir(self, ruta):
        """Solo reemplaza la sesión después de leer y validar todo el archivo."""
        proyecto = abrir_proyecto(ruta)
        self.proyecto = proyecto
        self.resultado = None
        self.ruta = Path(ruta)
        self.modificado = False
        return proyecto

    def guardar(self, ruta=None):
        """Confirma ruta y estado únicamente cuando el guardado concluye."""
        destino = Path(ruta) if ruta is not None else self.ruta
        if destino is None:
            raise ValueError("Seleccione una ruta para guardar el proyecto.")
        guardar_proyecto(destino, self.proyecto)
        self.ruta = destino
        self.modificado = False
        return destino

    def calcular(self):
        """Obtiene una única evaluación vigente; un fallo no deja resultados viejos."""
        self.resultado = None
        self.resultado = calcular_proyecto(self.proyecto)
        return self.resultado
