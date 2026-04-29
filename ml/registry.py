import json
import os
from datetime import datetime

import joblib

_REGISTRY_DIR = os.path.join(os.path.dirname(__file__), 'model_registry')
_MANIFEST_PATH = os.path.join(_REGISTRY_DIR, 'manifest.json')


def save_model(pipeline, version: str | None = None) -> str:
    """
    Guarda el pipeline en model_registry/{version}.joblib y actualiza el manifest.
    Retorna la ruta del archivo guardado.
    """
    os.makedirs(_REGISTRY_DIR, exist_ok=True)

    if version is None:
        manifest = _load_manifest()
        version = f"v{len(manifest['versions']) + 1}"

    model_path = os.path.join(_REGISTRY_DIR, f"{version}.joblib")
    joblib.dump(pipeline, model_path)

    manifest = _load_manifest()
    manifest['versions'].append({
        'version': version,
        'path': model_path,
        'created_at': datetime.utcnow().isoformat(),
    })
    manifest['latest'] = version

    with open(_MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

    return model_path


def load_model(version: str = 'latest'):
    """
    Carga un pipeline del registry. version='latest' carga el más reciente.
    Lanza RuntimeError si no hay modelos entrenados.
    """
    manifest = _load_manifest()
    if not manifest['versions']:
        raise RuntimeError(
            "No hay modelos entrenados en el registry. "
            "Ejecuta ml/trainer.py para entrenar el modelo primero."
        )

    target = manifest['latest'] if version == 'latest' else version
    model_path = os.path.join(_REGISTRY_DIR, f"{target}.joblib")

    if not os.path.exists(model_path):
        raise RuntimeError(f"Modelo '{target}' no encontrado en {_REGISTRY_DIR}.")

    return joblib.load(model_path)


def list_versions() -> list[dict]:
    return _load_manifest()['versions']


def _load_manifest() -> dict:
    if os.path.exists(_MANIFEST_PATH):
        with open(_MANIFEST_PATH) as f:
            return json.load(f)
    return {'versions': [], 'latest': None}
