import os

import httpx
from dotenv import load_dotenv

load_dotenv()

_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
_TIMEOUT = 30.0


def upload_document(file_bytes: bytes, filename: str, user_id: str) -> dict:
    with httpx.Client(base_url=_BASE_URL, timeout=_TIMEOUT) as client:
        response = client.post(
            '/api/v1/documents/upload',
            files={'file': (filename, file_bytes, 'application/pdf')},
            params={'user_id': user_id},
        )
        response.raise_for_status()
        return response.json()


def get_status(doc_id: str) -> dict:
    with httpx.Client(base_url=_BASE_URL, timeout=_TIMEOUT) as client:
        response = client.get(f'/api/v1/documents/{doc_id}/status')
        response.raise_for_status()
        return response.json()


def get_results(doc_id: str) -> dict:
    with httpx.Client(base_url=_BASE_URL, timeout=_TIMEOUT) as client:
        response = client.get(f'/api/v1/documents/{doc_id}/results')
        response.raise_for_status()
        return response.json()


def get_history(user_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
    with httpx.Client(base_url=_BASE_URL, timeout=_TIMEOUT) as client:
        response = client.get(
            '/api/v1/documents/',
            params={'user_id': user_id, 'skip': skip, 'limit': limit},
        )
        response.raise_for_status()
        return response.json()
