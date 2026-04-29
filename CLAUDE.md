# CLAUDE.md — Analizador de Sentimiento Banorte

## Stack
- **Frontend:** Streamlit (`app/app.py`) — consume FastAPI via `httpx`
- **Backend:** FastAPI (`api/`) — Uvicorn, puerto 8000
- **NLP:** spaCy `es_core_news_md` + NLTK en español
- **ML:** scikit-learn (línea base TF-IDF+SVM) → Hugging Face BETO (producción)
- **BD:** PostgreSQL 16 vía SQLAlchemy 2.0
- **Async:** Celery + Redis
- **Python:** 3.11+

## Estructura de módulos
- `api/` — FastAPI: rutas, esquemas Pydantic, modelos SQLAlchemy, tareas Celery
- `app/` — Streamlit: páginas, componentes UI
- `ingestion/` — lectura y validación de PDF/TIFF
- `nlp/` — limpieza, segmentación y preprocesamiento de texto
- `ml/` — predictor, trainer, evaluador y model registry
- `docs/` — specifications.md y todo.md
- `tests/` — pruebas unitarias e integración con pytest

## Convenciones
- Formato: Black (88 chars), isort profile=black, Flake8
- Tipado: type hints en todas las funciones públicas
- Errores: lanzar excepciones concretas (`ValueError`, `RuntimeError`, `FileNotFoundError`); no retornar `None` en silencio
- Idioma del código: inglés (nombres de variables, funciones, clases); comentarios y docs en español
- Tests: `tests/test_<módulo>.py`; cobertura mínima 80% en `nlp/` y `ml/`
- Variables de entorno: siempre desde `.env` vía `python-dotenv`; nunca hardcodear credenciales

## Comandos útiles
```bash
# Levantar todo
docker compose up --build

# Solo backend + BD (sin Streamlit)
docker compose up api db redis

# Tests
pytest

# Linting
black . && isort . && flake8 .

# Instalar modelo spaCy español (fuera de Docker)
python -m spacy download es_core_news_md
```

## Variables de entorno
Copiar `.env.example` → `.env` y ajustar valores antes de levantar Docker.
