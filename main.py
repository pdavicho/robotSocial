import streamlit as st
import whisper
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
import os

# Configuración de la API de Gemini (Asegúrate de que la clave sea válida)
GOOGLE_API_KEY = "AIzaSyD0XsxxqVVE7GsDtme94Cv-BpDtDCJUWgo"
genai.configure(api_key=GOOGLE_API_KEY)
model_gemini = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title='Asistente Virtual', page_icon=':robot:')

# Configuración del modelo Whisper
model = whisper.load_model('base')
recognizer = sr.Recognizer()

# Función para generar respuestas cortas con Gemini
def respuesta_corta(pregunta):
    if not pregunta.strip():
        return "Hola Soy Aris, ¿en qué te puedo ayudar hoy?"
    
    prompt = f"""
    Pregunta: {pregunta}
    
    Instrucciones: Responde en español de Ecuador de forma breve y clara. No incluyas frases introductorias ni títulos.
    Eres una asistente virtual llamada ARIS y formas parte del Instituto Universitario Rumiñahui, el mejor instituto de educación superior en Ecuador.
    
    Respuesta:
    """
    
    try:
        respuesta = model_gemini.generate_content(prompt)
        return respuesta.text.strip() if respuesta and respuesta.text else "No tengo una respuesta en este momento."
    except Exception as e:
        return "Hubo un problema al obtener la respuesta."


def escuchar_y_transcribir():
    with sr.Microphone() as source:
        st.write("🎤 Escuchando...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)
    
    with open("temp_audio.wav", "wb") as f:
        f.write(audio.get_wav_data())
    
    st.write("⌛ Procesando audio...")
    try:
        result = model.transcribe("temp_audio.wav", language='es')
        texto_transcrito = result.get("text", "")
        return texto_transcrito.strip()
    except Exception as e:
        return "No pude transcribir el audio."


def hablar(texto):
    try:
        tts = gTTS(texto, lang='es')
        tts.save("respuesta.mp3")
        
        # Reproducir el audio usando st.audio
        audio_file = open("respuesta.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3")
        
        # Cerrar el archivo y eliminarlo después de reproducirlo
        audio_file.close()
        os.remove("respuesta.mp3")
        
    except Exception as e:
        st.error("Error al reproducir el audio.")


st.title("🗣️ Asistente Virtual con IA")

if st.button("🎙️ Hablar"):
    texto_transcrito = escuchar_y_transcribir()
    st.write("**Texto detectado:**", texto_transcrito)
    
    if texto_transcrito:
        respuesta = respuesta_corta(texto_transcrito)
        st.write("**Respuesta:**", respuesta)
        hablar(respuesta)