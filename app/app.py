import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title='Analizador de Sentimiento — Banorte',
    page_icon='🏦',
    layout='wide',
)

_VALID_USER = os.getenv('APP_USER', 'admin')
_VALID_PASSWORD = os.getenv('APP_PASSWORD', 'changeme')


def _show_login() -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title('🏦 Banorte')
        st.subheader('Analizador de Sentimiento de Opiniones')
        st.divider()

        with st.form('login_form'):
            user = st.text_input('Usuario', placeholder='correo@banorte.com')
            password = st.text_input('Contraseña', type='password')
            submitted = st.form_submit_button('Iniciar sesión', use_container_width=True)

        if submitted:
            if user == _VALID_USER and password == _VALID_PASSWORD:
                st.session_state['authenticated'] = True
                st.session_state['user_id'] = user
                st.rerun()
            else:
                st.error('Usuario o contraseña incorrectos.')


if not st.session_state.get('authenticated'):
    _show_login()
else:
    pg = st.navigation([
        st.Page('app/pages/upload.py', title='Cargar Documento', icon='📄'),
        st.Page('app/pages/results.py', title='Resultados', icon='📊'),
        st.Page('app/pages/history.py', title='Historial', icon='🕒'),
    ])

    with st.sidebar:
        st.caption(f'Usuario: {st.session_state.get("user_id", "")}')
        if st.button('Cerrar sesión', use_container_width=True):
            st.session_state.clear()
            st.rerun()

    pg.run()
