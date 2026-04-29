from datetime import datetime

from sqlalchemy.orm import Session

from api.models import Document, Opinion
from ingestion.pdf_reader import read_pdf
from ingestion.tiff_reader import read_tiff
from ml.predictor import SentimentPredictor
from nlp.cleaner import clean_document
from nlp.preprocessor import preprocess
from nlp.segmenter import segment_opinions


def process_document(doc_id: str, db: Session) -> None:
    """
    Flujo completo de análisis de un documento:
    extracción → limpieza → segmentación → preprocesamiento → predicción → persistencia.
    Se ejecuta como BackgroundTask de FastAPI (Celery en Fase 3).
    """
    doc = db.get(Document, doc_id)
    if not doc:
        return

    try:
        doc.status = 'EN_PROCESO'
        db.commit()

        # 1. Extraer texto
        raw_text = read_pdf(doc.file_path) if doc.file_type == 'pdf' else read_tiff(doc.file_path)

        # 2. Limpiar y segmentar
        cleaned = clean_document(raw_text)
        opinion_texts = segment_opinions(cleaned)

        if not opinion_texts:
            raise ValueError(
                "El documento no contiene secciones de opinión para analizar. "
                "Verifica que el PDF incluya secciones con títulos como "
                "'Opinión de Negocio', 'Opinión de Crédito' u otras de opinión."
            )

        # 3. Preprocesar y predecir
        preprocessed = [preprocess(t) for t in opinion_texts]
        predictor = SentimentPredictor.load()
        predictions = predictor.predict_batch(preprocessed)

        # 4. Persistir resultados
        for position, (text, pred) in enumerate(zip(opinion_texts, predictions), start=1):
            opinion = Opinion(
                document_id=doc_id,
                text=text,
                sentiment=pred['sentiment'],
                confidence=pred['confidence'],
                position=position,
            )
            db.add(opinion)

        doc.status = 'COMPLETADO'
        doc.completed_at = datetime.utcnow()

    except Exception as exc:
        doc.status = 'ERROR'
        doc.error_message = str(exc)

    finally:
        db.commit()
