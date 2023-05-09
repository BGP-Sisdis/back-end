from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sim_main import execution

import os
import uuid


load_dotenv()

app = FastAPI()
sessions = set()

FE_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

origins = [
    "http://localhost",
    FE_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get('/run/{command}/{roles}')
async def run_simulator(roles: str, command: str):

    session_id = str(uuid.uuid4())
    sessions.add(session_id)

    roles = [True if i == "t" else False for i in roles]

    if len(roles) < 3:
        msg = f"The number of generals not reach the minimum. The minimum number of nodes is 3, but you have {len(roles)} generals."
        raise HTTPException(status_code=400, detail={"msg": msg})
    if len(roles) > 30:
        msg = f"The number of generals exceeds the maximum limit. The maximum number of nodes is 30, but you have {len(roles)} generals."
        raise HTTPException(status_code=400, detail={"msg": msg})
    if command.lower() != "attack" and command.lower() != "retreat":
        msg = "Command not found. Your command is neither 'attack' nor 'retreat'."
        raise HTTPException(status_code=400, detail={"msg": msg})

    generals_action, general_consensus = execution(roles, command.upper(), session_id)

    log_file = open(f"logs/{session_id}.txt", "r")
    logs_lines = log_file.readlines()
    log_file.close()
    logs = []

    for log in logs_lines:
        log = log.replace("\n", "")
        logs.append(log.split("-"))

    os.remove(f"logs/{session_id}.txt")
    sessions.remove(session_id)

    response = {
        "generals_action": generals_action,
        "general_consensus": general_consensus,
        "logs": logs
    }

    return response
