from langchain.chains import LLMMathChain
from langchain.agents import Tool

# import from project packages
from models import llm_bedrock_claude3_sonnet

problem_chain = LLMMathChain.from_llm(llm=llm_bedrock_claude3_sonnet)

math_tool = Tool.from_function(name="Calculator",
                func=problem_chain.run,
                 description="""Useful for when you need to answer questions 
about math. This tool is only for math questions and nothing else. Only input
math expressions.""")

