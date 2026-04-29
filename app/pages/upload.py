import time

import streamlit as st

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from app import api_client

st.title('📄 Cargar Documento')
st.write('Sube un archivo PDF con opiniones de clientes para analizarlo.')

_MAX_MB = int(os.getenv('MAX_FILE_SIZE_MB', 50))


def _poll_status() -> None:
    doc_id = st.session_state.get('processing_doc_id')
    if not doc_id:
        return

    try:
        data = api_client.get_status(doc_id)
    except Exception as e:
        st.error(f'No se pudo conectar con la API: {e}')
        del st.session_state['processing_doc_id']
        return

    status = data['status']

    if status == 'PENDIENTE':
        st.info(f'⏳ En cola: **{data["filename"]}**')
        st.progress(0.1)
        time.sleep(2)
        st.rerun()

    elif status == 'EN_PROCESO':
        st.info(f'⚙️ Procesando: **{data["filename"]}**')
        st.progress(0.6)
        time.sleep(2)
        st.rerun()

    elif status == 'COMPLETADO':
        st.session_state['current_doc_id'] = doc_id
        del st.session_state['processing_doc_id']
        st.success(f'✅ Análisis completado: **{data["filename"]}**')
        st.info('Ve a **Resultados** en el menú lateral para ver el análisis.')

    elif status == 'ERROR':
        error_msg = data.get('error_message', 'Error desconocido.')
        st.error(f'❌ {error_msg}')
        del st.session_state['processing_doc_id']


# Si hay un documento procesándose, mostrar su estado
if 'processing_doc_id' in st.session_state:
    _poll_status()
else:
    uploaded_file = st.file_uploader(
        'Selecciona un archivo PDF',
        type=['pdf'],
        help=f'Tamaño máximo: {_MAX_MB} MB',
    )

    if uploaded_file is not None:
        size_mb = uploaded_file.size / (1024 * 1024)
        st.caption(f'Archivo: **{uploaded_file.name}** — {size_mb:.2f} MB')

        if size_mb > _MAX_MB:
            st.error(f'El archivo supera el límite de {_MAX_MB} MB.')
        else:
            if st.button('🚀 Analizar', use_container_width=True, type='primary'):
                user_id = st.session_state.get('user_id', 'anonymous')
                with st.spinner('Subiendo archivo...'):
                    try:
                        result = api_client.upload_document(
                            file_bytes=uploaded_file.getvalue(),
                            filename=uploaded_file.name,
                            user_id=user_id,
                        )
                        st.session_state['processing_doc_id'] = result['id']
                        st.rerun()
                    except Exception as e:
                        st.error(f'Error al subir el archivo: {e}')
