"""Perfil transversal de una evaluación ya calculada, sin estado global pyplot."""
from matplotlib.figure import Figure

from socavacion_ll.dominio.modelos import Resultado


def crear_figura(resultado: Resultado, oscuro: bool = False) -> Figure:
    fondo = "#10212b" if oscuro else "white"
    texto = "#e8f3f6" if oscuro else "#263640"
    figura = Figure(figsize=(7.1, 3.5), dpi=120, layout="constrained", facecolor=fondo)
    ejes = figura.add_subplot(111, facecolor=fondo)
    puntos = resultado.puntos
    abscisas = [p.abscisa_m for p in puntos]
    terreno_resultado = [p.cota_fondo_m for p in puntos]
    if resultado.tipo_seccion == "irregular":
        abscisas_terreno = [p.abscisa_m for p in resultado.proyecto.puntos_terreno]
        terreno = [p.cota_m for p in resultado.proyecto.puntos_terreno]
    else:
        abscisas_terreno, terreno = abscisas, terreno_resultado
    agua_resultado = [resultado.proyecto.cota_agua_m] * len(abscisas)
    agua_terreno = [resultado.proyecto.cota_agua_m] * len(abscisas_terreno)
    ejes.fill_between(abscisas, terreno_resultado, agua_resultado,
                      color="#4cb6d4", alpha=0.12)
    ejes.plot(abscisas_terreno, terreno, color="#af8863", linewidth=2,
              label="Terreno natural")
    ejes.plot(abscisas_terreno, agua_terreno, color="#3c9ce8", linewidth=2,
              label="Nivel de agua")
    ejes.plot(abscisas, [p.cota_ll_m for p in puntos], color="#12a594",
              linestyle="--", linewidth=2, label="Perfil LL algebraico")
    if any(p.socavacion_m < 0 for p in puntos):
        ejes.plot(abscisas, [p.cota_perfil_m for p in puntos], color="#dd934a",
                  linestyle=":", linewidth=2.5, label="Perfil de erosión limitado")
    ejes.set_xlabel("Abscisa (m)", color=texto)
    ejes.set_ylabel("Cota (m)", color=texto)
    titulo = ("Sección irregular por franjas" if resultado.tipo_seccion == "irregular"
              else "Sección rectangular homogénea")
    ejes.set_title(titulo, color=texto, fontsize=11)
    ejes.tick_params(colors=texto)
    ejes.ticklabel_format(useOffset=False, style="plain")
    for borde in ejes.spines.values():
        borde.set_color(texto)
        borde.set_alpha(0.3)
    ejes.grid(alpha=0.18, color=texto)
    ejes.margins(x=0.03, y=0.25)
    leyenda = ejes.legend(loc="best", fontsize=8, facecolor=fondo, edgecolor=fondo)
    for rotulo in leyenda.get_texts():
        rotulo.set_color(texto)
    return figura
