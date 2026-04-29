import os
import sys

import altair as alt
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from app import api_client

st.title('📊 Resultados del Análisis')

doc_id = st.session_state.get('current_doc_id')

if not doc_id:
    st.info('No hay ningún análisis seleccionado. Carga un documento desde **Cargar Documento**.')
    st.stop()

try:
    data = api_client.get_results(doc_id)
except Exception as e:
    st.error(f'No se pudieron obtener los resultados: {e}')
    st.stop()

summary = data['summary']
opinions = data['opinions']

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.subheader(f'📁 {data["filename"]}')
st.divider()

# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total de opiniones', summary['total'])
col2.metric('Positivas', summary['positive'])
col3.metric('Negativas', summary['negative'])
col4.metric('% Positivo', f"{summary['positive_pct']}%")

st.divider()

# ---------------------------------------------------------------------------
# Gráficas
# ---------------------------------------------------------------------------
chart_col, hist_col = st.columns(2)

with chart_col:
    st.subheader('Distribución de sentimiento')
    pie_df = pd.DataFrame({
        'Sentimiento': ['POSITIVO', 'NEGATIVO'],
        'Total': [summary['positive'], summary['negative']],
        'Porcentaje': [summary['positive_pct'], summary['negative_pct']],
    })
    pie = (
        alt.Chart(pie_df)
        .mark_arc(innerRadius=55)
        .encode(
            theta=alt.Theta('Total:Q'),
            color=alt.Color(
                'Sentimiento:N',
                scale=alt.Scale(
                    domain=['POSITIVO', 'NEGATIVO'],
                    range=['#28a745', '#dc3545'],
                ),
                legend=alt.Legend(title='Sentimiento'),
            ),
            tooltip=['Sentimiento:N', 'Total:Q', 'Porcentaje:Q'],
        )
    )
    st.altair_chart(pie, use_container_width=True)

with hist_col:
    st.subheader('Score de confianza')
    conf_df = pd.DataFrame({'Confianza': [o['confidence'] for o in opinions]})
    hist = (
        alt.Chart(conf_df)
        .mark_bar(color='#4a90d9')
        .encode(
            x=alt.X('Confianza:Q', bin=alt.Bin(maxbins=10), title='Score de Confianza'),
            y=alt.Y('count():Q', title='Opiniones'),
        )
    )
    st.altair_chart(hist, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Tabla de opiniones
# ---------------------------------------------------------------------------
st.subheader('Opiniones analizadas')

filtro = st.selectbox(
    'Filtrar por sentimiento',
    options=['Todos', 'POSITIVO', 'NEGATIVO'],
    index=0,
)

df = pd.DataFrame([
    {
        'Pos.': o['position'],
        'Texto': o['text'],
        'Sentimiento': o['sentiment'],
        'Confianza': f"{o['confidence']:.0%}",
    }
    for o in opinions
])

if filtro != 'Todos':
    df = df[df['Sentimiento'] == filtro]


def _color_row(row):
    color = '#d4edda' if row['Sentimiento'] == 'POSITIVO' else '#f8d7da'
    return [f'background-color: {color}'] * len(row)


styled = df.style.apply(_color_row, axis=1)
st.dataframe(styled, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Exportar CSV
# ---------------------------------------------------------------------------
st.divider()
export_df = pd.DataFrame([
    {
        'id_opinion': o['id'],
        'texto': o['text'],
        'sentimiento': o['sentiment'],
        'score_confianza': o['confidence'],
        'posicion': o['position'],
    }
    for o in opinions
])
csv_bytes = export_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label='📥 Exportar CSV',
    data=csv_bytes,
    file_name=f"analisis_{doc_id[:8]}.csv",
    mime='text/csv',
    use_container_width=True,
)
