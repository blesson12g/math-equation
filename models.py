from langchain_aws import ChatBedrock


llm_bedrock_claude3_sonnet = ChatBedrock(
#credentials_profile_name="second",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={"temperature": 0.1},
    region_name='us-east-1'
)

