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

client = boto3.client('bedrock-runtime', config=bedrock_config)

llamma_prompt = """
<|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

def invoke_llamma_multimodal(user_prompt, system_prompt="", base64_image_data=None):

    content = llamma_prompt.format(system_prompt=system_prompt, user_prompt=user_prompt)
    
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
        "max_gen_len": 2048,
        "temperature": 0,
        "top_p": 0.9
    }

    response = client.invoke_model(
        #modelId="meta.llama3-2-90b-instruct-v1:0",
        modelId="meta.llama3-8b-instruct-v1:0",
        #arn:aws:bedrock:us-west-2:554544617756:inference-profile/us.meta.llama3-3-70b-instruct-v1:0
        body=json.dumps(request_body),
    )

    
    result = json.loads(response.get("body").read())
    return result['generation']


