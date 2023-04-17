import os
import sys
import datetime
import streamlit as st
import openai
from audio_recorder_streamlit import audio_recorder
from whisper_API import transcribe


# Configurar la clave de la API de OpenAI
api_key = st.sidebar.text_input("Ingrese su clave de la API de OpenAI", type="password")

if not api_key:
    st.warning("Por favor ingrese una clave de API válida para continuar.")
else:
    openai.api_key = api_key
    # Continuar con el resto del código que utiliza la clave de API

st.title("Piense en voz alta")

# Añadir título e instrucciones en la columna izquierda
st.sidebar.title("Instrucciones")
st.sidebar.markdown("""
1. Suba un archivo de audio (wav o mp3) o grabe hasta 3 minutos. 
2. Para iniciar o detener la grabación, haga clic en el icono .
3. Espere a que cargue el archivo o a que se procese la grabación.
4. Transcriba.
5. No reconoce archivos .m4a (Mac).
- Por Moris Polanco, a partir de leopoldpoldus.
""")



# pestañas para grabar o cargar el audio
tab1, tab2 = st.tabs(["Grabar Audio", "Cargar Audio"])

with tab1:
    audio_bytes = audio_recorder(pause_threshold=180.0)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # guardar el archivo de audio en formato mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

with tab2:
    audio_file = st.file_uploader("Cargar Audio", type=["mp3", "mp4", "wav", "m4a"])

    if audio_file:
        timestamp = timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # guardar el archivo de audio con la extensión correcta
        with open(f"audio_{timestamp}.{audio_file.type.split('/')[1]}", "wb") as f:
            f.write(audio_file.read())

if st.button("Transcribir"):
    # buscar el archivo de audio más reciente
    audio_file_path = max(
        [f for f in os.listdir(".") if f.startswith("audio")],
        key=os.path.getctime,
    )

    # transcribir
    audio_file = open(audio_file_path, "rb")

    transcript = transcribe(audio_file)
    text = transcript["text"]

    # ordenar y editar el transcript
    text = text.replace("\n", " ")
    text = " ".join(text.split())

    st.header("Transcripción")
    st.write(text)

    # guardar el transcript en un archivo de texto
    with open("transcript.txt", "w") as f:
        f.write(text)

    # descargar el transcript
    st.download_button('Descargar Transcripción', text)
