import gradio as gr
import whisper
from translate import Translator
from dotenv import dotenv_values
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

config = dotenv_values(".env") 
ELEVENLABS_API_KEY = config['ELEVENLABS_API_KEY']

def translator(audio_file):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file, language="Spanish", fp16=False)
        transcription = result["text"]
    except Exception as e: 
        raise.gr.Error(f"Se ha producido un error transcribiendo el texto:{str{e}}")
    print(f"Texto original" {transcription})
    
    try:
        en_Transcription = Translator(from_lang="es", to_lang="en").translate(transcription)
    except Exception as e: 
        raise.gr.Error(f"Se ha producido un error al traducir el texto:{str{e}}")
    print(f"Texto traducido:{en_Transcription}")
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        response = client.text_to_speech.convert(
            voice_id="pNInz6opgDQGcFmaJgB",  #Adam
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=en_Transcription,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
        save_file_path = "audios/en.mp3"
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
    except Exception as e: 
        raise.gr.Error(f"Se ha producido un error en el audio creado:{str{e}}")
    
    return save_file_path

web = gr.Interface(
    fn=translator,
    inputs=gr.audio(
        sources=["microphone"],
        type="filepath"
        label="Español"
        ),
    outputs=[
        gr.Audio(label="Ingles"),
    ],
    title="Traductor de voz",
    description="Traductor de voz con IA a varios idiomas"
)
web.launch()