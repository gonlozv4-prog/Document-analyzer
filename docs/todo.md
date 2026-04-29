# TODO — Analizador de Sentimiento de Opiniones (Banorte)

Estado del proyecto al 27 Abr 2026. Basado en `specifications.md` v1.0.

**Leyenda:** `[ ]` pendiente · `[~]` en progreso / parcial · `[x]` completado

---

## Fase 1 — Fundamentos y MVP (Semanas 1–4)

### Semana 1 · Infraestructura y estructura del proyecto

- [x] Definir estructura de carpetas del proyecto (`ingestion/`, `nlp/`, `ml/`, `api/`, `app/`, `docs/`, `tests/`)
- [x] Crear `docker-compose.yml` con servicios: api, streamlit, db (PostgreSQL 16), redis, celery
- [x] Crear `Dockerfile` para el backend (Python 3.11, incluye tesseract + spaCy español)
- [x] Configurar variables de entorno con `python-dotenv` (`.env.example`)
- [x] Configurar linting y formato: Black, isort, pytest (`pyproject.toml`)
- [ ] Agregar GitHub Actions: CI básico (lint + tests en cada PR)
- [x] Crear `CLAUDE.md` con convenciones del proyecto

### Semana 2 · Módulo de ingesta de PDF (`ingestion/`)

- [x] `ingestion/pdf_reader.py` — extracción de texto con `pdfplumber` + manejo de excepciones
- [x] `ingestion/tiff_reader.py` — OCR con `pytesseract`, soporte multi-página con `ImageSequence`
- [x] Agregar soporte de extracción con `PyMuPDF` como primario, `pdfplumber` como fallback
- [x] `ingestion/validator.py` — validar magic bytes (PDF/TIFF), tamaño (≤ 50 MB) y número de páginas
- [x] `ingestion/storage.py` — almacenamiento local con UUID por archivo, ruta configurable via `.env`
- [x] `ingestion/models.py` — `DocumentMetadata` dataclass (filename, path, tipo, tamaño, páginas, usuario, fecha)
- [x] Tests unitarios para el módulo de ingesta (13/13 passing)

### Semana 3 · Pipeline NLP (`nlp/`)

- [x] `nlp/cleaner.py` — `clean_document()` (limpieza raw, normalización) + `remove_headers_footers()`
- [x] `nlp/segmenter.py` — detección automática de patrón (numeración, bullets, párrafos) + filtro de longitud mínima
- [x] `nlp/preprocessor.py` — `preprocess()` y `preprocess_batch()` con spaCy `es_core_news_md`
- [x] Tests unitarios NLP (19/19 passing, suite completa: 32/32)

### Semana 4 · Modelo línea base y API REST (`ml/` + `api/`)

- [x] `ml/trainer.py` — pipeline TF-IDF + LogisticRegression, `train()` y `build_pipeline()`
- [x] `ml/predictor.py` — `SentimentPredictor` con `predict()` y `predict_batch()`
- [x] `ml/evaluator.py` — métricas: accuracy, F1, precision, recall, ROC-AUC
- [x] `ml/registry.py` + `ml/model_registry/` — almacenamiento versionado con manifest JSON
- [x] `api/main.py` — FastAPI app con lifespan, Swagger en `/docs`
- [x] `api/database.py` — SQLAlchemy 2.0 (SQLite dev / PostgreSQL prod via DATABASE_URL)
- [x] `api/models.py` — ORM: `Document` y `Opinion`
- [x] `api/schemas.py` — Pydantic: upload, status, resultados, resumen
- [x] `POST /api/v1/documents/upload` — valida, guarda, encola BackgroundTask
- [x] `GET  /api/v1/documents/{id}/status` — estado del análisis
- [x] `GET  /api/v1/documents/{id}/results` — opiniones + resumen positivo/negativo
- [x] `GET  /api/v1/documents/` — historial paginado
- [x] `api/tasks.py` — flujo completo: extracción → NLP → ML → persistencia
- [x] Tests ML + API (suite completa: 56/56 passing)

**Entregable Fase 1:** API funcional que recibe un PDF y devuelve clasificaciones de sentimiento.

---

## Fase 2 — Interfaz de Usuario y Mejora del Modelo (Semanas 5–8)

### Semana 5 · Frontend base (`app/`) — Streamlit

> Decisión: Streamlit en lugar de React. El backend FastAPI sigue igual; Streamlit consume la API REST.

- [x] `app/app.py` — login con session_state, `st.navigation` con 3 páginas, cerrar sesión
- [x] `app/api_client.py` — cliente httpx para upload, status, results e historial
- [x] `app/pages/upload.py` — file uploader + polling de estado con `st.rerun()`
- [x] Autenticación básica via env vars `APP_USER` / `APP_PASSWORD`

### Semana 6 · Dashboard, historial y exportación

- [x] `app/pages/results.py` — métricas (`st.metric`), gráfica de pastel + histograma (Altair)
- [x] Tabla de opiniones con colores por sentimiento (Pandas Styler)
- [x] Filtro por sentimiento con `st.selectbox`
- [x] Botón "Exportar CSV" con `st.download_button`
- [x] `app/pages/history.py` — historial paginado, navegación a resultados

### Semana 7 · Fine-tuning del modelo transformer

- [ ] Recopilar / preparar corpus de opiniones financieras en español (etiquetado)
- [ ] Fine-tuning de `dccuchile/bert-base-spanish-wwm-cased` (BETO) con Hugging Face Transformers
- [ ] Alternativa: fine-tuning de `PlanTL-GOB-ES/roberta-base-bne`
- [ ] Evaluar: objetivo F1 ≥ 0.85 en conjunto de validación
- [ ] Guardar modelo fine-tuned en `ml/model_registry/`

### Semana 8 · Integración del modelo transformer

- [ ] Integrar modelo transformer en `ml/predictor.py` (reemplazar o complementar TF-IDF+SVM)
- [ ] Comparar métricas: modelo clásico vs. transformer (accuracy, F1, latencia)
- [ ] Ajustar pipeline NLP para compatibilidad con tokenizador BERT
- [ ] Documentar decisión del modelo a usar en producción

**Entregable Fase 2:** Aplicación web funcional con modelo de alta precisión integrado.

---

## Fase 3 — Funcionalidades Avanzadas y Hardening (Semanas 9–12)

### Semana 9 · Procesamiento asíncrono

- [ ] Configurar Celery con Redis como broker
- [ ] Mover pipeline NLP + ML a tarea Celery (worker separado)
- [ ] Actualizar `POST /api/v1/documents/upload` para encolar tarea y responder de inmediato
- [ ] Polling o WebSocket para notificar al frontend cuando el análisis termina
- [ ] Mecanismo de reintentos automáticos para tareas fallidas en Celery
- [ ] Añadir worker de Celery al `docker-compose.yml`

### Semana 10 · Exportación, autenticación JWT y RBAC

- [ ] `POST /api/v1/auth/login` — autenticación, retorna JWT (expira en 8 horas)
- [ ] Middleware de autenticación JWT en todos los endpoints protegidos
- [ ] Almacenamiento de contraseñas con bcrypt
- [ ] Rate limiting en endpoint de login (prevenir fuerza bruta)
- [ ] RBAC: roles Analista, Gerente, Admin
- [ ] `GET /api/v1/documents/{id}/export?format=csv` — exportar resultados
- [ ] `GET /api/v1/documents/{id}/export?format=pdf` — exportar reporte PDF
- [ ] CSV con columnas: `id_opinion`, `texto`, `sentimiento`, `score_confianza`, `fecha_análisis`
- [ ] Botón "Exportar CSV" con `st.download_button` en la vista de resultados (si no se adelantó en Semana 6)
- [ ] Exportar reporte PDF con resultados (librería `reportlab` o `fpdf2`)

### Semana 11 · OCR, manejo de errores y edge cases

- [ ] Integrar OCR con `pytesseract` como fallback para PDFs escaneados (si no se adelantó en Semana 2)
- [ ] Validación de antivirus / escaneo básico del archivo antes de procesar
- [ ] Manejo robusto de errores en el pipeline: PDF corrupto, sin texto extraíble, demasiadas páginas
- [ ] Mensajes de error claros en la UI para cada caso de fallo
- [ ] Anonimización de datos sensibles en logs y reportes
- [ ] Registrar auditoría: usuario, fecha, IP en cada operación de carga, análisis y exportación
- [ ] Conservar logs de auditoría por mínimo 90 días

### Semana 12 · Pruebas, seguridad y despliegue

- [ ] Pruebas de carga (verificar soporte de ≥ 20 usuarios concurrentes)
- [ ] Cobertura de pruebas unitarias ≥ 80% en módulos `nlp/` y `ml/`
- [ ] Auditoría de seguridad: revisar OWASP Top 10 (inyección, XSS, autenticación, etc.)
- [ ] Configurar HTTPS/TLS 1.2+ (Nginx + certificado)
- [ ] Cifrado de archivos PDF en reposo (AES-256 o bucket policy)
- [ ] Configurar Nginx como proxy inverso para FastAPI (Streamlit corre en su propio puerto)
- [ ] Configurar almacenamiento de archivos en MinIO o AWS S3
- [ ] Migración de base de datos con Alembic (esquemas PostgreSQL finales)
- [ ] Documentación final de la API en `/docs` (Swagger UI generado por FastAPI)
- [ ] Despliegue en entorno de staging → validación → producción
- [ ] `README.md` con instrucciones de instalación, configuración y uso

**Entregable Fase 3:** Sistema en producción con documentación completa.

---

## Deuda técnica / correcciones urgentes

Estos ítems deben resolverse antes de continuar con nuevas funcionalidades:

- [x] **`cleaner.py`**: Cambiar `en_core_web_sm` → `es_core_news_md` (el modelo actual es en inglés)
- [x] **`cleaner.py`**: Corregir `re.sub(r'\s+', '', text)` que eliminaba todos los espacios; usar lematización; preservar chars españoles (á, é, ñ, etc.)
- [x] **`app.py`**: Decisión tomada — Streamlit como frontend definitivo para v1.0, FastAPI como backend
- [x] **`pdf_reader.py`**: Agregar manejo de excepciones (archivo corrupto, sin texto, permisos)
- [x] **`tiff_reader.py`**: Agregar soporte multi-página con `ImageSequence.Iterator` y manejo de excepciones

---

## Backlog / Fuera de alcance v1.0

- [ ] Clasificación multi-clase de emociones (alegría, enojo, tristeza)
- [ ] Análisis en tiempo real de redes sociales
- [ ] Integración directa con CRM de Banorte
- [ ] Soporte para idiomas distintos al español
- [ ] Aplicación móvil nativa
