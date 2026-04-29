import os
import shutil
import uuid

from dotenv import load_dotenv

load_dotenv()

_STORAGE_PATH = os.getenv("STORAGE_PATH", "./uploads")


def save_document(source_path: str, filename: str, user_id: str) -> str:
    """
    Copia el archivo a STORAGE_PATH/{user_id}/{uuid}_{filename}.
    Retorna la ruta final del archivo guardado.
    """
    user_dir = os.path.join(_STORAGE_PATH, user_id)
    os.makedirs(user_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    dest_path = os.path.join(user_dir, unique_name)
    shutil.copy2(source_path, dest_path)
    return dest_path


def delete_document(file_path: str) -> None:
    """Elimina un documento del almacenamiento local."""
    if os.path.exists(file_path):
        os.remove(file_path)
