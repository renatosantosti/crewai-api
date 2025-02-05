from crewai import Task
from mycrews.agents import crewaiPoetAgent, crewaiPhilosofyAgent

# CrewAI Tasks
crewaiCreatePoemTask = Task(
  description =  "Create a poem based on theme: {theme}.",
  expected_output="a poem based on given theme",
  agent=crewaiPoetAgent
)  

# CrewAI Tasks
crewaiPoemAnalisysTask = Task(
  description =  "Create a critical analisys of poem",
  expected_output="""return a json {poem: str, critical: str}, 
  'poem': is the entire poem created and 'critical' is the philosofy critical created. 
  Nothing more is expected, only the json content.
  No comment your work, just created the json with required content
  """,
  agent=crewaiPhilosofyAgent
)