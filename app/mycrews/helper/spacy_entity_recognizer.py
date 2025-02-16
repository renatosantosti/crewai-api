from typing import List
import spacy
from spacy.util import is_package
from spacy.cli import download

# Avaialble models
models = [{"lang": "pt", "modelName": "pt_core_news_sm"}, {"lang": "en", "modelName": "en_core_web_sm"}]

# Dictionary to store the model according each language
nlp = {}

# check and download model, if it is need
for model in models:
    model_name = model["modelName"]
    lang = model["lang"]
    
    if not is_package(model_name):
        download(model_name)  # Download model, if it is need
    
    nlp[lang] = spacy.load(model_name)  # Load model on dictionary by its language

def spacy_entity_recognizer(text: str, lang: str = "pt", types: List[str] = []) -> List[dict]:
    """
    Extract named entities from the given text based on the specified language.

    This function uses SpaCy to identify named entities in the input text. By default, it processes text in Portuguese.
    If a list of entity types is provided, only the specified entity types will be returned.

    Additionally, it normalizes the entity type "EMAIL_ADDRESS" to "EMAIL" for consistency.

    Args:
        text (str): The input text to analyze and extract named entities from.
        lang (str, optional): The language model to use. Defaults to "pt" (Portuguese).
        types (List[str], optional): A list of entity types to filter results. If empty, all recognized entities are returned.

    Returns:
        List[dict]: A list of extracted entities, each represented as a dictionary with:
            - "value" (str): The extracted entity text.
            - "type" (str): The entity type.

    Raises:
        ValueError: If the specified language model is not available.

    Example:
        >>> spacy_entity_recognizer("My email is test@email.com", lang="pt")
        [{'value': 'test@email.com', 'type': 'EMAIL'}]

        >>> spacy_entity_recognizer("Amazon is a company", lang="pt", types=["ORG"])
        [{'value': 'Amazon', 'type': 'ORG'}]
    """
    
    # Check if the selected language model is available
    if lang not in nlp:
        raise ValueError(f"Language model '{lang}' not available. Available options: {list(nlp.keys())}")

    # Process the text using the corresponding model
    doc = nlp[lang](text)

    # Extract entities from the text
    entities = [{"value": ent.text, "type": ent.label_} for ent in doc.ents]

    # Normalize the entity type "EMAIL_ADDRESS" to "EMAIL" and "PER" to "PERSON"
    for ent in entities:
        if ent["type"] == "EMAIL_ADDRESS":
            ent["type"] = "EMAIL"
        if ent["type"] == "PER":
            ent["type"] = "PERSON"


    # For only shrink spacy to recognize only certain entity types: PERSON, ORG, LOCATION
    ACCEPTED_TYPES = ["PERSON", "ORG", "LOCATION"]
    entities = [ent for ent in entities if ent["type"] in ACCEPTED_TYPES]
    
    # Also, filter entities by type if a type list is provided
    if any(types):
        types_upper = [t.upper() for t in types]
        types_upper.append('FAILED')
        entities = [ent for ent in entities if ent["type"] in types_upper]
  
    return entities
