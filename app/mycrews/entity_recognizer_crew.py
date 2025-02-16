#importing CrewAI dependencies
from crewai import Crew, Process

#Importing internal resources
from mycrews.entity_recognizer_tool import entity_recognizer_tool
from mycrews.entity_recognizer_task import EntityRecognizerTask
from mycrews.entity_recognizer_agent import EntityRecognizerAgent

# Create the Crew
EntityRecognizerCrew =  Crew(
  tasks = [EntityRecognizerTask],
  agents = [EntityRecognizerAgent],
  tools = [entity_recognizer_tool],
  process =  Process.sequential,
  verbose = True
) 
