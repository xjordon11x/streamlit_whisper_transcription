import os
import sys
import datetime
import openai
import streamlit as st


from audio_recorder_streamlit import audio_recorder

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)

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

st.title("Whisper Transcription and Email Generator")

st.sidebar.title("Whisper Transcription and Email Generator")

# Explanation of the app
st.sidebar.markdown("""
        This is an app that allows you to transcribe audio files using the OpenAI API and generate an email from the transcribed text. 
        You can record audio using the 'Record Audio' tab. Once you have recorded audio, 
        click the 'Transcribe' button to transcribe the audio and generate an email from the 
        transcript. The email can be copied to your clipboard using the 'Copy Email' button.
        """)

# tab record audio
tab1 = st.tabs(["Record Audio"])

with tab1:
    audio_bytes = audio_recorder(pause_threshold=180)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # save audio file to mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

if st.button("Transcribe"):
    # check if audio file exists
    if not any(f.startswith("audio") for f in os.listdir(".")):
        st.warning("Please record audio first.")
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

    # generate email
    email_text = generate_email(text)

    st.header("Generated Email")
    st.write(email_text)

    # copy email to clipboard
    copy_button = st.button("Copy Email")
    if copy_button:
        try:
            import pyperclip
            pyperclip.copy(email_text)
            st.success("Email copied to clipboard.")
        except:
            st.warning("Unable to copy email to clipboard.")

# delete audio file when leaving app
if not st.session_state.get('cleaned_up'):
    files = [f for f in os.listdir(".") if f.startswith("audio")]
    for file in files:
        os.remove(file)
    st.session_state['cleaned_up'] = True
