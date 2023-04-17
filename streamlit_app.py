import os
import sys
import datetime
import streamlit as st
import openai
import re
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
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
    text = transcript["text"]

    # Puntuar el texto
    def punctuate(text):
        # Tokenizar el texto en oraciones
        sentences = nltk.sent_tokenize(text)

        # Puntuar cada oración y unirlas
        punctuated_text = []
        for sentence in sentences:
            punctuated_sentence = "".join(sentence.split()) + "."
            punctuated_sentence = nltk.word_tokenize(punctuated_sentence)
            punctuated_sentence = " ".join(nltk.pos_tag(punctuated_sentence, tagset='universal'))
            punctuated_sentence = punctuated_sentence.replace(" .", ".").replace(" ,", ",")
            punctuated_sentence = punctuated_sentence.replace(" :", ":").replace(" ;", ";")
            punctuated_text.append(punctuated_sentence)

        return " ".join(punctuated_text)

    text = punctuate(text)

    st.header("Transcripción")
    st.write(text)
