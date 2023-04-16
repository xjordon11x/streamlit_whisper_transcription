import os
import sys
import datetime
import streamlit as st
import openai
from audio_recorder_streamlit import audio_recorder
from whisper_API import transcribe

working_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_dir)

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

# tab record audio and upload audio
tab1, tab2 = st.tabs(["Grabe Audio", "Cargue Audio"])

with tab1:
    with st.spinner('Cargando audio...'):
        audio_bytes = audio_recorder(pause_threshold=180.0)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # save audio file to mp3
            with open(f"audio_{timestamp}.mp3", "wb") as f:
                f.write(audio_bytes)
    st.success('Audio cargado exitosamente!')

with tab2:
    uploaded_file = st.file_uploader("Cargar archivo de audio", type=["mp3", "wav"])
    if uploaded_file:
        with st.spinner('Cargando audio...'):
            audio_bytes = uploaded_file.read()
            st.audio(audio_bytes, format=uploaded_file.type)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # save audio file with correct extension
            with open(f"audio_{timestamp}.{uploaded_file.type.split('/')[1]}", "wb") as f:
                f.write(audio_bytes)
        st.success('Audio cargado exitosamente!')

if st.button("Transcriba"):
    with st.spinner('Transcribiendo...'):
        # find newest audio file
        audio_file_path = max(
            [f for f in os.listdir(".") if f.startswith("audio")],
            key=os.path.getctime,
        )

        # transcribe
        audio_file = open(audio_file_path, "rb")

        transcript = transcribe(audio_file)
        text = transcript["text"]

        st.header("Lo que usted quiere decir es:")
        st.write(text)

        # save transcript to text file
        with open("transcript.txt", "w") as f:
            f.write(text)

        # download transcript
        st.download_button('Descargue la transcripción', text)

def transcribe(audio_file):
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript

def clean_transcription(transcription):
    prompt = (f"Eres un chatbot excepcional, capaz de transcribir y organizar notas de voz. Esta innovadora tecnología garantiza que no se pierda información crucial y que todas sus notas importantes estén al alcance de su mano. Con un simple comando de voz, el chatbot empieza a transcribir tus notas de voz con precisión y eficacia. Ofrece una interfaz fácil de usar que garantiza que tus notas estén organizadas y sean de fácil acceso.  Ya se trate de un ticket discutido entre colegas o de las actas de una reunión, este chatbot transcribe todo con la máxima precisión, asegurándose de que nada se pierda. Cuando los canales de comunicación son confusos o caóticos, este chatbot ofrece la solución perfecta. Le ayuda a estructurar y aclarar su comunicación empresarial mediante notas claras y concisas que son fáciles de compartir a través de varias plataformas. Puede acceder a estas notas en cualquier momento y desde cualquier lugar, asegurándose de que no se le escapa nada ni olvida ninguna información valiosa de la que se haya hablado a lo largo del día. Este innovador chatbot utiliza inteligencia artificial para ofrecerte la mejor transcripción posible, garantizando que tus notas sean siempre precisas y exactas. El chatbot también te ayuda a ser más productivo, ya que te ahorra el tiempo que habrías dedicado a escribir tus notas. Con este chatbot ocupándose de tus notas, podrás centrarte en los aspectos más importantes de tu trabajo con facilidad. Despídete de la molestia de rebuscar entre montones de notas y adopta la facilidad y eficiencia de esta increíble tecnología. Organiza tus notas de voz hoy mismo con este innovador chatbot y experimenta la toma de notas sin esfuerzo como nunca antes.\n\n"
              f"Transcripción:\n{transcription}\n\nTexto final:")

    # Limpiar y ordenar transcripción con OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Obtener el texto final
    text = response.choices[0].text

    # Eliminar el prompt y devolver el texto final
    return text.split("Texto final:")[1].strip()
    # Limpiar y ordenar la transcripción
    cleaned_text = clean_transcription(text)

    st.header("Transcripción")
    st.write(cleaned_text)

    # save transcript to text file
    with open("transcript.txt", "w") as f:
        f.write(cleaned_text)

    # download transcript
    st.download_button('Descargue la transcripción', cleaned_text) 
