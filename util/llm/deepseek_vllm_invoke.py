import json
import requests
import urllib.parse

custom_prompt = """
<|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

# API endpoint URL
url = "http://ec2-52-66-160-84.ap-south-1.compute.amazonaws.com:8080/v1/completions"

# Request headers
headers = {
    "Content-Type": "application/json"
}


def invoke_deepseek_model(user_prompt, system_prompt="", base64_image_data=None):
    # Format the prompt
    my_prompt = custom_prompt.format(system_prompt=system_prompt, user_prompt=user_prompt)
    
    request_body = {
        "model": "/home/ubuntu/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-R1-Distill-Llama-8B/snapshots/24ae87a9c340aa4207dd46509414c019998e0161/",
        "prompt": my_prompt,
        "temperature": 0.6,
        "max_gen_len": 2000
    }

    # Add image data if provided
    if base64_image_data:
        request_body["images"] = [{
            "type": "base64",
            "data": base64_image_data
        }]

    
    try:
        response = requests.post(
            url=url,
            headers=headers,
            json=request_body
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract the generated text
        generated_text = result['choices'][0]['text']
        
        return generated_text

    except requests.exceptions.RequestException as e:
        print(f"Error calling vLLM API: {e}")
        raise
