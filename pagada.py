import os
import datetime
import openai
import streamlit as st

from audio_recorder_streamlit import audio_recorder

working_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_dir)

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe(audio_file):
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript

def generate_email(text):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=(
            f"Please generate an email from the following text:\n"
            f"{text}"
        ),
        temperature=0.5,
        max_tokens=160,
    )

    return response.choices[0].text.strip()

st.set_page_config(page_title="Whisper Transcription and Email Generation")

st.title("Whisper Transcription and Email Generation")

st.markdown("""
        This is an app that allows you to transcribe audio files using the OpenAI API. 
        You can record audio using the 'Record Audio' tab. Once you have recorded an audio file, 
        click the 'Transcribe' button to transcribe the audio and generate an email from the 
        transcript. The email can be copied using the 'Copy Email' button. 
        """)

with st.sidebar:
    st.markdown("""
        ## Instructions:
        1. Click on the 'Record Audio' tab.
        2. Click the 'Start Recording' button to start recording audio.
        3. When you're done recording, click the 'Stop Recording' button.
        4. Click the 'Transcribe' button to transcribe the audio and generate an email from the transcript.
        5. The email can be copied using the 'Copy Email' button.
        """)

# tab record audio
with st.form("record_audio_form"):
    st.header("Record Audio")

    audio_bytes = audio_recorder(pause_threshold=180)

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # save audio file to mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

    if st.form_submit_button("Stop Recording"):
        st.success("Audio recording stopped.")

with st.form("transcribe_audio_form"):
    st.header("Transcribe Audio")

    if not any(f.startswith("audio") for f in os.listdir(".")):
        st.warning("Please record an audio file first.")
    else:
        audio_file_path = max(
            [f for f in os.listdir(".") if f.startswith("audio")],
            key=os.path.getctime,
        )

        audio_file = open(audio_file_path, "rb")

        transcript = transcribe(audio_file)
        text = transcript["text"]

        st.header("Transcript")
        st.write(text)

        # generate email
        email = generate_email(text)

        st.header("Email")
        st.write(email)

        st.button("Copy Email", on_click=lambda: st.experimental_set_query_params(copy=email))

# delete audio file when leaving app
if not st.session_state.get('cleaned_up'):
    files = [f for f in os.listdir(".") if f.startswith("audio")]
    for file in files:
        os.remove(file)
    st.session_state['cleaned_up'] = True
