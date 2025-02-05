#importing CrewAI dependencies
from crewai import Crew, Process

#Importing internal resources
from mycrews.tasks import crewaiCreatePoemTask, crewaiPoemAnalisysTask
from mycrews.agents import crewaiPoetAgent, crewaiPhilosofyAgent

# Create the Crew
mycrew =  Crew(
  tasks = [crewaiCreatePoemTask, crewaiPoemAnalisysTask],
  agents = [crewaiPoetAgent, crewaiPhilosofyAgent],
  tools = [],
  process =  Process.sequential,
  verbose = True
) 
