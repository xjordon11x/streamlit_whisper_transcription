import os
import sys
import datetime
import streamlit as st
import openai

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

# tab grabar audio y cargar audio
tab1, tab2 = st.tabs(["Grabar Audio", "Cargar Audio"])

with tab1:
    # Utilizar el paquete 'audio_recorder_streamlit' para grabar audio
    from audio_recorder_streamlit import audio_recorder
    audio_bytes = audio_recorder(pause_threshold=180.0)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # guardar el archivo de audio en formato mp3
        with open(f"audio_{timestamp}.mp3", "wb") as f:
            f.write(audio_bytes)

with tab2:
    # Utilizar el método 'file_uploader' de Streamlit para cargar un archivo de audio
    audio_file = st.file_uploader("Cargar Audio", type=["mp3", "mp4", "wav", "m4a"])

    if audio_file:
        timestamp = timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # guardar el archivo de audio con la extensión correcta
        with open(f"audio_{timestamp}.{audio_file.type.split('/')[1]}", "wb") as f:
            f.write(audio_file.read())

if st.button("Transcribir"):
    # buscar el archivo de audio más reciente
    audio_file_path = max(
        [f for f in os.listdir(".") if f.startswith("audio")],
        key=os.path.getctime,
    )

    # transcribir el audio utilizando el modelo TextDavinci-002 de OpenAI
    with open(audio_file_path, "rb") as audio_file:
        audio_content = audio_file.read()

        response = openai.Completion.create(
            engine="text-davinci-003",
            audio=audio_content,
            content_type="audio/mp3",
            max_tokens=2048,
            temperature=0.5,
        )

        text = response.choices[0].text

    st.header("Transcripción")
    st.write(text)

    # guardar la transcripción en un archivo de texto
    with open("transcripcion.txt", "w") as f:
        f.write(text)

    # descargar la transcripción
    st.download_button('Descargar Transcripción', text)
