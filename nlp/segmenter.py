import re

_MIN_LENGTH = 20  # caracteres mínimos para considerar un segmento válido

# Numeración: "1.", "2)", "3-", "Opinión 1:", "Comentario 2:"
_NUMBERED = re.compile(
    r'(?:^|\n)\s*(?:\d+\s*[\.\)\-]|[Oo]pini[oó]n\s+\d+\s*:|[Cc]omentario\s+\d+\s*:)\s*',
    re.MULTILINE,
)

# Bullets: •, -, *, –, →
_BULLETS = re.compile(r'(?:^|\n)\s*[•\*–→]\s+', re.MULTILINE)

# Secciones con letra: "A. Título", "G. Opinión de Negocio", etc.
# Requiere título de al menos 3 chars para evitar falsos positivos
_LETTERED_SECTION = re.compile(
    r'(?:^|\n)([A-Z])\.\s+([A-ZÁÉÍÓÚÑ][^\n]{3,80})\n',
    re.MULTILINE,
)

# Palabras clave que identifican una sección como relevante para el análisis
_OPINION_KEYWORDS = re.compile(
    r'opini[oó]n|comentario|conclusi[oó]n|valoraci[oó]n|evaluaci[oó]n|dictamen',
    re.IGNORECASE,
)


def segment_opinions(text: str) -> list[str]:
    """
    Divide el texto en unidades de opinión detectando el patrón automáticamente.
    Prioridad: secciones con letra → numeración → bullets → párrafos.
    En documentos con secciones A-Z, extrae solo las de contenido de opinión.
    """
    strategy = _detect_pattern(text)

    if strategy == 'lettered_sections':
        segments = _extract_opinion_sections(text)
    elif strategy == 'numbered':
        segments = _split_by(text, _NUMBERED)
    elif strategy == 'bullets':
        segments = _split_by(text, _BULLETS)
    else:
        segments = _split_by_paragraphs(text)

    return [s.strip() for s in segments if len(s.strip()) >= _MIN_LENGTH]


def _detect_pattern(text: str) -> str:
    if len(_LETTERED_SECTION.findall(text)) >= 3:
        return 'lettered_sections'
    if len(_NUMBERED.findall(text)) >= 2:
        return 'numbered'
    if len(_BULLETS.findall(text)) >= 2:
        return 'bullets'
    return 'paragraphs'


def _extract_opinion_sections(text: str) -> list[str]:
    """
    Para documentos con secciones tipo A-Z, extrae el contenido de las secciones
    cuyo título contiene palabras clave de opinión.
    Si no hay secciones de opinión, devuelve todas las secciones.
    """
    matches = list(_LETTERED_SECTION.finditer(text))
    if not matches:
        return [text]

    # Construir lista de (posición_inicio, título, contenido)
    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = m.group(2)
        # El contenido empieza justo después de la línea del título
        content = text[m.end():end].strip()
        sections.append((title, content))

    # Retornar solo secciones de opinión; lista vacía si el doc no las tiene
    return [
        content for title, content in sections
        if _OPINION_KEYWORDS.search(title)
    ]


def _split_by(text: str, pattern: re.Pattern) -> list[str]:
    """
    Divide el texto en los puntos donde el patrón aparece,
    excluyendo el delimitador en sí.
    """
    positions = [m.start() for m in pattern.finditer(text)]
    if not positions:
        return [text]

    segments = []
    for i, start in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        raw = text[start:end]
        # Elimina el propio delimitador del inicio del segmento
        clean = pattern.sub('', raw, count=1)
        segments.append(clean)
    return segments


def _split_by_paragraphs(text: str) -> list[str]:
    return re.split(r'\n{2,}', text)
