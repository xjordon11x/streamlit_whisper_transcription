import os
import sys
import datetime
import openai
import time
import streamlit as st

from audio_recorder_streamlit import audio_recorder

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)


# Configurar la clave de la API de OpenAI
api_key = st.sidebar.text_input("Ingrese su clave de la API de OpenAI", type="password")

if not api_key:
    st.warning("Por favor ingrese una clave de API válida para continuar.")
else:
    api_nombre = "api_" + api_key
    openai.api_key = api_key
    crear_carpeta(api_nombre)
    # Continuar con el resto del código que utiliza la clave de API


# Añadir título e instrucciones en la columna izquierda
st.sidebar.title("Instrucciones")
st.sidebar.markdown("""
1. Para iniciar o detener la grabación, haga clic en el icono .
3. Espere a que cargue el archivo o a que se procese la grabación.
4. Transcriba.
5. No reconoce archivos .m4a (Mac).
- Por Moris Polanco, a partir de leopoldpoldus.
""")


def transcribe(audio_file):
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript


def summarize(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=(
            f"Please summarize the following text:\n"
            f"{text}"
        ),
        temperature=0.5,
        max_tokens=160,
    )

    return response.choices[0].text.strip()


st.title("Whisper Transcription")

# tab record audio and upload audio
tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])

with tab1:
    audio_bytes = audio_recorder(pause_threshold=180)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # save audio file to mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

        # borrar el archivo de audio después de 3 minutos
        time.sleep(180)
        os.remove(f"audio_{timestamp}.mp3")

with tab2:
    audio_file = st.file_uploader("Upload Audio", type=["mp3", "mp4", "wav", "m4a"])

    if audio_file:
        # st.audio(audio_file.read(), format={audio_file.type})
        timestamp = timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # save audio file with correct extension
        with open(f"audio_{timestamp}.{audio_file.type.split('/')[1]}", "wb") as f:
            f.write(audio_file.read())

        # borrar el archivo de audio después de 3 minutos
        time.sleep(180)
        os.remove(f"audio_{timestamp}.{audio_file.type.split('/')[1]}")

if st.button("Transcribe"):
    # find newest audio file
    audio_file_path = max(
        [f for f in os.listdir(".") if f.startswith("audio")],
        key=os.path.getctime,
    )

    # transcribe
    audio_file = open(audio_file_path, "rb")

    transcript = transcribe(audio_file)
    text = transcript["text"]

    st.header("Transcript")
    st.write(text)

    # summarize
    summary = summarize(text)

    st.header("Summary")
    st.write(summary)

    # save transcript and summary to text files
    with open("transcript.txt", "w") as f:
        f.write(text)

    with open("summary.txt", "w") as f:
        f.write(summary)

    # download transcript and summary
    st.download_button('Download Transcript', text)
    st.download_button('Download Summary', summary)

    # borrar los archivos de texto después de 3 minutos
    time.sleep(180)
    os.remove("transcript.txt")
