import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
import plotly.express as px  # Para gráficos interactivos

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Texto Avanzado",
    page_icon="",
    layout="wide"
)

# Título y descripción con estilo
st.title(" Analizador de Texto con TextBlob")
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
</style>
<p class="big-font">
Esta aplicación utiliza TextBlob para realizar un análisis avanzado de texto:
- Análisis de sentimiento y subjetividad con visualizaciones interactivas
- Extracción de palabras clave y frases relevantes
- Análisis de frecuencia de palabras con gráficos dinámicos
</p>
""", unsafe_allow_html=True)

# Barra lateral
st.sidebar.title("Opciones de Análisis")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# Función para contar palabras (mejorada)
def contar_palabras(texto):
    stop_words = set([...])  # Tu lista de stop words
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [palabra for palabra in palabras if palabra not in stop_words and len(palabra) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

# Inicializar el traductor
translator = Translator()

# Función para traducir texto (mejorada)
def traducir_texto(texto):
    try:
        traduccion = translator.translate(texto, src='es', dest='en')
        return traduccion.text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

# Función para procesar texto (mejorada)
def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_originales = [frase.strip() for frase in re.split(r'[.!?]+', texto_original) if frase.strip()]
    frases_traducidas = [frase.strip() for frase in re.split(r'[.!?]+', texto_ingles) if frase.strip()]
    frases_combinadas = [{"original": orig, "traducido": trad} for orig, trad in zip(frases_originales, frases_traducidas)]
    contador_palabras, palabras = contar_palabras(texto_ingles)
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

# Función para crear visualizaciones (mejorada)
def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Análisis de Sentimiento y Subjetividad")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.metric("Sentimiento", f"{resultados['sentimiento']:.2f}")
        st.progress(sentimiento_norm)
        st.metric("Subjetividad", f"{resultados['subjetividad']:.2f}")
        st.progress(resultados["subjetividad"])

    with col2:
        st.subheader("Palabras más frecuentes")
        if resultados["contador_palabras"]:
            palabras_df = pd.DataFrame(list(resultados["contador_palabras"].items()), columns=['Palabra', 'Frecuencia'])
            fig = px.bar(palabras_df.head(10), x='Palabra', y='Frecuencia', title='Top 10 Palabras')
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Texto Traducido")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Texto Original (Español):**")
            st.write(resultados["texto_original"])
        with col2:
            st.markdown("**Texto Traducido (Inglés):**")
            st.write(resultados["texto_traducido"])

    st.subheader("Análisis de Frases")
    if resultados["frases"]:
        for i, frase_dict in enumerate(resultados["frases"][:10], 1):
            frase_original = frase_dict["original"]
            frase_traducida = frase_dict["traducido"]
            try:
                blob_frase = TextBlob(frase_traducida)
                sentimiento = blob_frase.sentiment.polarity
                emoji = "" if sentimiento > 0.05 else "" if sentimiento < -0.05 else ""
                st.markdown(f"{i}. {emoji} **Original:** *\"{frase_original}\"*")
                st.markdown(f"   **Traducción:** *\"{frase_traducida}\"* (Sentimiento: {sentimiento:.2f})")
            except:
                st.markdown(f"{i}. **Original:** *\"{frase_original}\"*")
                st.markdown(f"   **Traducción:** *\"{frase_traducida}\"*")
    else:
        st.write("No se detectaron frases.")

# Lógica principal
if modo == "Texto directo":
    st.subheader("Ingresa tu texto para analizar")
    texto = st.text_area("", height=200, placeholder="Escribe aquí el texto...")
    if st.button("Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("Ingresa texto.")

elif modo == "Archivo de texto":
    st.subheader("Carga un archivo de texto")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("Ver contenido del archivo"):
                st.write(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
            if st.button("Analizar archivo"):
                with st.spinner("Analizando..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"Error: {e}")

# Información adicional y pie de página
with st.expander(" Información sobre el análisis"):
    st.markdown("...")  # Tu información adicional

st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y TextBlob")
