import io
import os

# Debe estar ANTES de cualquier import de api.* para que SQLAlchemy use SQLite in-memory
os.environ.setdefault('DATABASE_URL', 'sqlite://')

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Importar engine DESPUÉS de setear DATABASE_URL
from api.database import Base, engine
from api.main import app


@pytest.fixture(autouse=True)
def setup_db():
    """Crea las tablas antes de cada test y las elimina al terminar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PDF_MAGIC = b'%PDF-1.4\nfake pdf content for testing purposes only'


def _fake_validate(path):
    return {'file_type': 'pdf', 'file_size_bytes': len(PDF_MAGIC), 'page_count': 2}


def _fake_process(doc_id, db):
    """Simula procesamiento sin correr el pipeline NLP/ML real."""
    from datetime import datetime
    from api.models import Document, Opinion
    doc = db.get(Document, doc_id)
    if doc:
        op = Opinion(
            document_id=doc_id,
            text='El servicio fue excelente.',
            sentiment='POSITIVO',
            confidence=0.92,
            position=1,
        )
        db.add(op)
        doc.status = 'COMPLETADO'
        doc.completed_at = datetime.utcnow()
        db.commit()


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


# ---------------------------------------------------------------------------
# POST /api/v1/documents/upload
# ---------------------------------------------------------------------------

class TestUpload:

    def test_upload_valid_pdf(self):
        with (
            patch('api.routes.documents.validate_document', side_effect=_fake_validate),
            patch('api.routes.documents.process_document'),
        ):
            response = client.post(
                '/api/v1/documents/upload',
                files={'file': ('test.pdf', io.BytesIO(PDF_MAGIC), 'application/pdf')},
            )

        assert response.status_code == 202
        data = response.json()
        assert 'id' in data
        assert data['filename'] == 'test.pdf'
        assert data['status'] == 'PENDIENTE'

    def test_upload_invalid_file_returns_422(self):
        with patch('api.routes.documents.validate_document',
                   side_effect=ValueError('Formato no soportado')):
            response = client.post(
                '/api/v1/documents/upload',
                files={'file': ('bad.txt', io.BytesIO(b'not a pdf'), 'text/plain')},
            )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/documents/{id}/status
# ---------------------------------------------------------------------------

class TestStatus:

    def _upload(self):
        with (
            patch('api.routes.documents.validate_document', side_effect=_fake_validate),
            patch('api.routes.documents.process_document'),
        ):
            resp = client.post(
                '/api/v1/documents/upload',
                files={'file': ('doc.pdf', io.BytesIO(PDF_MAGIC), 'application/pdf')},
            )
        return resp.json()['id']

    def test_returns_status_for_known_document(self):
        doc_id = self._upload()
        response = client.get(f'/api/v1/documents/{doc_id}/status')
        assert response.status_code == 200
        assert response.json()['status'] == 'PENDIENTE'

    def test_returns_404_for_unknown_document(self):
        response = client.get('/api/v1/documents/no-existe/status')
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/v1/documents/{id}/results
# ---------------------------------------------------------------------------

class TestResults:

    def _upload_and_process(self):
        with (
            patch('api.routes.documents.validate_document', side_effect=_fake_validate),
            patch('api.routes.documents.process_document', side_effect=_fake_process),
        ):
            resp = client.post(
                '/api/v1/documents/upload',
                files={'file': ('doc.pdf', io.BytesIO(PDF_MAGIC), 'application/pdf')},
            )
        return resp.json()['id']

    def test_returns_results_when_completed(self):
        doc_id = self._upload_and_process()
        response = client.get(f'/api/v1/documents/{doc_id}/results')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'COMPLETADO'
        assert data['summary']['total'] == 1
        assert data['summary']['positive'] == 1
        assert len(data['opinions']) == 1
        assert data['opinions'][0]['sentiment'] == 'POSITIVO'

    def test_returns_409_when_not_completed(self):
        with (
            patch('api.routes.documents.validate_document', side_effect=_fake_validate),
            patch('api.routes.documents.process_document'),
        ):
            resp = client.post(
                '/api/v1/documents/upload',
                files={'file': ('doc.pdf', io.BytesIO(PDF_MAGIC), 'application/pdf')},
            )
        doc_id = resp.json()['id']
        response = client.get(f'/api/v1/documents/{doc_id}/results')
        assert response.status_code == 409


# ---------------------------------------------------------------------------
# GET /api/v1/documents/
# ---------------------------------------------------------------------------

class TestListDocuments:

    def test_returns_empty_list_initially(self):
        response = client.get('/api/v1/documents/')
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_uploaded_documents(self):
        with (
            patch('api.routes.documents.validate_document', side_effect=_fake_validate),
            patch('api.routes.documents.process_document'),
        ):
            client.post(
                '/api/v1/documents/upload',
                files={'file': ('a.pdf', io.BytesIO(PDF_MAGIC), 'application/pdf')},
            )
        response = client.get('/api/v1/documents/')
        assert response.status_code == 200
        assert len(response.json()) == 1
