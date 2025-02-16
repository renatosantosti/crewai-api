#importing CrewAI dependencies
from crewai import Crew, Process

#Importing internal resources
from mycrews.tasks import crewaiCreatePoemTask, crewaiPoemAnalisysTask
from mycrews.agents import crewaiPoetAgent, crewaiPhilosofyAgent
from mycrews.entity_recognizer_agent import EntityRecognizerAgent

# Create the Crew
mycrew =  Crew(
  tasks = [crewaiCreatePoemTask, crewaiPoemAnalisysTask],
  agents = [crewaiPoetAgent, crewaiPhilosofyAgent, EntityRecognizerAgent],
  tools = [],
  process =  Process.sequential,
  verbose = True
) 
