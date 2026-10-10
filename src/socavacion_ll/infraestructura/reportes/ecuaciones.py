"""Ecuaciones OMML con la misma letra, fracciones e índices que la memoria del acueducto."""
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

FUENTE = "Arial Narrow"
TAMANO = "22"


def es_formula(texto: str) -> bool:
    """Una sustitución numérica entra a ecuación; una frase con dos puntos, no."""
    profundidad = 0
    for caracter in texto:
        if caracter in "([{":
            profundidad += 1
        elif caracter in ")]}":
            profundidad = max(profundidad - 1, 0)
        elif profundidad == 0 and caracter in ";:":
            return False
    return any(simbolo in texto for simbolo in ("=", "≤", "≥", "^"))


def agregar_ecuacion(documento, texto):
    parrafo = documento.add_paragraph(style="Equation")
    parrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    parrafo.paragraph_format.line_spacing = 1.5
    parrafo.paragraph_format.keep_with_next = True
    matematicas = OxmlElement("m:oMath")
    _expresion(matematicas, _normalizar(texto))
    parrafo._p.append(matematicas)


def _normalizar(texto: str) -> str:
    texto = texto.replace("*", " · ").replace(" - ", " − ")
    while "  " in texto:
        texto = texto.replace("  ", " ")
    return texto.strip()


def _expresion(padre, expresion: str) -> None:
    expresion = expresion.strip()
    if not expresion:
        return
    if _grupo(expresion, "(", ")"):
        padre.append(_run("("))
        _expresion(padre, expresion[1:-1])
        padre.append(_run(")"))
        return
    for operadores in (("≤", "≥", "="), ("+", "−")):
        corte = _corte(expresion, operadores)
        if corte is not None:
            izquierda, operador, derecha = corte
            _expresion(padre, izquierda)
            padre.append(_run(f" {operador} "))
            _expresion(padre, derecha)
            return
    corte = _corte(expresion, ("/",))
    if corte is not None:
        numerador, _, denominador = corte
        fraccion = OxmlElement("m:f")
        propiedades = OxmlElement("m:fPr")
        tipo = OxmlElement("m:type")
        tipo.set(qn("m:val"), "bar")
        propiedades.append(tipo)
        fraccion.append(propiedades)
        arriba, abajo = OxmlElement("m:num"), OxmlElement("m:den")
        _expresion(arriba, numerador)
        _expresion(abajo, denominador)
        fraccion.extend((arriba, abajo))
        padre.append(fraccion)
        return
    potencia = _indice(expresion, "^")
    if potencia is not None:
        inicio = _inicio_base(expresion, potencia)
        if inicio > 0:
            _expresion(padre, expresion[:inicio])
        superindice = OxmlElement("m:sSup")
        base, exponente = OxmlElement("m:e"), OxmlElement("m:sup")
        _expresion(base, expresion[inicio:potencia])
        _expresion(exponente, expresion[potencia + 1:])
        superindice.extend((base, exponente))
        padre.append(superindice)
        return
    subindice = _indice(expresion, "_")
    if subindice is not None and subindice > 0:
        resto = expresion[subindice + 1:]
        if resto:
            nodo = OxmlElement("m:sSub")
            base, indice = OxmlElement("m:e"), OxmlElement("m:sub")
            _expresion(base, expresion[:subindice])
            token, sobra = _token(resto)
            _expresion(indice, token)
            nodo.extend((base, indice))
            padre.append(nodo)
            if sobra:
                _expresion(padre, sobra)
            return
    padre.append(_run(expresion))


def _token(texto: str) -> tuple[str, str]:
    texto = texto.strip()
    if texto.startswith("{") and "}" in texto:
        fin = texto.find("}")
        return texto[1:fin], texto[fin + 1:].strip()
    indice = 0
    while indice < len(texto) and texto[indice].isalnum():
        indice += 1
        if indice < len(texto) and texto[0].isdigit() and not texto[indice].isdigit():
            break
        if indice < len(texto) and texto[0].isalpha() and texto[indice] in " ,=+-·":
            break
    if indice == 0:
        return texto[:1], texto[1:]
    return texto[:indice], texto[indice:].strip()


def _corte(expresion: str, operadores: tuple[str, ...]):
    profundidades = {"(": 0, "[": 0, "{": 0}
    cierres = {")": "(", "]": "[", "}": "{"}
    for indice, caracter in enumerate(expresion):
        if caracter in profundidades:
            profundidades[caracter] += 1
            continue
        if caracter in cierres:
            profundidades[cierres[caracter]] = max(profundidades[cierres[caracter]] - 1, 0)
            continue
        if any(profundidades.values()):
            continue
        for operador in operadores:
            if not expresion.startswith(operador, indice):
                continue
            if operador in {"+", "−"} and indice == 0:
                continue
            if operador == "/" and not _es_fraccion(expresion, indice):
                continue
            if operador == "_" and indice == 0:
                continue
            izquierda = expresion[:indice].strip()
            derecha = expresion[indice + len(operador):].strip()
            if izquierda and derecha:
                return izquierda, operador, derecha
    return None


def _es_fraccion(expresion: str, indice: int) -> bool:
    izquierda = expresion[:indice].rstrip()
    derecha = expresion[indice + 1:].lstrip()
    if izquierda.endswith(("³", "²", ")")) and derecha.startswith("s"):
        return False
    if any(izquierda.endswith(unidad) for unidad in ("kgf", "kg", "kN", "m", "s")):
        if derecha.startswith(("ml", "m", "s", "m²", "cm")):
            return False
    return True


def _indice(expresion: str, operador: str) -> int | None:
    corte = _corte(expresion, (operador,))
    if corte is None:
        return None
    return expresion.find(operador, len(corte[0]))


def _grupo(expresion: str, abre: str, cierra: str) -> bool:
    if not (expresion.startswith(abre) and expresion.endswith(cierra)):
        return False
    profundidad = 0
    for indice, caracter in enumerate(expresion):
        if caracter == abre:
            profundidad += 1
        elif caracter == cierra:
            profundidad -= 1
            if profundidad == 0 and indice != len(expresion) - 1:
                return False
    return profundidad == 0


def _inicio_base(expresion: str, potencia: int) -> int:
    fin = potencia - 1
    if fin >= 0 and expresion[fin] in ")]":
        abre = "(" if expresion[fin] == ")" else "["
        profundidad = 0
        for indice in range(fin, -1, -1):
            if expresion[indice] == expresion[fin]:
                profundidad += 1
            elif expresion[indice] == abre:
                profundidad -= 1
                if profundidad == 0:
                    return indice
    indice = fin
    while indice >= 0 and expresion[indice] not in " =+−·;/([":
        indice -= 1
    return indice + 1


def _run(texto: str):
    segmento = OxmlElement("m:r")
    matematicas = OxmlElement("m:rPr")
    estilo = OxmlElement("m:sty")
    estilo.set(qn("m:val"), "p")
    matematicas.append(estilo)
    segmento.append(matematicas)
    propiedades = OxmlElement("w:rPr")
    fuentes = OxmlElement("w:rFonts")
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fuentes.set(qn(atributo), FUENTE)
    tamano = OxmlElement("w:sz")
    tamano.set(qn("w:val"), TAMANO)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "000000")
    propiedades.extend((fuentes, tamano, color))
    segmento.append(propiedades)
    contenido = OxmlElement("m:t")
    contenido.set(qn("xml:space"), "preserve")
    contenido.text = texto
    segmento.append(contenido)
    return segmento
