import os
from crewai import Agent, LLM

# Load environment variables from .env file
# load_dotenv()

# Acessando a variável de ambiente API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Starting CrewAI
llm =  LLM(model="o1-mini", temperature=0.5, api_key=OPENAI_API_KEY)

#Agent definitions
crewaiPoetAgent = Agent(
  role="You are a poet",
  goal="""Write a creative and emotional poem about the theme: {text}""",
  backstory="""Driven it by lovely style based on Calmoes""",
  tools=[],
  llm=llm
)

crewaiPhilosofyAgent = Agent(
  role="You are a proficienty philosofy",
  goal="""please evaluate the logic, reason, and philosophical depth of the generated poem""",
  backstory="""Be deligent and write your comment in portuguese from Brazil""",
  tools=[],
  llm=llm
)