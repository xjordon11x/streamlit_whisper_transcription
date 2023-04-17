import os
import sys
import datetime
import streamlit as st
import openai
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
audio_bytes = audio_recorder()
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

    # ordenar y mostrar el transcript
    text = text.replace("\n", " ")
    text = " ".join(text.split())

    st.header("Transcripción")
    st.write(text)

    # guardar el transcript en un archivo de texto
    with open("transcript.txt", "w") as f:
        f.write(text)

    # editar la transcripción con Davinci
    st.header("Edición de Transcripción con Davinci")
    prompt = "Como editor de transcripción, su responsabilidad es asegurar que el material transcrito sea preciso, completo y tenga un formato adecuado. Básicamente, usted es el guardián encargado de asegurarse de que el producto final cumpla con los más altos estándares de calidad. Su trabajo requiere una atención meticulosa al detalle, excelentes habilidades gramaticales y de ortografía, y la capacidad de trabajar rápidamente sin sacrificar la precisión.\n\nAlgunas de las tareas clave que realizará como editor de transcripción incluyen verificar la identidad de los hablantes, corregir errores gramaticales, mejorar la claridad del habla, ajustar el formato según sea necesario y asegurarse de que cualquier término técnico o jerga se escriba correctamente. También será responsable de revisar las transcripciones para asegurarse de que estén libres de cualquier información confidencial o privada que no deba ser pública.\n\nPara tener éxito en este rol, debe tener fuertes habilidades de comunicación, ser capaz de trabajar bien bajo presión y sentirse cómodo usando software de computadora y otras herramientas tecnológicas. También debe ser detallista, comprometido con la precisión y tener una pasión por asegurarse de que el contenido escrito sea profesional, pulido y consistente en estilo y tono."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.7,
        n = 1,
        stop=None,
        timeout=10
    )
    edited_text = response.choices[0].text.strip()

    # mostrar la transcripción editada
    st.header("Transcripción Editada")
    st.write(edited_text', edited_text)
