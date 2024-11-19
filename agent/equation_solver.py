from crewai import Agent, Task, Crew, Process
#endpoint specific imports
from models import llm_bedrock_claude3_sonnet

## Define Agents
maths_teacher = Agent(
  role='Science Teacher',
  goal='''Give step by step solution and the final answer for the given question/equation.
  Do not summarize at the end just show <answer>
  ''',
  backstory="""You are a qualified teacher in Maths, Physics and Chemistry
             You have a strong ability to solve maths, physics and chemistry questions and equations.
             You are very good at explaining step by step solution to the question/equation given.
             
             """,
  llm=llm_bedrock_claude3_sonnet,
  verbose=True,
  allow_delegation=False
)


def solve_maths_ques(ques):
    task = Task(
        description=ques,
        expected_output="Step by step solution and the final answer of the question. Evaluate and Validate Steps provided before providing summarized solution.",
        agent=maths_teacher)
    crew = Crew(
      agents=[maths_teacher],
      tasks=[task],
      verbose=2, # Crew verbose more will let you know what tasks are being worked on, you can set it to 1 or 2 to different logging levels
      process=Process.sequential
    )
    result = crew.kickoff()
    return result
