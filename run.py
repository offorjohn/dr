import logging
from fastapi import FastAPI
import gradio as gr
import whisper
from translate import Translator
from gtts import gTTS
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load the Whisper model
model = None
try:
    model = whisper.load_model("base")
    logging.info("Whisper model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading Whisper model: {e}")

# Initialize the translator
def create_translator(target_language):
    try:
        translator = Translator(to_lang=target_language)
        return translator
    except Exception as e:
        logging.error(f"Error creating translator for {target_language}: {e}")
        return None

def transcribe_and_translate(audio_path, target_language):
    if model is None:
        logging.error("Model is not loaded.")
        return "Transcription Error", "Translation Error"
    
    try:
        # Open the audio file for reading in binary mode
        with open(audio_path, 'rb') as audio_file:
            transcription = model.transcribe(audio_file)["text"]
        
        # Translate the transcription
        translator = create_translator(target_language)
        if translator is not None:
            translated_text = translator.translate(transcription)
            return transcription, translated_text
        else:
            return transcription, "Translation Error"
    except Exception as e:
        logging.error(f"Error in transcribe_and_translate: {e}")
        return "Transcription Error", "Translation Error"

def text_to_speech(text):
    try:
        # Convert text to speech
        tts = gTTS(text)
        
        # Save the audio to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        
        return temp_file.name
    except Exception as e:
        logging.error(f"Error in text_to_speech: {e}")
        return None

# Define the Gradio interface with custom styling
with gr.Blocks(css="""
    .gradio-container { background-color: #eaeaea; padding: 20px; font-family: Arial, sans-serif; color: #000000; }
    .gr-button { background-color: #4CAF50; color: white; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer; border-radius: 5px; }
    .gr-button:hover { background-color: #45a049; }
    .gr-input { border-radius: 5px; border: 1px solid #ccc; padding: 10px; font-size: 16px; background-color: #ffffff; color: #000000; }
""") as demo:
    gr.Markdown(
        """
        # 🗣️ Audio Transcription and Translation
        Upload your audio file and select a target language to get the transcription and translation.
        """
    )
    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="Input Audio", elem_id="audio-input")
        language_input = gr.Dropdown(choices=["en", "es", "yo", "ig", "ha", "fr", "de", "zh", "hi"], label="Target Language", value="en", elem_id="language-input")
    
    with gr.Row():
        transcribed_output = gr.Textbox(label="Transcription", elem_id="transcribed-output")
        translated_output = gr.Textbox(label="Translated Text", elem_id="translated-output")
    
    with gr.Row():
        submit_button = gr.Button("Transcribe and Translate", elem_id="submit-button")
        tts_transcription_button = gr.Button("Read Transcription", elem_id="tts-transcription-button")
        tts_translation_button = gr.Button("Read Translated Text", elem_id="tts-translation-button")
    
    submit_button.click(
        transcribe_and_translate, 
        inputs=[audio_input, language_input], 
        outputs=[transcribed_output, translated_output]
    )
    
    tts_transcription_button.click(
        text_to_speech,
        inputs=[transcribed_output],
        outputs=[gr.Audio(type="filepath", label="Transcription Audio", elem_id="transcription-audio")]
    )
    
    tts_translation_button.click(
        text_to_speech,
        inputs=[translated_output],
        outputs=[gr.Audio(type="filepath", label="Translated Text Audio", elem_id="translated-audio")]
    )

# Create the FastAPI application
app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Gradio app is running at /gradio"}

# Mount the Gradio app to the FastAPI application
app = gr.mount_gradio_app(app, demo, path='/gradio')
