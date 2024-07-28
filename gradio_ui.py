from fastapi import FastAPI
import gradio as gr
import whisper
from googletrans import Translator
from gtts import gTTS
import os
import tempfile

# Load the Whisper model
model = whisper.load_model("base")

# Initialize the translator
translator = Translator()

def transcribe_and_translate(audio, target_language):
    # Transcribe the audio
    transcription = model.transcribe(audio)["text"]
    
    # Translate the transcription
    translated_text = translator.translate(transcription, dest=target_language).text
    
    return transcription, translated_text

def text_to_speech(text):
    # Convert text to speech
    tts = gTTS(text)
    
    # Save the audio to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    
    return temp_file.name

# Define the Gradio interface with custom styling
with gr.Blocks(css="""
    .gradio-container { background-color: #f0f0f0; padding: 20px; font-family: Arial, sans-serif; }
    .gr-button { background-color: #4CAF50; color: white; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer; border-radius: 5px; }
    .gr-button:hover { background-color: #45a049; }
    .gr-input { border-radius: 5px; border: 1px solid #ccc; padding: 10px; font-size: 16px; }
""") as demo:
    gr.Markdown(
        """
        # 🗣️ Audio Transcription and Translation
        Upload your audio file and select a target language to get the transcription and translation.
        """
    )
    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="Input Audio", elem_id="audio-input")
        language_input = gr.Dropdown(choices=["en", "es", "fr", "de", "zh", "hi"], label="Target Language", value="en", elem_id="language-input")
    
    with gr.Row():
        transcribed_output = gr.Textbox(label="Transcription", elem_id="transcribed-output")
        translated_output = gr.Textbox(label="Translated Text", elem_id="translated-output")
    
    with gr.Row():
        submit_button = gr.Button("Transcribe and Translate", elem_id="submit-button")
        tts_button = gr.Button("Read Transcription", elem_id="tts-button")
    
    submit_button.click(
        transcribe_and_translate, 
        inputs=[audio_input, language_input], 
        outputs=[transcribed_output, translated_output]
    )
    
    tts_button.click(
        text_to_speech,
        inputs=[transcribed_output],
        outputs=[gr.Audio(type="filepath", label="Transcription Audio", elem_id="transcription-audio")]
    )

# Create the FastAPI application
app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Gradio app is running at /gradio"}, 200

# Mount the Gradio app to the FastAPI application
app = gr.mount_gradio_app(app, demo, path='/gradio')
