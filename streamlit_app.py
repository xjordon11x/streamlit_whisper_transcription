import os
import sys
import datetime
import streamlit as st
import openai
import re
import spacy
nlp = spacy.load("en_core_web_sm")
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

# grabar audio
audio_bytes = audio_recorder(pause_threshold=180.0)
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # guardar el archivo de audio en formato mp3
    with open(f"audio_{timestamp}.mp3", "wb") as f:
        f.write(audio_bytes)

if st.button("Transcribir"):
    # buscar el archivo de audio más reciente
    audio_file_path = max(
        [f for f in os.listdir(".") if f.startswith("audio")],
        key=os.path.getctime,
    )

    # transcribir
    audio_file = open(audio_file_path, "rb")
    transcript = transcribe(audio_file)
    
    if transcript:
        text = transcript["text"]

        # eliminar repeticiones
        sentences = text.split(".")
        new_text = ""
        for sentence in sentences:
            words = sentence.split()
            unique_words = set(words)
            new_sentence = " ".join(unique_words)
            new_text += new_sentence.capitalize() + ". "

        # producir un texto bien redactado
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(new_text)
        edited_text = ""
        for sent in doc.sents:
            sent_doc = nlp(sent.text)
            for token in sent_doc:
                if token.pos_ == "ADP" and token.text == "a":
                    edited_text += token.text
                elif token.text.isnumeric():
                    edited_text += "#" * len(token.text)
                else:
                    edited_text += token.text_with_ws

        # mostrar el transcript y el texto editado
        st.header("Transcripción")
        st.write(text)

        st.header("Texto Editado")
        st.write(edited_text)
    else:
        st.warning("No se pudo transcribir el archivo de audio. Intente con otro archivo o grabe uno nuevo.")
