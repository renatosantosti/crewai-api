import sys
import os
sys.path.append("./app") # Adiciona o diretório atual ao path
from mycrews.crews import mycrew
from dotenv import load_dotenv
from typing import Union, Optional
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from openai import OpenAI
import uuid
from fastapi.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

# Acessando a variável de ambiente API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verificando se a API_KEY foi carregada com sucesso
if OPENAI_API_KEY:
    print("Chave de OPENAI_API_KEY carregada com sucesso.")
else:
    print("Chave de OPENAI_API_KEY não encontrada no arquivo .env.")
    exit(1)

client = OpenAI(
    api_key= OPENAI_API_KEY,  # This is the default and can be omitted
)

app = FastAPI()

# Modelo de requisição para as tasks
class CrewRequest(BaseModel):
    objective: str
    context: Optional[str] = None
    max_iterations: Optional[int] = 3
    async_execution: Optional[bool] = True

# Modelo de resposta para as tasks
class CrewResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None

# Banco de dados simples para armazenar resultados (simulação)
task_storage = {}

# Função para criar um poema (agente Poeta)
def create_poem(theme: str) -> str:
    prompt = f"You are a poet, write a creative and emotional poem about the theme: {theme}"
    completion  =  client.chat.completions.create(
    messages=[
        {
            "role": "assistant",
            "content": prompt,
        }
    ],
    model="o1-mini",
    )
    return completion.choices[0].message.content.strip()

# Função para avaliar a lógica do poema (agente Filósofo)
def evaluate_poem(poem: str) -> str:
    prompt = f"You are philosofy, please evaluate the logic, reason, and philosophical depth of the following poem, please write your comment in portuguese from Brazil: {poem}"
    completion  =  client.chat.completions.create(
    messages=[
        {
            "role": "assistant",
            "content": prompt,
        }
    ],
    model="gpt-4o",
    )
    return completion.choices[0].message.content.strip()

# Função de background para processar e armazenar resultado de forma assíncrona
def process_task_background(task_id: str, objective: str):
    # Criando o poema (agente Poeta)
    poem = create_poem(objective)
    
    # Avaliando o poema (agente Filósofo)
    evaluation = evaluate_poem(poem)
    
    # Armazenando o resultado
    result = f"Poem: {poem}\nEvaluation: {evaluation}"
    task_storage[task_id] = {"status": "completed", "result": result}

# Função de background para processar e armazenar resultado de forma assíncrona
def process_task_crewai_background(task_id: str, objective: str):   
    # Armazenando o resultado
    result = mycrew.kickoff(inputs={'theme': objective})

    # Accessing the crew output
    print(f"Raw Output: {result.raw}")
    if result.json_dict:
        print(f"JSON Output: {json.dumps(result.json_dict, indent=2)}")
    if result.pydantic:
        print(f"Pydantic Output: {result.pydantic}")
    print(f"Tasks Output: {result.tasks_output}")
    print(f"Token Usage: {result.token_usage}")

    task_storage[task_id] = {"status": "completed", "result": result.raw}

# Função para avaliar a lógica do poema (agente Filósofo)
def evaluate_poem(poem: str) -> str:
    prompt = f"You are philosofy, please evaluate the logic, reason, and philosophical depth of the following poem, please write your comment in portuguese from Brazil: {poem}"
    completion  =  client.chat.completions.create(
    messages=[
        {
            "role": "assistant",
            "content": prompt,
        }
    ],
    model="gpt-4o",
    )
    return completion.choices[0].message.content.strip()

# Rota para consulta de liveness
@app.get("/liveness")
def check_liveness():
    return {"status": "alive"}

# Rota para executar a task com os agentes
@app.post("/open/test", response_model=CrewResponse)
async def execute_task(request: CrewRequest, background_tasks: BackgroundTasks):
    # Geração do ID da task
    task_id = str(uuid.uuid4())
    
    if request.async_execution:
        # Caso a execução seja assíncrona, apenas cria a task e retorna imediatamente
        task_storage[task_id] = {"status": "pending", "result": None}
        background_tasks.add_task(process_task_background, task_id, request.objective)
        return CrewResponse(task_id=task_id, status="pending", result=None)
    else:
        # Caso a execução seja síncrona, processa a task imediatamente
        poem = create_poem(request.objective)
        evaluation = evaluate_poem(poem)
        result = f"Poem: {poem}\nEvaluation: {evaluation}"
        task_storage[task_id] = {"status": "completed", "result": result}
        return CrewResponse(task_id=task_id, status="completed", result=result)

# Rota para consultar o status e resultado de uma task
@app.get("/agents/tasks/{task_id}", response_model=CrewResponse)
async def get_task_result(task_id: str):
    if task_id not in task_storage:
        raise JSONResponse(status_code=404, content={"message": "Task not found"})
    
    task = task_storage[task_id]
    return CrewResponse(task_id=task_id, status=task["status"], result=task["result"])

# Rota para executar a task com os agentes
@app.post("/crewai/test", response_model=CrewResponse)
async def execute_task(request: CrewRequest, background_tasks: BackgroundTasks):
    # Geração do ID da task
    task_id = str(uuid.uuid4())
    
    if request.async_execution:
        # Caso a execução seja assíncrona, apenas cria a task e retorna imediatamente
        task_storage[task_id] = {"status": "pending", "result": None}
        background_tasks.add_task(process_task_crewai_background, task_id, request.objective)
        return CrewResponse(task_id=task_id, status="pending", result=None)
    else:
       # Caso a execução seja síncrona, processa a task imediatamente
       # result = create_crew_poem(request.objective)
        result = mycrew.kickoff(inputs={'theme': request.objective})

        # Accessing the crew output
        print(f"Raw Output: {result.raw}")
        if result.json_dict:
            print(f"JSON Output: {json.dumps(result.json_dict, indent=2)}")
        if result.pydantic:
            print(f"Pydantic Output: {result.pydantic}")
        print(f"Tasks Output: {result.tasks_output}")
        print(f"Token Usage: {result.token_usage}")

        task_storage[task_id] = {"status": "completed", "result": result.raw}
        return CrewResponse(task_id=task_id, status="completed", result=result.raw)
