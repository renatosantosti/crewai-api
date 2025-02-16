import spacy
from crewai.tools import tool
from app.mycrews.helper.spacy_entity_recognizer import spacy_entity_recognizer


@tool("entity_recognizer_tool")
def entity_recognizer_tool(text: str, result_as_answer=True) -> str:
    """Extract named entities from the given text and return them in a structured format."""
    entities = spacy_entity_recognizer(text)   
    return entities
