from crewai import Task
from mycrews.entity_recognizer_agent import EntityRecognizerAgent
from mycrews.entity_recognizer_tool import entity_recognizer_tool

# Define the task
EntityRecognizerTask = Task(
    description=(
        "Extract named entities (like names, locations, organizations, and dates) from the given text: {text}."
        " The output MUST be a valid JSON object"
        " Do NOT add extra text, explanations, or Markdown formatting."
    ),
    expected_output="{ \"entities\": [ { \"text\": \"Elon Musk\", \"type\": \"PERSON\" }, { \"text\": \"SpaceX\", \"type\": \"ORG\" } ] }",
    agent=EntityRecognizerAgent,
    tools=[entity_recognizer_tool]
)