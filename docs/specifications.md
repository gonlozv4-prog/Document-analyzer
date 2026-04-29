# Especificaciones Técnicas del Proyecto
## Sistema de Análisis de Sentimiento de Opiniones de Clientes — Banorte

**Versión:** 1.0  
**Fecha:** Abril 2026  
**Autor:** Rogelio Ortiz — rortiz@altimetrik.com  
**Estado:** Borrador

---

## Tabla de Contenidos

1. [Descripción General](#1-descripción-general)
2. [Objetivos](#2-objetivos)
3. [Alcance](#3-alcance)
4. [Arquitectura del Sistema](#4-arquitectura-del-sistema)
5. [Stack Tecnológico](#5-stack-tecnológico)
6. [Flujos de Proceso](#6-flujos-de-proceso)
7. [Módulos del Sistema](#7-módulos-del-sistema)
8. [Historias de Usuario](#8-historias-de-usuario)
9. [Requisitos No Funcionales](#9-requisitos-no-funcionales)
10. [Plan de Fases y Roadmap](#10-plan-de-fases-y-roadmap)
11. [Consideraciones de Seguridad](#11-consideraciones-de-seguridad)
12. [Riesgos y Mitigaciones](#12-riesgos-y-mitigaciones)
13. [Glosario](#13-glosario)

---

## 1. Descripción General

El proyecto consiste en el desarrollo de una **aplicación web de análisis de sentimiento** orientada al procesamiento de documentos PDF que contienen opiniones y comentarios de clientes de **Banorte**. La plataforma permitirá a los usuarios del negocio cargar archivos PDF, extraer automáticamente el texto de las opiniones, aplicar modelos de Machine Learning para clasificar el sentimiento (positivo o negativo) y visualizar los resultados de manera clara e interactiva.

La solución combina técnicas de procesamiento de lenguaje natural (NLP), modelos de clasificación entrenados en español financiero, y una interfaz web moderna que facilita la toma de decisiones estratégicas basadas en datos.

---

## 2. Objetivos

### 2.1 Objetivo General

Desarrollar una aplicación web que automatice el análisis de sentimiento de opiniones de clientes de Banorte a partir de documentos PDF, clasificando cada opinión como positiva o negativa mediante modelos de Machine Learning.

### 2.2 Objetivos Específicos

- Implementar un módulo robusto de ingesta y extracción de texto a partir de archivos PDF.
- Desarrollar un pipeline de preprocesamiento y limpieza de texto en español adaptado al contexto financiero.
- Identificar y segmentar automáticamente las secciones del documento que contienen opiniones de clientes.
- Entrenar y/o adaptar modelos de clasificación de sentimiento con alto grado de precisión.
- Proveer una interfaz de usuario (UI) intuitiva para la carga de documentos, visualización de resultados y seguimiento histórico de análisis.
- Exponer una API REST que permita la integración futura con otros sistemas internos de Banorte.
- Generar reportes exportables con los resultados del análisis.

---

## 3. Alcance

### 3.1 Dentro del Alcance

- Carga de archivos PDF con opiniones de clientes.
- Extracción, limpieza y segmentación de texto de los documentos.
- Clasificación binaria de sentimiento: **Positivo** / **Negativo**.
- Visualización de resultados por opinión y resumen agregado (dashboard).
- Historial de análisis por sesión y por usuario.
- Exportación de resultados en formatos CSV y PDF.
- API REST para consumo externo.
- Autenticación básica de usuarios.

### 3.2 Fuera del Alcance (v1.0)

- Clasificación multi-clase de emociones (alegría, enojo, tristeza, etc.).
- Análisis en tiempo real de redes sociales o canales externos.
- Integración directa con sistemas CRM de Banorte.
- Soporte para idiomas distintos al español.
- Aplicación móvil nativa.

---

## 4. Arquitectura del Sistema

La aplicación sigue una arquitectura de **tres capas** (Three-Tier Architecture) con separación clara entre presentación, lógica de negocio y datos.

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND (UI)                       │
│                  Streamlit (Python)                      │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / REST API
┌────────────────────────▼────────────────────────────────┐
│                   BACKEND / API REST                     │
│              FastAPI (Python 3.11+)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Módulo de Ingesta  │  Módulo NLP  │  Módulo ML  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
┌─────────▼──────┐ ┌─────▼──────┐ ┌───▼──────────────┐
│  Base de Datos │ │  Almacen.  │ │  Modelo ML       │
│  PostgreSQL    │ │  Archivos  │ │  (scikit-learn / │
│                │ │  (S3/Local)│ │   transformers)  │
└────────────────┘ └────────────┘ └──────────────────┘
```

### 4.1 Componentes Principales

| Componente | Responsabilidad |
|---|---|
| **Frontend (Streamlit)** | Interfaz de usuario, carga de archivos, visualización de resultados |
| **API REST (FastAPI)** | Orquestación de peticiones, autenticación, gestión de flujos |
| **Módulo de Ingesta** | Extracción de texto desde PDF, detección de secciones |
| **Módulo NLP** | Limpieza, tokenización, normalización del texto |
| **Módulo ML** | Clasificación de sentimiento positivo/negativo |
| **Base de Datos** | Persistencia de usuarios, análisis e historial |
| **Almacenamiento** | Archivos PDF cargados por usuarios |

---

## 5. Stack Tecnológico

### 5.1 Backend

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje principal del backend |
| FastAPI | 0.111+ | Framework web y API REST |
| Uvicorn | 0.29+ | Servidor ASGI de producción |
| PyMuPDF (fitz) | 1.24+ | Extracción de texto desde PDF |
| pdfplumber | 0.11+ | Extracción avanzada de tablas y texto PDF |
| spaCy | 3.7+ | Pipeline NLP: tokenización, lematización, entidades |
| NLTK | 3.8+ | Stopwords, utilidades de texto en español |
| scikit-learn | 1.4+ | Modelos de ML: Logistic Regression, SVM, Random Forest |
| Hugging Face Transformers | 4.40+ | Modelos BERT/RoBERTa en español para fine-tuning |
| Pandas | 2.2+ | Manipulación y análisis de datos |
| NumPy | 1.26+ | Operaciones numéricas |
| SQLAlchemy | 2.0+ | ORM para base de datos |
| Alembic | 1.13+ | Migraciones de base de datos |
| Pydantic | 2.7+ | Validación de datos y esquemas |
| Celery | 5.3+ | Procesamiento asíncrono de tareas largas |
| Redis | 7.2+ | Broker de mensajes para Celery |
| PyJWT | 2.8+ | Autenticación JWT |
| python-dotenv | 1.0+ | Gestión de variables de entorno |

### 5.2 Frontend

> **Decisión de arquitectura (Abr 2026):** Se optó por Streamlit en lugar de React + TypeScript para acelerar el desarrollo. El equipo es Python-first, la audiencia es interna, y Streamlit cubre todos los requisitos de UI del v1.0. FastAPI sigue siendo el backend, por lo que la API REST para integraciones futuras se mantiene intacta.

| Tecnología | Versión | Uso |
|---|---|---|
| Streamlit | 1.35+ | Framework de interfaz web en Python |
| Plotly / Altair | — | Gráficas interactivas (pastel, histograma) |
| streamlit-authenticator | 0.3+ | Autenticación básica de usuarios en Streamlit |
| Pandas | 2.2+ | Renderizado de tablas y exportación CSV |

### 5.3 Base de Datos y Almacenamiento

| Tecnología | Uso |
|---|---|
| PostgreSQL 16 | Base de datos relacional principal |
| Redis 7 | Caché y cola de tareas |
| MinIO / AWS S3 | Almacenamiento de archivos PDF |

### 5.4 DevOps e Infraestructura

| Tecnología | Uso |
|---|---|
| Docker + Docker Compose | Contenerización del proyecto |
| GitHub Actions | CI/CD pipelines |
| Nginx | Proxy inverso y servicio del frontend |
| Pytest | Testing unitario e integración |
| Black / Flake8 / isort | Calidad y estilo del código Python |

### 5.5 Modelo de Machine Learning

El sistema soportará dos enfoques complementarios:

1. **Modelo Clásico (línea base):** Vectorización TF-IDF + clasificador SVM / Logistic Regression. Rápido, interpretable, sin GPU requerida.
2. **Modelo Transformer (producción):** Fine-tuning de `dccuchile/bert-base-spanish-wwm-cased` (BETO) o `PlanTL-GOB-ES/roberta-base-bne` sobre un corpus de reseñas financieras en español.

---

## 6. Flujos de Proceso

### 6.1 Flujo Principal: Carga y Análisis de PDF

```
Usuario
  │
  ├─[1]─► Accede a la plataforma web y se autentica
  │
  ├─[2]─► Carga archivo PDF desde la UI
  │
  ├─[3]─► Frontend envía el archivo a la API REST (/upload)
  │
  └─[4]─► API valida el archivo (tamaño, tipo, formato)
             │
             ├──[OK]──► Guarda PDF en almacenamiento (S3/MinIO)
             │           Registra el análisis en BD (estado: PENDIENTE)
             │           Encola tarea en Celery
             │
             └──[ERROR]─► Retorna error al usuario (formato inválido, etc.)

Celery Worker
  │
  ├─[5]─► Extrae texto del PDF (PyMuPDF / pdfplumber)
  │
  ├─[6]─► Segmenta el documento (identifica secciones de opiniones)
  │
  ├─[7]─► Limpia y normaliza el texto (NLP pipeline)
  │        │ - Elimina caracteres especiales y ruido
  │        │ - Normalización de acentos y mayúsculas
  │        │ - Eliminación de stopwords
  │        └── Tokenización y lematización (spaCy)
  │
  ├─[8]─► Aplica modelo de sentimiento a cada opinión
  │        │ - Genera etiqueta: POSITIVO / NEGATIVO
  │        └── Genera score de confianza (0.0 – 1.0)
  │
  ├─[9]─► Guarda resultados en BD (estado: COMPLETADO)
  │
  └─[10]─► Notifica al frontend (WebSocket / polling)

Usuario
  │
  └─[11]─► Visualiza resultados en el dashboard
             ├── Lista de opiniones con clasificación
             ├── Gráfica de distribución positivo/negativo
             ├── Score de confianza por opinión
             └── Opción de exportar (CSV / PDF)
```

### 6.2 Flujo de Preprocesamiento de Texto

```
Texto Crudo (del PDF)
       │
       ▼
[Limpieza básica]
  - Eliminar saltos de página, headers/footers repetidos
  - Normalizar espacios y saltos de línea
       │
       ▼
[Segmentación de opiniones]
  - Identificar patrones (numeración, bullets, separadores)
  - Separar cada opinión como unidad de análisis
       │
       ▼
[Normalización NLP]
  - Convertir a minúsculas
  - Eliminar caracteres especiales (excepto puntuación relevante)
  - Normalizar acentos (opcional, dependiendo del modelo)
  - Eliminar stopwords en español
       │
       ▼
[Tokenización y lematización] (spaCy es_core_news_md)
       │
       ▼
[Vectorización]
  - TF-IDF (modelo clásico)  O  Tokenizador BERT (modelo transformer)
       │
       ▼
[Clasificador de Sentimiento]
       │
       ▼
Etiqueta: POSITIVO / NEGATIVO + Score de Confianza
```

---

## 7. Módulos del Sistema

### 7.1 Módulo de Ingesta (`ingestion/`)

Responsable de recibir, validar y almacenar los archivos PDF.

- Validación de formato, tamaño máximo (configurable, default: 50 MB) y páginas máximas.
- Extracción de texto con soporte para PDFs nativos y escaneados (OCR con Tesseract como fallback).
- Metadatos del documento: nombre, fecha de carga, páginas, usuario.

### 7.2 Módulo NLP (`nlp/`)

Pipeline de procesamiento de texto.

- `text_cleaner.py`: Limpieza y normalización.
- `segmenter.py`: Detección y separación de opiniones dentro del documento.
- `preprocessor.py`: Tokenización, lematización, eliminación de stopwords.

### 7.3 Módulo ML (`ml/`)

Gestión del ciclo de vida del modelo.

- `predictor.py`: Carga del modelo y predicción de sentimiento.
- `trainer.py`: Script de entrenamiento/fine-tuning del modelo.
- `evaluator.py`: Métricas de evaluación (accuracy, F1, precision, recall, ROC-AUC).
- `model_registry/`: Almacenamiento versionado de modelos.

### 7.4 Módulo API (`api/`)

Endpoints REST expuestos al frontend y sistemas externos.

- `POST /api/v1/auth/login` — Autenticación de usuario.
- `POST /api/v1/documents/upload` — Carga de PDF.
- `GET  /api/v1/documents/{id}/status` — Estado del análisis.
- `GET  /api/v1/documents/{id}/results` — Resultados del análisis.
- `GET  /api/v1/documents/` — Historial de análisis del usuario.
- `GET  /api/v1/documents/{id}/export?format=csv|pdf` — Exportar resultados.

### 7.5 Módulo Frontend (`app/`)

Interfaz de usuario construida con Streamlit. Consume la API REST de FastAPI.

- **Login:** Autenticación vía `streamlit-authenticator` (correo + contraseña).
- **Dashboard principal:** Métricas agregadas y resumen de análisis recientes.
- **Carga de documentos:** `st.file_uploader` + barra de progreso (`st.progress`).
- **Vista de resultados:** `st.dataframe` con colores por sentimiento (verde/rojo) y score de confianza.
- **Gráficos:** Gráfica de pastel e histograma de confianza con Plotly/Altair.
- **Historial:** Lista paginada de análisis previos con acceso al detalle.
- **Exportar CSV:** `st.download_button` con el DataFrame de resultados.

---

## 8. Historias de Usuario

### Épica 1: Gestión de Documentos

**HU-01 — Cargar un PDF para análisis**
> **Como** analista de negocio,  
> **quiero** poder cargar un archivo PDF con opiniones de clientes,  
> **para** que el sistema procese automáticamente su contenido y me entregue los resultados de sentimiento.

*Criterios de aceptación:*
- El sistema acepta archivos `.pdf` de hasta 50 MB.
- Se muestra una barra de progreso durante la carga.
- Si el archivo no es un PDF válido, se muestra un mensaje de error claro.
- Una vez cargado, el usuario ve el estado del análisis en tiempo real.

---

**HU-02 — Ver historial de análisis**
> **Como** usuario de la plataforma,  
> **quiero** ver un historial de todos los documentos que he analizado previamente,  
> **para** poder acceder a resultados anteriores sin necesidad de recargar el archivo.

*Criterios de aceptación:*
- El historial muestra nombre del archivo, fecha de análisis y estado.
- Se puede acceder al detalle de cualquier análisis pasado.
- El historial es paginado si supera 20 registros.

---

### Épica 2: Análisis de Sentimiento

**HU-03 — Ver resultados de sentimiento por opinión**
> **Como** analista de negocio,  
> **quiero** ver cada opinión extraída del PDF con su clasificación (Positivo/Negativo) y nivel de confianza,  
> **para** poder revisar individualmente los resultados y detectar patrones.

*Criterios de aceptación:*
- Cada opinión se muestra en una tarjeta o fila con su texto, etiqueta y score.
- Las opiniones positivas se destacan en verde y las negativas en rojo.
- El score de confianza se muestra como porcentaje (ej. 92%).
- Se puede filtrar por tipo de sentimiento (Positivo / Negativo / Todos).

---

**HU-04 — Ver resumen visual del análisis**
> **Como** gerente de área,  
> **quiero** ver un resumen visual con gráficas de distribución de sentimientos,  
> **para** tener una visión rápida del estado general de la percepción de los clientes.

*Criterios de aceptación:*
- Se muestra una gráfica de pastel con el porcentaje de opiniones positivas vs. negativas.
- Se muestra el total de opiniones analizadas.
- Las gráficas se actualizan automáticamente cuando termina el procesamiento.

---

### Épica 3: Exportación e Integración

**HU-05 — Exportar resultados a CSV**
> **Como** analista de datos,  
> **quiero** exportar los resultados del análisis en formato CSV,  
> **para** poder realizar análisis adicionales en Excel o herramientas de BI.

*Criterios de aceptación:*
- El CSV incluye columnas: `id_opinion`, `texto`, `sentimiento`, `score_confianza`, `fecha_análisis`.
- La exportación está disponible desde la vista de resultados.
- El archivo se descarga automáticamente al hacer clic en el botón "Exportar CSV".

---

**HU-06 — Consumir resultados vía API**
> **Como** desarrollador de sistemas internos de Banorte,  
> **quiero** consumir los resultados de análisis a través de una API REST,  
> **para** integrar los insights de sentimiento con otros sistemas del banco.

*Criterios de aceptación:*
- La API responde en formato JSON con autenticación JWT.
- La documentación de la API está disponible en `/docs` (Swagger UI).
- Los endpoints están versionados (`/api/v1/`).

---

### Épica 4: Administración y Seguridad

**HU-07 — Autenticarme de forma segura**
> **Como** usuario de la plataforma,  
> **quiero** poder iniciar sesión con mis credenciales corporativas,  
> **para** que solo personal autorizado acceda a los datos de los clientes.

*Criterios de aceptación:*
- El login requiere correo y contraseña.
- Las contraseñas se almacenan con hash bcrypt.
- Los tokens JWT expiran en 8 horas.
- Intentos fallidos consecutivos bloquean temporalmente la cuenta.

---

## 9. Requisitos No Funcionales

### 9.1 Rendimiento

- El tiempo de respuesta para la carga de un archivo PDF debe ser menor a **2 segundos** para archivos de hasta 10 MB.
- El procesamiento completo de un documento de 50 páginas debe completarse en menos de **60 segundos**.
- El sistema debe soportar al menos **20 usuarios concurrentes** en v1.0.

### 9.2 Disponibilidad

- La aplicación debe tener una disponibilidad del **99.5%** en horario laboral (L–V, 8:00–20:00 h).
- Debe contar con mecanismos de reintentos automáticos para tareas fallidas en Celery.

### 9.3 Seguridad

- Toda comunicación debe realizarse por **HTTPS/TLS 1.2+**.
- Los archivos PDF se almacenan cifrados en reposo (AES-256).
- Se implementa control de acceso basado en roles (RBAC): Analista, Gerente, Admin.
- Los logs de acceso y auditoría deben conservarse por mínimo 90 días.
- No se almacena información sensible de clientes más allá de lo necesario para el análisis.

### 9.4 Escalabilidad

- La arquitectura debe permitir escalar horizontalmente los workers de Celery según demanda.
- El modelo ML debe poder actualizarse sin interrumpir el servicio (modelo versioning).

### 9.5 Mantenibilidad

- Cobertura de pruebas unitarias mínima del **80%** en módulos NLP y ML.
- El código debe seguir PEP 8 y estar documentado con docstrings.
- Todos los servicios deben estar contenerizados con Docker.

---

## 10. Plan de Fases y Roadmap

### Fase 1 — Fundamentos y MVP (Semanas 1–4)

**Objetivo:** Tener un sistema funcional de extremo a extremo con el flujo básico.

| Semana | Actividades |
|---|---|
| 1 | Configuración del repositorio, Docker Compose, estructura del proyecto, CI básico |
| 2 | Módulo de ingesta: carga de PDF, extracción de texto con PyMuPDF/pdfplumber |
| 3 | Pipeline NLP: limpieza, segmentación de opiniones, tokenización |
| 4 | Modelo línea base (TF-IDF + SVM), API REST endpoints básicos, pruebas |

**Entregable:** API funcional que recibe un PDF y devuelve clasificaciones de sentimiento.

---

### Fase 2 — Interfaz de Usuario y Mejora del Modelo (Semanas 5–8)

**Objetivo:** Interfaz web usable y modelo mejorado con transformers.

| Semana | Actividades |
|---|---|
| 5 | Frontend: login, carga de archivos, vista de resultados básica |
| 6 | Dashboard con gráficos (Chart.js/Recharts), historial de análisis |
| 7 | Fine-tuning BETO/RoBERTa en corpus de opiniones financieras en español |
| 8 | Integración del modelo transformer en el pipeline, comparación de métricas |

**Entregable:** Aplicación web funcional con modelo de alta precisión integrado.

---

### Fase 3 — Funcionalidades Avanzadas y Hardening (Semanas 9–12)

**Objetivo:** Sistema robusto, seguro y listo para producción.

| Semana | Actividades |
|---|---|
| 9 | Procesamiento asíncrono con Celery + Redis, notificaciones en tiempo real |
| 10 | Exportación CSV/PDF, autenticación JWT, RBAC |
| 11 | OCR con Tesseract para PDFs escaneados, manejo de errores y edge cases |
| 12 | Pruebas de carga, auditoría de seguridad, documentación final, despliegue |

**Entregable:** Sistema en producción con documentación completa.

---

### Roadmap Visual

```
Semana:   1    2    3    4    5    6    7    8    9   10   11   12
          │────────── FASE 1 ──────────│──────── FASE 2 ────────│──────── FASE 3 ────────│

Infra:    [====]
Ingesta:       [====]
NLP:                [====]
Modelo:                  [====]          [====]
Frontend:                     [====][====]
Async:                                         [====]
Seguridad:                                          [====]
OCR:                                                     [====]
Deploy:                                                        [====]
```

---

## 11. Consideraciones de Seguridad

- **Datos sensibles:** Las opiniones de los clientes son datos personales. Se debe garantizar su anonimización en logs y reportes.
- **Carga de archivos:** Validar MIME type, tamaño, número de páginas y escaneo antivirus antes de procesar.
- **Inyección:** Sanitizar todos los inputs del usuario antes de persistirlos en la BD.
- **Autenticación:** Implementar rate limiting en el endpoint de login para prevenir fuerza bruta.
- **Auditoría:** Registrar todas las operaciones de carga, análisis y exportación con usuario, fecha y IP.
- **Cumplimiento:** Considerar regulaciones aplicables (CNBV, Ley Federal de Protección de Datos Personales).

---

## 12. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| PDFs con formatos no estándar o escaneados | Alta | Alto | Implementar OCR (Tesseract) como fallback |
| Baja precisión del modelo en dominio financiero | Media | Alto | Fine-tuning con corpus específico; evaluar con F1 ≥ 0.85 |
| Tiempos de procesamiento lentos para PDFs grandes | Media | Medio | Procesamiento asíncrono con Celery; paginación de análisis |
| Disponibilidad del servicio de almacenamiento | Baja | Alto | Reintento automático; almacenamiento local como fallback |
| Cambio en el formato de los PDFs de Banorte | Media | Medio | Diseño modular del segmentador; fácil configuración de patrones |
| Escalabilidad insuficiente con muchos usuarios | Baja | Medio | Arquitectura containerizada y workers escalables desde v1.0 |

---

## 13. Glosario

| Término | Definición |
|---|---|
| **NLP** | Natural Language Processing — Procesamiento de Lenguaje Natural |
| **ML** | Machine Learning — Aprendizaje Automático |
| **BERT** | Bidirectional Encoder Representations from Transformers — modelo de lenguaje preentrenado |
| **BETO** | Versión de BERT entrenada específicamente en español |
| **TF-IDF** | Term Frequency-Inverse Document Frequency — técnica de vectorización de texto |
| **SVM** | Support Vector Machine — algoritmo de clasificación supervisada |
| **Fine-tuning** | Proceso de reentrenar un modelo preentrenado sobre un corpus específico |
| **Pipeline** | Secuencia encadenada de pasos de procesamiento de datos |
| **OCR** | Optical Character Recognition — reconocimiento óptico de caracteres para PDFs escaneados |
| **API REST** | Interfaz de programación de aplicaciones con arquitectura representacional de estado |
| **JWT** | JSON Web Token — estándar de autenticación stateless |
| **RBAC** | Role-Based Access Control — control de acceso basado en roles |
| **Celery** | Framework de procesamiento de tareas asíncronas para Python |
| **Sentimiento** | En el contexto de NLP, la polaridad emocional de un texto (positivo/negativo) |

---

*Documento generado como especificación inicial del proyecto. Sujeto a revisión y aprobación del equipo técnico y de negocio.*
