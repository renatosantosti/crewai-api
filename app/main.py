from http.client import HTTPException
import json
import re
import sys
import os
from typing import List, Union, Optional
import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from openai import OpenAI

# Add the current directory to the path
sys.path.append("./app")

from app.mycrews.helper.spacy_entity_recognizer import spacy_entity_recognizer
from app.mycrews.helper.commons import DateEntityEnum, NumericEntityEnum, TextEntityEnum, WebEntityEnum
from mycrews.crews import mycrew
from mycrews.entity_recognizer_crew import EntityRecognizerCrew
from mycrews.entity_recognizer_tool import entity_recognizer_tool

# Load environment variables from .env file
load_dotenv()

# Access the OPENAI_API_KEY environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check if the API_KEY was successfully loaded
if OPENAI_API_KEY:
    print("OPENAI_API_KEY successfully loaded.")
else:
    print("OPENAI_API_KEY not found in the .env file.")
    exit(1)

client = OpenAI(
    api_key=OPENAI_API_KEY,  # This is the default and can be omitted
)

app = FastAPI(
    title="Entity Recognition and CrewAI API",
    description="API for entity recognition using Spacy and CrewAI agents.",
    version="1.0.0",
)

# Request model for tasks
class CrewRequest(BaseModel):
    objective: str
    context: Optional[str] = None
    max_iterations: Optional[int] = 3
    async_execution: Optional[bool] = True

# Response model for tasks
class CrewResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None

# Simple database to store results (simulation)
task_storage = {}

# Function to create a poem (Poet agent)
def create_poem(theme: str) -> str:
    prompt = f"You are a poet, write a creative and emotional poem about the theme: {theme}"
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "assistant",
                "content": prompt,
            }
        ],
        model="o1-mini",
    )
    return completion.choices[0].message.content.strip()

# Function to evaluate the logic of the poem (Philosopher agent)
def evaluate_poem(poem: str) -> str:
    prompt = f"You are a philosopher, please evaluate the logic, reason, and philosophical depth of the following poem. Write your comment in Brazilian Portuguese: {poem}"
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "assistant",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )
    return completion.choices[0].message.content.strip()

# Background function to process and store the result asynchronously
def process_task_background(task_id: str, objective: str):
    poem = create_poem(objective)
    evaluation = evaluate_poem(poem)
    result = f"Poem: {poem}\nEvaluation: {evaluation}"
    task_storage[task_id] = {"status": "completed", "result": result}

# Background function to process and store the result of the EntityRecognizerCrew asynchronously
def process_task_crewairec_background(task_id: str, fulltext: str):
    try:
        result = EntityRecognizerCrew.kickoff(inputs={'text': fulltext})
        print(f"Raw Output: {result.raw}")
        if result.json_dict:
            print(f"JSON Output: {json.dumps(result.json_dict, indent=2)}")
        if result.pydantic:
            print(f"Pydantic Output: {result.pydantic}")
        print(f"Tasks Output: {result.tasks_output}")
        print(f"Token Usage: {result.token_usage}")
        json_result = json.loads(result.raw)  # Convert raw string to JSON
        task_storage[task_id] = {"status": "completed", "result": json_result}
    except json.JSONDecodeError as json_error:
        raise HTTPException(status_code=500, detail=f"Error to parse result to json: {str(json_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Background function to process and store the result of the CrewAI task asynchronously
def process_task_crewai_background(task_id: str, theme: str):
    try:
        print('mycrew started')
        result = mycrew.kickoff(inputs={'text': theme})
        task_storage[task_id] = {"status": "completed", "result": result.raw}
    except Exception as e:
        task_storage[task_id] = {"status": "failed", "result": str(e)}

# Route to check liveness
@app.get("/liveness", summary="Liveness Check", description="Endpoint to check if the API is alive.")
def check_liveness():
    return {"status": "alive"}

# Route to execute a task with agents
@app.post("/open/test", response_model=CrewResponse, summary="Execute Task with Agents", description="Endpoint to execute a task using agents to create and evaluate a poem.")
async def execute_task(request: CrewRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    if request.async_execution:
        task_storage[task_id] = {"status": "pending", "result": None}
        background_tasks.add_task(process_task_background, task_id, request.objective)
        return CrewResponse(task_id=task_id, status="pending", result=None)
    else:
        poem = create_poem(request.objective)
        evaluation = evaluate_poem(poem)
        result = f"Poem: {poem}\nEvaluation: {evaluation}"
        task_storage[task_id] = {"status": "completed", "result": result}
        return CrewResponse(task_id=task_id, status="completed", result=result)

# Route to get the status and result of a task
@app.get("/agents/tasks/{task_id}", response_model=CrewResponse, summary="Get Task Result", description="Endpoint to get the status and result of a specific task.")
async def get_task_result(task_id: str):
    if task_id not in task_storage:
        return JSONResponse(status_code=404, content={"message": "Task not found"})
    task = task_storage[task_id]
    return CrewResponse(task_id=task_id, status=task["status"], result=task["result"])

# Route to execute a task with CrewAI
@app.post("/crewai/test", response_model=CrewResponse, summary="Execute CrewAI Task", description="Endpoint to execute a task with CrewAI.")
async def execute_task(request: CrewRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    if request.async_execution:
        task_storage[task_id] = {"status": "pending", "result": None}
        background_tasks.add_task(process_task_crewai_background, task_id, request.objective)
        return CrewResponse(task_id=task_id, status="pending", result=None)
    else:
        print('Started mycrew for testing')
        result = mycrew.kickoff(inputs={'text': request.objective})
        print(f"Raw Output: {result.raw}")
        if result.json_dict:
            print(f"JSON Output: {json.dumps(result.json_dict, indent=2)}")
        if result.pydantic:
            print(f"Pydantic Output: {result.pydantic}")
        print(f"Tasks Output: {result.tasks_output}")
        print(f"Token Usage: {result.token_usage}")
        task_storage[task_id] = {"status": "completed", "result": result.raw}
        return CrewResponse(task_id=task_id, status="completed", result=result.raw)

# Define request and response models for EntityRecognizerCrew
class EntityRecognizerCrewRequest(BaseModel):
    fulltext: str
    async_execution: bool = False

class EntityRecognizerCrewResponse(BaseModel):
    task_id: str
    status: str
    result: List[dict] | None = None

# Route to access EntityRecognizer crew
@app.post("/crewai/entityRecognizer", response_model=EntityRecognizerCrewResponse, summary="Entity Recognizer Crew", description="Endpoint to recognize entities using EntityRecognizerCrew.")
async def execute_task(request: EntityRecognizerCrewRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    if request.async_execution:
        task_storage[task_id] = {"status": "pending", "result": None}
        background_tasks.add_task(process_task_crewairec_background, task_id, request.fulltext)
        return EntityRecognizerCrewResponse(task_id=task_id, status="pending", result=None)
    else:
        try:
            print('EntityRecognizerCrew started')
            result = EntityRecognizerCrew.kickoff(inputs={'text': request.fulltext})
            print(f"Raw Output: {result.raw}")
            print(f"json_dict: {result.json_dict}")
            if result.json_dict:
                print(f"JSON Output: {json.dumps(result.json_dict, indent=2)}")
                task_storage[task_id] = {"status": "completed", "result": result.json_dict.entities}
                return EntityRecognizerCrewResponse(task_id=task_id, status="completed", result=result.json_dict.entities)
            if result.pydantic:
                print(f"Pydantic Output: {result.pydantic}")
                
            print(f"Tasks Output: {result.tasks_output}")
            print(f"Token Usage: {result.token_usage}")        

            # If raw contains extra text, extract the first valid JSON block
            match = re.search(r"\{.*\}", result.raw, re.DOTALL)  # Extract JSON from text
            if match:
                json_result = json.loads(match.group())  # Convert to JSON
                return EntityRecognizerCrewResponse(task_id=task_id, status="completed", result=json_result["entities"])
            else:
                raise ValueError("No valid JSON found in CrewAI output.")

        except json.JSONDecodeError as json_error:
            raise HTTPException(status_code=500, detail=f"Error to parse result to json: {str(json_error)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
# A simple Spacy entity recognizer is provided to avoid paid NLP services
@app.post("/spacy/entityRecognizer", response_model=EntityRecognizerCrewResponse, summary="Spacy Entity Recognizer", description="Endpoint to recognize entities using Spacy.")
async def execute_task(request: EntityRecognizerCrewRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    if request.async_execution:
        task_storage[task_id] = {"status": "pending", "result": None}
        background_tasks.add_task(spacy_entity_recognizer, task_id, request.fulltext)
        return EntityRecognizerCrewResponse(task_id=task_id, status="pending", result=None)
    else:
        result = spacy_entity_recognizer(request.fulltext, "pt", [])
        print(f"Raw Output: {result}")
        print(f"Tasks Output: {len(result)}")
        print("Token Usage: 0")
        task_storage[task_id] = {"status": "completed", "result": result}
        return EntityRecognizerCrewResponse(task_id=task_id, status="completed", result=result)

# Request model for general entity recognition
class EntityRecognizerRequest(BaseModel):
    fulltext: str  # Text to be checked
    entities: List[str]  # List of entities to be analyzed
    lang: str = "pt"  # Default language (Portuguese)
    async_execution: bool = False  # Default to false

# Response model for general entity recognition
class EntityRecognizerResponse(BaseModel):
    entities: List[dict] | None  # List of extracted entities

# API route to recognize named entities
@app.post("/general/entityRecognizer", response_model=EntityRecognizerResponse, summary="General Entity Recognizer", description="Endpoint to recognize entities using Spacy based on specified entity types.")
async def entity_recognizer(request: EntityRecognizerRequest):
    all_entities = []
    if len(request.entities) > 0:
        request.entities.append("FAILED")
        text_filter = [entity for entity in request.entities if entity in {e.value for e in TextEntityEnum}]
        if any(text_filter):
            all_entities.extend(spacy_entity_recognizer(request.fulltext, request.lang, text_filter))
    else:
        all_entities.extend(spacy_entity_recognizer(request.fulltext, request.lang, []))
    return {"entities": all_entities}

