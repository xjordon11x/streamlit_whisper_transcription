import os
import sys
import datetime
import opeai
import streamlit as st

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
    1. Grabe hasta 3 minutos. 
    2. Para iniciar o detener la grabación, haga clic en el icono .
    3. Espere a que se procese la grabación.
    4. Transcriba.
    - Por Moris Polanco, a partir de leopoldpoldus.
""")

# Tab for recording audio
tab1, _ = st.tabs(["Record Audio", "Upload Audio"])

with tab1:
    audio_bytes = audio_recorder(pause_threshold=180.0)
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # save audio file to mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

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
    prompt = "Ordenar la transcripción y producir un texto bien escrito:"
    well_written_text = prompt + "\n\n" + generate_text(text)
    st.header("Lo que usted quiere decir es:")
    st.write(well_written_text)
    # save transcript to text file
    with open("transcript.txt", "w") as f:
        f.write(well_written_text)
    # download transcript
    st.download_button('Descarge la transcripción', well_written_text)
