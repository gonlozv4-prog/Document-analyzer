import fitz  # PyMuPDF
import pdfplumber


def read_pdf(file_path: str) -> str:
    """
    Extrae texto del PDF. Intenta PyMuPDF primero (más rápido);
    si no obtiene texto, usa pdfplumber como fallback.
    """
    if not _file_exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    text = _read_with_pymupdf(file_path)
    if not text:
        text = _read_with_pdfplumber(file_path)
    if not text:
        raise ValueError(f"No se pudo extraer texto del PDF: {file_path}")
    return text


def _read_with_pymupdf(file_path: str) -> str:
    try:
        with fitz.open(file_path) as doc:
            pages_text = [page.get_text() for page in doc]
        return '\n'.join(pages_text).strip()
    except Exception:
        return ''


def _read_with_pdfplumber(file_path: str) -> str:
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_text = [page.extract_text() or '' for page in pdf.pages]
        return '\n'.join(pages_text).strip()
    except Exception:
        return ''


def _file_exists(file_path: str) -> bool:
    import os
    return os.path.exists(file_path)