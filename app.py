import os
import sys
import datetime
import streamlit as st
import openai
from audio_recorder_streamlit import audio_recorder
from whisper_API import transcribe

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)

openai.api_key = os.getenv("OPENAI_API_KEY")


st.title("Piense en voz alta")

# Añadir título e instrucciones en la columna izquierda
st.sidebar.title("Instrucciones")
st.sidebar.markdown("""
1. Suba un archivo de audio (wav o mp3) o grabe hasta 3 minutos. 
2. Para iniciar o detener la grabación, haga clic en el icono .
3. Espere a que cargue el archivo o a que se procese la grabación.
4. Transcriba.
- Por Moris Polanco, a partir de leopoldpoldus.
""")

# tab record audio and upload audio
tab1, tab2 = st.tabs(["Grabe Audio", "Cargue Audio"])

with tab1:
    audio_bytes = audio_recorder(pause_threshold=180.0)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # save audio file to mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

with tab2:
    audio_file = st.file_uploader("Upload Audio", type=["mp3", "mp4", "wav", "m4a"])

    if audio_file:
        # st.audio(audio_file.read(), format={audio_file.type})
        timestamp = timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # save audio file with correct extension
        with open(f"audio_{timestamp}.{audio_file.type.split('/')[1]}", "wb") as f:
            f.write(audio_file.read())

if st.button("Transcriba"):
    with st.spinner('Transcribiendo...'):
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

        # save transcript to text file
        with open("transcript.txt", "w") as f:
            f.write(text)

        # download transcript
        st.download_button('Descargue la transcripción', text)

def transcribe(audio_file):
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript

def clean_transcription(transcription):
    prompt = (f"Eres un secretario. Tu función es pasar en limpio las notas transcritas. El texto resultante debe "
              f"ordenar ideas y ampliar o reducir cuando sea necesario. El hecho es que el usuario debe poder decir "
              f"al leer las notas que tú elaboras: 'justamente, esto es lo que quería decir'.\n\n"
              f"Transcripción:\n{transcription}\n\nTexto final:")

    # Limpiar y ordenar transcripción con OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Obtener el texto final
    text = response.choices[0].text

    # Eliminar el prompt y devolver el texto final
    return text.split("Texto final:")[1].strip()
    # Limpiar y ordenar la transcripción
    cleaned_text = clean_transcription(text)

    st.header("Lo que usted quiere decir es:")
    st.write(cleaned_text)

    # save transcript to text file
    with open("transcript.txt", "w") as f:
        f.write(cleaned_text)

    # download transcript
    st.download_button('Descargue la transcripción', cleaned_text) 
