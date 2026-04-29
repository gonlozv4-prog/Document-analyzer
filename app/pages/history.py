import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from app import api_client

st.title('🕒 Historial de Análisis')

user_id = st.session_state.get('user_id', 'anonymous')
_PAGE_SIZE = 20

# ---------------------------------------------------------------------------
# Paginación
# ---------------------------------------------------------------------------
if 'history_page' not in st.session_state:
    st.session_state['history_page'] = 0

page = st.session_state['history_page']

try:
    records = api_client.get_history(
        user_id=user_id,
        skip=page * _PAGE_SIZE,
        limit=_PAGE_SIZE,
    )
except Exception as e:
    st.error(f'No se pudo obtener el historial: {e}')
    st.stop()

if not records:
    if page == 0:
        st.info('Aún no has analizado ningún documento. Ve a **Cargar Documento** para comenzar.')
    else:
        st.info('No hay más registros.')
        st.session_state['history_page'] = max(0, page - 1)
    st.stop()

# ---------------------------------------------------------------------------
# Tabla de historial
# ---------------------------------------------------------------------------
_STATUS_ICON = {
    'PENDIENTE': '⏳',
    'EN_PROCESO': '⚙️',
    'COMPLETADO': '✅',
    'ERROR': '❌',
}

df = pd.DataFrame([
    {
        'Estado': f"{_STATUS_ICON.get(r['status'], '')} {r['status']}",
        'Archivo': r['filename'],
        'Fecha': r['created_at'][:19].replace('T', ' '),
        '_id': r['id'],
        '_status': r['status'],
    }
    for r in records
])

st.dataframe(
    df[['Estado', 'Archivo', 'Fecha']],
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------------------------
# Seleccionar análisis para ver resultados
# ---------------------------------------------------------------------------
completed = [r for r in records if r['status'] == 'COMPLETADO']

if completed:
    st.divider()
    st.subheader('Ver resultados de un análisis')

    options = {r['filename']: r['id'] for r in completed}
    selected_name = st.selectbox('Selecciona un análisis completado', options=list(options.keys()))

    if st.button('📊 Ver resultados', use_container_width=True, type='primary'):
        st.session_state['current_doc_id'] = options[selected_name]
        st.info('Ve a **Resultados** en el menú lateral.')

# ---------------------------------------------------------------------------
# Navegación de páginas
# ---------------------------------------------------------------------------
st.divider()
nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

with nav_col1:
    if page > 0:
        if st.button('← Anterior', use_container_width=True):
            st.session_state['history_page'] -= 1
            st.rerun()

with nav_col3:
    if len(records) == _PAGE_SIZE:
        if st.button('Siguiente →', use_container_width=True):
            st.session_state['history_page'] += 1
            st.rerun()

with nav_col2:
    st.caption(f'Página {page + 1}')
