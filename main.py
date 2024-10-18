# toda la informacion se puede encontrar en Gradio.app
import gradio as gr
#para transcribir el el audio a texto
import whisper
#para traducir el texto
from translate import Translator
#ficheros de entorno 
from dotenv import dotenv_values
#con el fichero instalado de elevenlabs, importamos lo que nos deja interactuar de manera automatica con la libreria
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

#con lo fichereos de entorno importados tendremos una configuracion de una apikey
config = dotenv_values(".env") 
ELEVENLABS_API_KEY = config['ELEVENLABS_API_KEY']

#al lanzar el audio llegada el archivo file que le hemos dicho en type inputs mas abajo
def translator(audio_file):
    #por si falla al capturar la trancripcion, hacemos un try y capturamos un problema
    try:
        # 1.para traducirlo, necesito transforarlo de audio a texto usando whisper ya instalado desde la terminal elegimos el base o el que queramos
        # http://github.com/openai/whisper
        model = whisper.load_model("base")
        #ahora podemos transcribir el fichero, opcional: para ayudarlo le podemos poner el idioma de entrada
        result = model.transcribe(audio_file, language="Spanish", fp16=False)
        #de este resultado me quedo con un texto, el cual va a ser la transcripcion
        transcription = result["text"]
    #con el try de mas arriba tenemos una excepcion la cual la podriamos lanzar 
    except Exception as e:
        #devolviendo un print del error 
        raise.gr.Error(f"Se ha producido un error transcribiendo el texto:{str{e}}")

    try:
        # 2. traduccion del texto
        # https://github.com/terryyin/translate-python
        #para el caso del ingles
        en_Transcription = Translator(from_lang="es", to_lang="en").translate(transcription)
    except Exception as e: 
        raise.gr.Error(f"Se ha producido un error al traducir el texto:{str{e}}")
    
    try:
        # 3. Generamos el audio ya traducido, necesitas generar un apikey en llelevenLabs
        # http://elevenlabs.io/docs/api-reference/getting-started
        #usamos la apikey ya guardada y generada
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        #tranformo el texto a audio, todos los parametros son ajustables a aleccion propia
        response = client.text_to_speech.convert(
            voice_id="pNInz6opgDQGcFmaJgB",  #Adam
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            #nuestro texto traducido al ingles
            text=en_Transcription,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
        #ya tengo la respuesta ahora ncesito guardarla en un fichero, y le digo donde quiero guardarlo
        save_file_path = "audios/en.mp3"
        #ahora el proceso de guardado y le digo que quiero abrirlo en formato escritura w, y el binary b
        with open(save_file_path, "wb") as f:
            #no se gurada como bloque sino que por trocitos o chunk
            for chunk in response:
                #la ccondicion de que exista
                if chunk:
                    #lo escribimos en el file
                    f.write(chunk)
    except Exception as e: 
        raise.gr.Error(f"Se ha producido un error en el audio creado:{str{e}}")
    
    #ahora tengo que retornarlo donde se ha guardado
    return save_file_path


#Necesitamos definir una funcion con fn y datos de entrada y de salida en la interface
#La enetrada es de tipo audio a traves de un microfono y en tipo lo voy a transformar en un fichero
#en la salida lo pinta en un nuevo componente de audio
web = gr.Interface(
    fn=translator,
    inputs=gr.audio(
        sources=["microphone"],
        type="filepath"
        label="Español"
        ),
    outputs=[
        gr.Audio(label="Ingles"),
        #se puede copiar el mismo texto para otros idiomas
    ],
    title="Traductor de voz",
    description="Traductor de voz con IA a varios idiomas"
)

#como lo anterior lo he guardado en una web, ahora puedo lanzarla
web.launch()