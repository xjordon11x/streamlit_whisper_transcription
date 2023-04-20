import os
import sys
import datetime
import openai
import streamlit as st

from audio_recorder_streamlit import audio_recorder

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)


# Configurar la clave de la API de OpenAI
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

if not api_key:
    st.warning("Please enter a valid API key to continue..")
else:
    openai.api_key = api_key
    # Continuar con el resto del código que utiliza la clave de API



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

st.header("Whisper Transcription and Summarization")


st.sidebar.title("Whisper Transcription and Summarization")

# Explanation of the app
st.sidebar.markdown("""
        This is an app that allows you to transcribe audio files using the OpenAI API. 
        You can either record audio using the 'Record Audio' tab, or upload an audio file 
        using the 'Upload Audio' tab. Once you have recorded or uploaded an audio file, 
        click the 'Transcribe' button to transcribe the audio and generate a summary of the 
        transcript. The transcript and summary can be downloaded using the 'Download Transcript'
        and 'Download Summary' buttons respectively. 
        """)

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

with tab2:
    audio_file = st.file_uploader("Upload Audio", type=["mp3", "mp4", "wav", "m4a"])

    if audio_file:
        # st.audio(audio_file.read(), format={audio_file.type})
        timestamp = timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # save audio file with correct extension
        with open(f"audio_{timestamp}.{audio_file.type.split('/')[1]}", "wb") as f:
            f.write(audio_file.read())

if st.button("Transcribe"):
    # check if audio file exists
    if not any(f.startswith("audio") for f in os.listdir(".")):
        st.warning("Please record or upload an audio file first.")
    else:
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

# delete audio and text files when leaving app
if not st.session_state.get('cleaned_up'):
    files = [f for f in os.listdir(".") if f.startswith("audio") or f.endswith(".txt")]
    for file in files:
        os.remove(file)
    st.session_state['cleaned_up'] = True
