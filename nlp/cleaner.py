import re
from collections import Counter


def clean_document(text: str) -> str:
    """
    Limpieza básica del texto crudo extraído del PDF (documento completo).
    Normaliza saltos de línea, elimina headers/footers repetidos y espacios extra.
    No hace NLP — eso es responsabilidad de preprocessor.py.
    """
    text = remove_headers_footers(text)
    text = re.sub(r'\f', '\n', text)
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[^\S\n]+', ' ', text)
    return text.strip()


def remove_headers_footers(text: str, threshold: int = 3) -> str:
    """
    Elimina líneas que aparecen ≥ threshold veces en el documento,
    ya que probablemente son encabezados o pies de página repetidos.
    """
    lines = text.split('\n')
    counts = Counter(line.strip() for line in lines if line.strip())
    repeated = {line for line, count in counts.items() if count >= threshold}
    return '\n'.join(line for line in lines if line.strip() not in repeated)