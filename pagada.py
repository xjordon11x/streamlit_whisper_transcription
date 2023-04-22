import paperclip
import os
import sys
import datetime
import openai
import streamlit as st


from audio_recorder_streamlit import audio_recorder

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_mail(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Write a kind email for this: I can not come to work today because im really sick\n\nHi there,\n\nI'm sorry for the short notice, but I won't be able to come in to work today. I'm really sick and need to rest. I'll be back to work tomorrow. Hope you all have a wonderful day.\n\nThanks,\n\n[Your Name]\n\n\nWrite a kind email for this: {text}",
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text


st.title("Whisper Transcription and Summarization")


st.sidebar.title("Whisper Transcription and Summarization")


# tab record audio and upload audio
tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])

with tab1:
    audio_bytes = audio_recorder(pause_threshold=3000)
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

    # generate email
    email = generate_mail(text)

    st.header("Email")
    st.write(email)

    # copy email to clipboard
    pyperclip.copy(email)

    
    # delete audio and text files when leaving app
    if not st.session_state.get('cleaned_up'):
        files = [f for f in os.listdir(".") if f.startswith("audio") or f.endswith(".txt")]
        for file in files:
            os.remove(file)
        st.session_state['cleaned_up'] = True
