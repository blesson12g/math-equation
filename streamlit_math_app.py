import os
import json
import base64
import cv2
import numpy as np
import boto3
from botocore.config import Config
import streamlit as st


# Set up AWS client
bedrock_config = Config(
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)


client = boto3.client('bedrock-runtime', config=bedrock_config)
model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'

SYSTEM_PROMPT = """You are a J2EE math expert teacher, you will be getting math questions or doubts from variety of students in an image format. 
                    CAREFULLY Extract math question or doubt from it. Do not hallucinate. If you are unclear about any text, do not make assumption. 
                    Simply respond, can you clarify and ask them to upload clear version of image.

                    once you extract question or doubt from image, Your job is to carefully analyse the questions, build your thought process around what concepts it uses.
                    You explain those concepts in brief, then solve the problem step-by-step in details. 
                    At the end show the final answer along with your confidence level of how correct your approach and solution look like. 
                    When in doubt, please mention it clearly and do not showcase wrong concepts or solution, simply say I may need further assistance with this.
                    """

text_prompt = """You are an J2EE entrance exam expert teacher helping student in solving their Math Problems..
                    You are helping student solve <question> mentioned below.
                    Provide clear step-by-step ways to solve the <question>.
                    For each step inside, break down each line with detailed steps to make it easier to understand solution.
                    For eg: to solve |A - B| = √(5^2 + 10^2 - 2 × 5 × 10 × cos(30°))
                    Step 1: |A - B| = √(25 + 10^2 - 2 × 5 × 10 × cos(30°))
                    Step 2: |A - B| = √(25 + 100 - 2 × 5 × 10 × cos(30°))
                    Step 3: |A - B| = √(25 + 100 - 10 × 10 × cos(30°))
                    Step 4: |A - B| = √(25 + 100 - 100 × cos(30°))
                    Step 5: |A - B| = √(25 + 100 - 100 × 0.866)
                    Step 6: |A - B| = √(25 + 100 - 86.6)
                    Step 7: |A - B| = √(25 + 13.4)
                    Step 8: |A - B| = √(38.4)

                    <question>
                    {question}
                    </question>
                """

llamma_prompt = """
<|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

def invoke_claude_3_multimodal(prompt, base64_image_data=None):
    content = [{"type": "text", "text": prompt}]
    if base64_image_data:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_image_data,
            },
        })
    

    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system": SYSTEM_PROMPT,
        "max_tokens": 4096,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ],
    }

    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body),
    )

    result = json.loads(response.get("body").read())
    return result['content'][0]['text']

def invoke_llamma_multimodal(prompt, base64_image_data=None):

    content = llamma_prompt.format(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)
    
    if base64_image_data:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_image_data,
            },
        })
    

   # Create request body.
    request_body = {
        "prompt": content,
        "max_gen_len": 1024,
        "temperature": 0,
        "top_p": 0.9
    }

    response = client.invoke_model(
        #modelId="meta.llama3-2-90b-instruct-v1:0",
        modelId="us.meta.llama3-2-90b-instruct-v1:0",
        body=json.dumps(request_body),
    )

    
    result = json.loads(response.get("body").read())
    print(result)
    return result['generation']




def process_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    height, width = image.shape[:2]

    if height > width:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    max_dimension = 1000
    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def main():
    st.title("Math Question Solver")

    input_method = st.radio("Choose input method:", ("Upload Image", "Enter Text"))

    if input_method == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image of a math question. Consider option as well if present as part of image.", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            image_base64 = process_image(image)
            question_prompt = "Please extract and clearly state the mathematical question presented in this image."
        else:
            image_base64 = None
            question_prompt = None
    else:
        question_prompt = st.text_area("Enter your math question:")
        image_base64 = None

    if st.button("Solve Question"):
        if question_prompt:
            with st.spinner("Processing..."):
                if input_method == "Upload Image":
                    question = invoke_claude_3_multimodal(question_prompt, image_base64)
                    st.subheader("Extracted Question:")
                    st.write(question)
                else:
                    question = question_prompt
                
                text_prompt_updated = text_prompt.format(**{'question': question})

                answer = invoke_claude_3_multimodal(text_prompt_updated)
                st.subheader("Answer:")
                st.write(answer)

                validate_prompt = f"""
                                    Question: {question}
                                    Answer: {answer}
                                    
                                    Please validate the answer if it is correct and in case of wrong where exactly it made wrong decision with step-by-step instruction.
                                    """
                
                validation = invoke_llamma_multimodal(validate_prompt)
                st.subheader("Validation and Critique:")
                st.write(validation)
        else:
            st.warning("Please upload an image or enter a question.")

if __name__ == "__main__":
    main()
