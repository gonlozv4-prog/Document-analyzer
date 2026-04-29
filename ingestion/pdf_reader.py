import pdfplumber

def read_pdf(file_path: str) -> str:
    try:
        with pdfplumber.open(file_path) as pdf:
            pages_text = [page.extract_text() or '' for page in pdf.pages]
        text = '\n'.join(pages_text).strip()
        if not text:
            raise ValueError(f"No se pudo extraer texto del PDF: {file_path}")
        return text
    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error al leer el PDF '{file_path}': {e}") from e