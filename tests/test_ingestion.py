import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from ingestion.models import DocumentMetadata
from ingestion.storage import delete_document, save_document
from ingestion.validator import validate_document

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PDF_MAGIC = b'%PDF-1.4 fake content'
TIFF_MAGIC_LE = b'\x49\x49\x2A\x00fake tiff content'
UNKNOWN_MAGIC = b'\x00\x00\x00\x00unknown'


def _write_temp_file(content: bytes, suffix: str = '.pdf') -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'wb') as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# validator.py
# ---------------------------------------------------------------------------

class TestValidateDocument:

    def test_raises_if_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            validate_document('/ruta/que/no/existe.pdf')

    def test_raises_if_unsupported_format(self):
        path = _write_temp_file(UNKNOWN_MAGIC, suffix='.bin')
        try:
            with pytest.raises(ValueError, match="Formato no soportado"):
                validate_document(path)
        finally:
            os.remove(path)

    def test_raises_if_file_too_large(self, monkeypatch):
        path = _write_temp_file(PDF_MAGIC)
        try:
            # Simular tamaño mayor al límite (default 50 MB)
            monkeypatch.setattr(os.path, 'getsize', lambda _: 60 * 1024 * 1024)
            with pytest.raises(ValueError, match="límite"):
                validate_document(path)
        finally:
            os.remove(path)

    def test_detects_pdf_type(self):
        path = _write_temp_file(PDF_MAGIC)
        try:
            with patch('ingestion.validator._count_pages', return_value=5):
                result = validate_document(path)
            assert result['file_type'] == 'pdf'
            assert result['page_count'] == 5
        finally:
            os.remove(path)

    def test_detects_tiff_type(self):
        path = _write_temp_file(TIFF_MAGIC_LE, suffix='.tiff')
        try:
            with patch('ingestion.validator._count_pages', return_value=3):
                result = validate_document(path)
            assert result['file_type'] == 'tiff'
            assert result['page_count'] == 3
        finally:
            os.remove(path)

    def test_raises_if_too_many_pages(self):
        path = _write_temp_file(PDF_MAGIC)
        try:
            with patch('ingestion.validator._count_pages', return_value=600):
                with pytest.raises(ValueError, match="páginas"):
                    validate_document(path)
        finally:
            os.remove(path)

    def test_returns_file_size(self):
        path = _write_temp_file(PDF_MAGIC)
        try:
            with patch('ingestion.validator._count_pages', return_value=1):
                result = validate_document(path)
            assert result['file_size_bytes'] == os.path.getsize(path)
        finally:
            os.remove(path)


# ---------------------------------------------------------------------------
# storage.py
# ---------------------------------------------------------------------------

class TestStorage:

    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_save_document_creates_file(self, monkeypatch):
        monkeypatch.setenv("STORAGE_PATH", self.tmp_dir)
        # Re-importar para que tome el nuevo env
        import importlib
        import ingestion.storage as storage_mod
        importlib.reload(storage_mod)

        src = _write_temp_file(PDF_MAGIC)
        try:
            dest = storage_mod.save_document(src, 'test.pdf', 'user123')
            assert os.path.exists(dest)
            assert 'user123' in dest
            assert dest.endswith('test.pdf')
        finally:
            os.remove(src)

    def test_save_document_uses_uuid_prefix(self, monkeypatch):
        monkeypatch.setenv("STORAGE_PATH", self.tmp_dir)
        import importlib
        import ingestion.storage as storage_mod
        importlib.reload(storage_mod)

        src = _write_temp_file(PDF_MAGIC)
        try:
            dest1 = storage_mod.save_document(src, 'mismo.pdf', 'user1')
            dest2 = storage_mod.save_document(src, 'mismo.pdf', 'user1')
            assert dest1 != dest2  # UUID diferente cada vez
        finally:
            os.remove(src)

    def test_delete_document_removes_file(self, monkeypatch):
        monkeypatch.setenv("STORAGE_PATH", self.tmp_dir)
        import importlib
        import ingestion.storage as storage_mod
        importlib.reload(storage_mod)

        src = _write_temp_file(PDF_MAGIC)
        dest = storage_mod.save_document(src, 'borrar.pdf', 'user1')
        os.remove(src)

        assert os.path.exists(dest)
        storage_mod.delete_document(dest)
        assert not os.path.exists(dest)

    def test_delete_document_silently_ignores_missing(self, monkeypatch):
        monkeypatch.setenv("STORAGE_PATH", self.tmp_dir)
        import importlib
        import ingestion.storage as storage_mod
        importlib.reload(storage_mod)

        storage_mod.delete_document('/no/existe/archivo.pdf')  # no debe lanzar excepción


# ---------------------------------------------------------------------------
# models.py
# ---------------------------------------------------------------------------

class TestDocumentMetadata:

    def test_default_upload_date_is_set(self):
        meta = DocumentMetadata(
            filename='doc.pdf',
            file_path='/uploads/user1/doc.pdf',
            file_type='pdf',
            file_size_bytes=1024,
            page_count=10,
            user_id='user1',
        )
        assert isinstance(meta.upload_date, datetime)

    def test_fields_are_stored_correctly(self):
        now = datetime(2026, 4, 28, 12, 0, 0)
        meta = DocumentMetadata(
            filename='reporte.pdf',
            file_path='/uploads/u1/reporte.pdf',
            file_type='pdf',
            file_size_bytes=2048,
            page_count=5,
            user_id='u1',
            upload_date=now,
        )
        assert meta.filename == 'reporte.pdf'
        assert meta.file_type == 'pdf'
        assert meta.page_count == 5
        assert meta.upload_date == now
