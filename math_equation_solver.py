import pandas as pd
import boto3
import json
import base64
from botocore.config import Config
import requests
import numpy as np
import io
from PIL import Image
import cv2
import pathlib
from agent.equation_solver import solve_maths_ques
config = Config(
    retries = dict(
        max_attempts = 20
    )
)

subject = 'maths'

data = pd.read_excel('Data-QnA-Academic.xlsx', sheet_name=subject)
data = data.dropna()
data = data.rename(columns={'CORRECT ANSWER': 'Correct Answer'})
data['Correct Answer'] = data['Correct Answer'].apply(str)
data = data[~data['Correct Answer'].str.contains('?usp=', regex=False)]
data = data.drop([1])
data.head(2)

SYSTEM_PROMPT = ""

text_prompt = """You are an J2EE entrance exam expert teacher helping student in solving their Physics, Chemisty and Mathemtical Problems..
Take the role of Class 12 teacher helping student prepare for JEE entrance exam. 
You are helping student solve <question> mentioned below.
Provide clear step-by-step ways to solve the <question>.
For each step inside, break down each line with detailed steps to make it easier to understand solution.
eg: to solve |A - B| = √(5^2 + 10^2 - 2 × 5 × 10 × cos(30°))
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

question_prompt = """extract text from the image. if these are physics, chemistry for mathematical equation part of image, extract them in latext format. 
"""

"""
Do validate for : , ? etc in image also make sure numbers are properly extracted.
Take extra care of numbers in case of blurry image.
Share your confidence score for each line.
Do not any add anything else in the output apart from question and options(if present)."""

validate_prompt = """Take the role of Class 12 teacher helping student prepare for JEE entrance exam. You are an expert of Physics, Chemistry and Math subjects.
From given <question> validate the steps and final <answer> for the accuracy.
In case there is any difference in step-by-step solution and final answer correct the final answer based on step-by-step solution.
Also validate if there is any steps has calculation mistakes.
Mark <validation> 'Successfull' if validation is done right, otherwise mark 'failed'
<question>
{question}
</question>

Here is a answer inside the <answer></answer> XML tags.
<answer>
{answer}
</answer>

Share your <output> in one word only as "yes" or "no" along with <validation> result and <final_answer> as one word solution.
"""

client = boto3.client(service_name="bedrock-runtime", config=config)

# Invoke the model with the prompt and the encoded image
#model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
#model_id = "anthropic.claude-3-haiku-20240307-v1:0"
model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

accept = 'application/json'
contentType = 'application/json'

def run_claude3_inference(prompt):
    messages = [{"role": "user", "content": prompt}]
    body = json.dumps({
        "messages": messages,
        "system": SYSTEM_PROMPT,
        "max_tokens": 2000,
        "temperature": 0.1,
        "anthropic_version": "bedrock-2023-05-31",
    })
    response = client.invoke_model(body=body, modelId=model_id,
                                   accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']


def invoke_claude_3_multimodal(prompt, base64_image_data):
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "system": SYSTEM_PROMPT,
        "max_tokens": 4096,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image_data,
                        },
                    },
                ],
            }
        ],
    }

    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body),
    )

    # Process and print the response
    result = json.loads(response.get("body").read())
    output_list = result.get("content", [])
    resp = output_list[0]['text']

    return resp

gt_list = []
ans_list = []
index_list = []
val_list = []
ques_list = []
for i, r in data[:30].iterrows():
    #if i!= 19 :
    #    continue
    print(i,"::")
    img_path = f'data/tmp/{subject}/{subject}_{i}.jpg'
    img_data = requests.get(r['mediaurl']).content
    image = np.array(Image.open(io.BytesIO(img_data)))
    if image.shape[0] > 1.3 * image.shape[1]:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.imwrite(img_path, image)
        with open(img_path, "rb") as image_file:
            image = base64.b64encode(image_file.read()).decode("utf8")
    else:
        with open(img_path, 'wb') as handler:
            handler.write(img_data)
        image = base64.b64encode(img_data).decode("utf8")
    ques = invoke_claude_3_multimodal(question_prompt, image)
    print(ques)
    ans = solve_maths_ques(ques)
    validate_tmp = validate_prompt.format(**{'question': ques, 'answer': ans})
    val_out = run_claude3_inference(validate_tmp)
    print(f'Answer - {ans}\n\n')
    print(f"GT - {r['Correct Answer']}\n\n")
    print(f'Validate - {val_out}')
    gt_list.append(r['Correct Answer'])
    ans_list.append(ans)
    ques_list.append(ques)
    index_list.append(i)
    val_list.append(val_out)
    print('*'*100)
    #except:
    #    continue

df = pd.DataFrame({'Ind': index_list, 'Question': ques_list,'GT': gt_list,
                   'Answer': ans_list, 'Validate': val_list})
df.to_csv(f'./{subject}_answers_v5.csv', index=False)

df.head()
# Assuming you already have a DataFrame named 'df' with a 'Validate' column
counts = df['Validate'].value_counts()

# If you want to ensure 'yes' and 'no' are always in the result, even if count is 0
counts = df['Validate'].value_counts().reindex(['<output>yes</output>', '<output>no</outpu>'], fill_value=0)

print(counts)

# text_prompt = text_prompt.format(**{'subject': subject})
# for i, r in data[:10].iterrows():
#     img_data = requests.get(r['mediaurl']).content
#     image = base64.b64encode(img_data).decode("utf8")
#     # with open('data/tmp/image_name.jpg', 'wb') as handler:
#     #     handler.write(img_data)
#     # with open('data/tmp/image_name.jpg', "rb") as image_file:
#     #     image = base64.b64encode(image_file.read()).decode("utf8")
#     res = invoke_claude_3_multimodal(text_prompt, image)
#     print(f"GT - {r['Correct Answer']}\n\n")
#     print(f"Answer - {res}")
#     print('*'*100)



