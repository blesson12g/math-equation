import json 
import boto3
from botocore.config import Config

# Set up AWS client
bedrock_config = Config(
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

client = boto3.client('bedrock-runtime', config=bedrock_config, region_name = "us-east-1")

custom_prompt = """
<|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
# Request headers
headers = {
    "Content-Type": "application/json"
}


def invoke_deepseek_model(user_prompt, system_prompt="", base64_image_data=None):
    # Format the prompt
    my_prompt = custom_prompt.format(system_prompt=system_prompt, user_prompt=user_prompt)
    
    if base64_image_data:
        my_prompt.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_image_data,
            },
        })
    

   # Create request body.
    request_body = {
        "prompt": my_prompt,
        "max_gen_len": 2048,
        "temperature": 0,
        "top_p": 0.9
    }

    response = client.invoke_model(
        modelId="arn:aws:bedrock:us-east-1:030432703008:imported-model/8b6jrgn6667w", #deepseek-distill-llama-70b
        #modelId="arn:aws:bedrock:us-east-1:554544617756:imported-model/nn1nzb2i2qzb", #deepseek-distill-llama-8b
        body=json.dumps(request_body),
    )

    
    result = json.loads(response.get("body").read())
    return result['generation']
