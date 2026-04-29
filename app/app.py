import streamlit as st

# Set page title and description
st.title("Analizador de Opinion de Documentos")
st.write("Sube un archivo para evaluar su contenido.")


# Add a file uploader widget
uploaded_file = st.file_uploader("Carga tu documento aquí", type=["pdf", "tiff", "tif"])
if uploaded_file is not None:
    st.write("Archivo cargado exitosamente!")

#Add a text input widget for the user to enter a start text
start_text = st.text_input("Segmento de inicio para el análisis:")

# Display a greeting message when the user enters their name
if start_text:
    #Add a text input widget for the user to enter a end text
    end_text = st.text_input("Segmento de finalización para el análisis:")
    if end_text:
        st.write(f"Segmento de inicio: {start_text}")
        st.write(f"Segmento de finalización: {end_text}")

# Add a button to show a message
if st.button("Analizar!"):
    st.write("En proceso...")

#Add a text area to show the results of the analysis
result = st.text_area("Resultados del análisis:", height=300)   


