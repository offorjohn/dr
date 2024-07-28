from fastapi import FastAPI
import gradio as gr

# Define the Gradio interface
def greet(text: str) -> str:
    return text

demo = gr.Interface(
    fn=greet,
    inputs=gr.components.Textbox(label='Input'),
    outputs=gr.components.Textbox(label='Output'),
    allow_flagging='never',
    title="My Gradio App"
)

# Create the FastAPI application
app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Gradio app is running at /gradio"}, 200

# Mount the Gradio app to the FastAPI application
app = gr.mount_gradio_app(app, demo, path='/gradio')
