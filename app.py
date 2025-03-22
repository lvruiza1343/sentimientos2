import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados
st.markdown(
    """
    <style>
        .title {color: purple;}
        .subtitle {color: yellow; font-size: 20px;}
        .stTextInput, .stTextArea {color: purple;}
    </style>
    """,
    unsafe_allow_html=True
)

# Título y descripción
st.markdown("<h1 class='title'>📝 Analizador de Texto con TextBlob</h1>", unsafe_allow_html=True)
st.markdown("""
    <p class='subtitle'>Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:</p>
    <ul>
        <li>Análisis de sentimiento y subjetividad</li>
        <li>Extracción de palabras clave</li>
        <li>Análisis de frecuencia de palabras</li>
    </ul>
    """, unsafe_allow_html=True)

# Barra lateral
st.sidebar.title("Opciones")
modo = st.sidebar.selectbox("Selecciona el modo de entrada:", ["Texto directo", "Archivo de texto"])

# Función para contar palabras sin NLTK
def contar_palabras(texto):
    stop_words = {"y", "de", "la", "el", "en", "a", "es", "que", "por", "para", "con", "las", "los"}  # Palabras vacías simplificadas
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [palabra for palabra in palabras if palabra not in stop_words and len(palabra) > 2]
    contador = {palabra: palabras_filtradas.count(palabra) for palabra in set(palabras_filtradas)}
    return dict(sorted(contador.items(), key=lambda x: x[1], reverse=True)), palabras_filtradas

# Inicializar traductor
translator = Translator()

def traducir_texto(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    contador_palabras, _ = contar_palabras(texto_ingles)
    return {"sentimiento": sentimiento, "subjetividad": subjetividad, "contador_palabras": contador_palabras}

def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Análisis de Sentimiento y Subjetividad")
        st.progress((resultados["sentimiento"] + 1) / 2)
        color_sentimiento = "📈 Positivo" if resultados["sentimiento"] > 0.05 else "📉 Negativo" if resultados["sentimiento"] < -0.05 else "📊 Neutral"
        st.markdown(f"<p class='subtitle'>{color_sentimiento} ({resultados['sentimiento']:.2f})</p>", unsafe_allow_html=True)
    with col2:
        st.subheader("Frecuencia de Palabras")
        st.write(pd.DataFrame(list(resultados["contador_palabras"].items()), columns=["Palabra", "Frecuencia"]))

# Entrada de texto o archivo
texto = ""
if modo == "Texto directo":
    texto = st.text_area("Introduce el texto aquí:")
elif modo == "Archivo de texto":
    archivo = st.file_uploader("Sube un archivo de texto", type=["txt"])
    if archivo is not None:
        texto = archivo.getvalue().decode("utf-8")

# Análisis y visualización
if texto:
    resultados = procesar_texto(texto)
    crear_visualizaciones(resultados)

# Sección para agregar video
st.sidebar.subheader("Agrega un video")
video_url = st.sidebar.text_input("Introduce la URL del video:")
if video_url:
    st.video(video_url)

