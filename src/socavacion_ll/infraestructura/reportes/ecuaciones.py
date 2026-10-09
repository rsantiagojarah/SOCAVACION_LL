"""Ecuaciones Word nativas con fracciones, índices y potencias editables."""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _contenedor(etiqueta, *elementos):
    nodo = OxmlElement(etiqueta)
    for elemento in elementos:
        nodo.append(_texto(elemento) if isinstance(elemento, str) else elemento)
    return nodo


def _texto(texto):
    segmento = OxmlElement("m:r")
    propiedades = OxmlElement("w:rPr")
    fuente = OxmlElement("w:rFonts")
    fuente.set(qn("w:ascii"), "Cambria Math")
    fuente.set(qn("w:hAnsi"), "Cambria Math")
    propiedades.append(fuente)
    tamano = OxmlElement("w:sz")
    tamano.set(qn("w:val"), "22")
    propiedades.append(tamano)
    segmento.append(propiedades)
    contenido = OxmlElement("m:t")
    contenido.set(qn("xml:space"), "preserve")
    contenido.text = texto
    segmento.append(contenido)
    return segmento


def _fraccion(numerador, denominador):
    return _contenedor("m:f", _contenedor("m:num", *numerador),
                       _contenedor("m:den", *denominador))


def _potencia(base, exponente):
    return _contenedor("m:sSup", _contenedor("m:e", base),
                       _contenedor("m:sup", exponente))


def _subindice(base, indice):
    return _contenedor("m:sSub", _contenedor("m:e", base),
                       _contenedor("m:sub", indice))


def _corchetes(elemento):
    propiedades = OxmlElement("m:dPr")
    for etiqueta, valor in (("m:begChr", "["), ("m:endChr", "]")):
        delimitador = OxmlElement(etiqueta)
        delimitador.set(qn("m:val"), valor)
        propiedades.append(delimitador)
    return _contenedor("m:d", propiedades, _contenedor("m:e", elemento))


def _formula_alpha():
    potencia = _potencia("h", _fraccion(["5"], ["3"]))
    return (_texto("α = "), _fraccion([_subindice("Q", "d")], ["B · ", potencia]))


def _formula_hs():
    numerador = ["α · ", _potencia("h", _fraccion(["5"], ["3"]))]
    denominador = ["0.68 · β · μ · φ · ", _potencia(_subindice("D", "m"), "0.28")]
    base = _corchetes(_fraccion(numerador, denominador))
    exponente = _fraccion(["1"], ["1 + z"])
    return (_subindice("H", "s"), _texto(" = "), _potencia(base, exponente))


def agregar_ecuacion(documento, texto):
    """Las dos fórmulas centrales usan estructura OMML, no notación ASCII simulada."""
    if texto == "alpha = Q / SUMA":
        elementos = (_texto(texto),)
    elif texto.startswith("alpha ="):
        elementos = _formula_alpha()
    elif texto.startswith("Hs ="):
        elementos = _formula_hs()
    else:
        elementos = (_texto(texto),)
    parrafo = documento.add_paragraph()
    matematicas = _contenedor("m:oMath", *elementos)
    parrafo._p.append(matematicas)
