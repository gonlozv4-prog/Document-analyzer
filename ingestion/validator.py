import os

from dotenv import load_dotenv

load_dotenv()

_MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
_MAX_PAGES = int(os.getenv("MAX_PAGES", 500))

_PDF_MAGIC = b'%PDF'
_TIFF_MAGIC_LE = b'\x49\x49\x2A\x00'
_TIFF_MAGIC_BE = b'\x4D\x4D\x00\x2A'


def validate_document(file_path: str) -> dict:
    """
    Valida formato (magic bytes), tamaño y número de páginas.
    Retorna dict con file_type, file_size_bytes y page_count.
    Lanza ValueError si alguna validación falla, FileNotFoundError si no existe.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > _MAX_FILE_SIZE_MB:
        raise ValueError(
            f"El archivo supera el límite de {_MAX_FILE_SIZE_MB} MB "
            f"(tamaño actual: {size_mb:.1f} MB)."
        )

    file_type = _detect_type(file_path)

    page_count = _count_pages(file_path, file_type)
    if page_count > _MAX_PAGES:
        raise ValueError(
            f"El documento tiene {page_count} páginas; "
            f"el máximo permitido es {_MAX_PAGES}."
        )

    return {
        "file_type": file_type,
        "file_size_bytes": size_bytes,
        "page_count": page_count,
    }


def _detect_type(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        header = f.read(8)

    if header[:4] == _PDF_MAGIC:
        return 'pdf'
    if header[:4] in (_TIFF_MAGIC_LE, _TIFF_MAGIC_BE):
        return 'tiff'
    raise ValueError(
        "Formato no soportado. Solo se aceptan archivos PDF y TIFF."
    )


def _count_pages(file_path: str, file_type: str) -> int:
    if file_type == 'pdf':
        import fitz
        with fitz.open(file_path) as doc:
            return len(doc)

    from PIL import Image, ImageSequence
    with Image.open(file_path) as img:
        return sum(1 for _ in ImageSequence.Iterator(img))
