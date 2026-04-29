import os
import tempfile

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import Document, Opinion
from api.schemas import (
    AnalysisSummary,
    DocumentResults,
    DocumentStatus,
    DocumentUploadResponse,
    OpinionResult,
)
from api.tasks import process_document
from ingestion.validator import validate_document

router = APIRouter(prefix='/api/v1/documents', tags=['documents'])

_STORAGE_PATH = os.getenv('STORAGE_PATH', './uploads')


@router.post('/upload', response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user_id: str = 'anonymous',
    db: Session = Depends(get_db),
):
    # Guardar temporalmente para validar
    suffix = os.path.splitext(file.filename or 'doc')[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        meta = validate_document(tmp_path)
    except (ValueError, FileNotFoundError) as exc:
        os.remove(tmp_path)
        raise HTTPException(status_code=422, detail=str(exc))

    # Mover a almacenamiento definitivo
    user_dir = os.path.join(_STORAGE_PATH, user_id)
    os.makedirs(user_dir, exist_ok=True)
    dest_path = os.path.join(user_dir, f"{os.path.basename(tmp_path)}_{file.filename}")
    os.rename(tmp_path, dest_path)

    doc = Document(
        filename=file.filename,
        file_path=dest_path,
        file_type=meta['file_type'],
        file_size_bytes=meta['file_size_bytes'],
        page_count=meta['page_count'],
        user_id=user_id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(process_document, doc.id, db)

    return DocumentUploadResponse(id=doc.id, filename=doc.filename, status=doc.status)


@router.get('/{doc_id}/status', response_model=DocumentStatus)
def get_status(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Documento no encontrado.')
    return DocumentStatus(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        created_at=doc.created_at,
        completed_at=doc.completed_at,
        error_message=doc.error_message,
    )


@router.get('/{doc_id}/results', response_model=DocumentResults)
def get_results(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Documento no encontrado.')
    if doc.status != 'COMPLETADO':
        raise HTTPException(status_code=409, detail=f'El análisis está en estado: {doc.status}.')

    opinions = (
        db.query(Opinion)
        .filter(Opinion.document_id == doc_id)
        .order_by(Opinion.position)
        .all()
    )

    positive = sum(1 for o in opinions if o.sentiment == 'POSITIVO')
    total = len(opinions)

    return DocumentResults(
        id=doc.id,
        filename=doc.filename,
        status=doc.status,
        summary=AnalysisSummary(
            total=total,
            positive=positive,
            negative=total - positive,
            positive_pct=round(positive / total * 100, 1) if total else 0.0,
            negative_pct=round((total - positive) / total * 100, 1) if total else 0.0,
        ),
        opinions=[
            OpinionResult(
                id=o.id,
                text=o.text,
                sentiment=o.sentiment,
                confidence=o.confidence,
                position=o.position,
            )
            for o in opinions
        ],
    )


@router.get('/', response_model=list[DocumentStatus])
def list_documents(
    user_id: str = 'anonymous',
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    docs = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        DocumentStatus(
            id=d.id,
            filename=d.filename,
            status=d.status,
            created_at=d.created_at,
            completed_at=d.completed_at,
        )
        for d in docs
    ]
