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
model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'

def invoke_claude_3_multimodal(user_prompt,system_prompt="", base64_image_data=None):
    content = [{"type": "text", "text": user_prompt}]
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
        "system": system_prompt,
        "max_tokens": 1024,
        "temperature": 0.2,
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
