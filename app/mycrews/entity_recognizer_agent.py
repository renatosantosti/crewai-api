from crewai import Agent
from mycrews.entity_recognizer_tool import entity_recognizer_tool


# Define the agent
EntityRecognizerAgent = Agent(
    role="Named Entity Recognition (NER) Expert",
    goal="{text}",
    backstory=(
        "A leading NLP researcher with deep expertise in natural language processing."
        " You specialize in entity recognition, helping to structure unstructured data."
    ),
    tools=[entity_recognizer_tool],
    verbose=True
)