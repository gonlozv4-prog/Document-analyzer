from PIL import Image, ImageSequence
import pytesseract

def read_tiff(file_path: str) -> str:
    try:
        image = Image.open(file_path)
        pages_text = [
            pytesseract.image_to_string(frame.copy(), lang='spa')
            for frame in ImageSequence.Iterator(image)
        ]
        text = '\n'.join(pages_text).strip()
        if not text:
            raise ValueError(f"No se pudo extraer texto del TIFF: {file_path}")
        return text
    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error al leer el TIFF '{file_path}': {e}") from e