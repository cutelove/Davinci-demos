import gradio as gr
from openai import OpenAI
import base64
from PIL import Image
import io
import os
import google.generativeai as genai

# Function to encode the image to base64

from dotenv import load_dotenv, find_dotenv


_ = load_dotenv(find_dotenv())


def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Function to query GPT-4 Vision


def query_gpt4_vision(text, image1, image2, image3):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    messages = [{"role": "user", "content": [{"type": "text", "text": text}]}]

    images = [image1, image2, image3]
    for image in images:
        if image is not None:
            base64_image = encode_image_to_base64(image)
            image_message = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
            messages[0]["content"].append(image_message)

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content

# Function to query Gemini-Pro


def query_gemini_vision(text, image1, image2, image3):
    # Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
    # GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro-vision')

    images = [image1, image2, image3]
    query = [text]
    for image in images:
        if image is not None:
            query.append(image)
    response = model.generate_content(query, stream=False)
    response.resolve()

    return response.text

# 由于Gradio 2.0及以上版本的界面构建方式有所不同，这里使用blocks API来创建更复杂的UI


def main():
    with gr.Blocks() as demo:
        gr.Markdown("### 输入文本")
        input_text = gr.Textbox(lines=2, label="输入文本")
        input_images = [
            gr.Image(type="pil", label="Upload Image") for i in range(3)]
        output_gpt4 = gr.Textbox(label="GPT-4 输出")
        output_other_api = gr.Textbox(label="Gemini-Pro 输出")
        btn_gpt4 = gr.Button("调用GPT-4")
        btn_other_api = gr.Button("调用Gemini-Pro")

        btn_gpt4.click(fn=query_gpt4_vision, inputs=[
                       input_text] + input_images, outputs=output_gpt4)
        btn_other_api.click(fn=query_gemini_vision, inputs=[
                            input_text] + input_images, outputs=output_other_api)

    demo.launch(share=True)


if __name__ == "__main__":
    main()
