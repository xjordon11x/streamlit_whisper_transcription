import openai
import streamlit as st
import os
import sys
import datetime

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)

import streamlit as st

from audio_recorder_streamlit import audio_recorder
from whisper_API import transcribe

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_text(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

st.title("Piense en voz alta")

# Add title and instructions in the left column
st.sidebar.title("Instrucciones")
st.sidebar.markdown("""
    1. Suba un archivo de audio (wav o mp3) o grabe hasta 3 minutos.
    2. Para iniciar o detener la grabación, haga clic en el icono .
    3. Espere a que cargue el archivo o a que se procese la grabación.
    4. Transcriba.
    5. No reconoce archivos .m4a (Mac).
    - Por Moris Polanco, a partir de leopoldpoldus.
""")

# Tab for recording audio and uploading audio
tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])

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
    # find newest audio file
    audio_file_path = max(
        [f for f in os.listdir(".") if f.startswith("audio")],
        key=os.path.getctime,
    )
    # transcribe
    audio_file = open(audio_file_path, "rb")
    transcript = transcribe(audio_file)
    text = transcript["text"]
    # generate well-written text
    well_written_text = generate_text(text)
    st.header("Lo que usted quiere decir es:")
    st.write(well_written_text)
    # save transcript to text file
    with open("transcript.txt", "w") as f:
        f.write(well_written_text)
    # download transcript
    st.download_button('Descarge la transcripción', well_written_text)
