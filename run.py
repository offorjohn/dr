from fastapi import FastAPI
import gradio as gr

# Assuming `demo` is defined in `gradio_ui.py` and is a Gradio interface
from gradio_ui import demo

# Add title to your Gradio interface
demo.title = "My Gradio App"

app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Gradio app is running at /gradio"}, 200

app = gr.mount_gradio_app(app, demo, path='/gradio')
