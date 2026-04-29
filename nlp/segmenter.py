import re

_MIN_LENGTH = 20  # caracteres mínimos para considerar un segmento válido

# Numeración: "1.", "2)", "3-", "Opinión 1:", "Comentario 2:"
_NUMBERED = re.compile(
    r'(?:^|\n)\s*(?:\d+\s*[\.\)\-]|[Oo]pini[oó]n\s+\d+\s*:|[Cc]omentario\s+\d+\s*:)\s*',
    re.MULTILINE,
)

# Bullets: •, -, *, –, →
_BULLETS = re.compile(r'(?:^|\n)\s*[•\*–→]\s+', re.MULTILINE)


def segment_opinions(text: str) -> list[str]:
    """
    Divide el texto en opiniones individuales detectando automáticamente
    el patrón de separación: numeración, bullets o párrafos.
    """
    strategy = _detect_pattern(text)

    if strategy == 'numbered':
        segments = _split_by(text, _NUMBERED)
    elif strategy == 'bullets':
        segments = _split_by(text, _BULLETS)
    else:
        segments = _split_by_paragraphs(text)

    return [s.strip() for s in segments if len(s.strip()) >= _MIN_LENGTH]


def _detect_pattern(text: str) -> str:
    if len(_NUMBERED.findall(text)) >= 2:
        return 'numbered'
    if len(_BULLETS.findall(text)) >= 2:
        return 'bullets'
    return 'paragraphs'


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
