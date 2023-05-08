from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
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
    # command: "ATTACK" or "RETREAT"
    # roles example: "ltltltltlt"

    roles = [True if i == "t" else False for i in roles]
    session_id = str(uuid.uuid4())
    sessions.add(session_id)

    result = execution(roles, command.upper(), session_id)
    log_file = open(f"logs/{session_id}.txt", "r")
    logs = log_file.readlines()
    log_file.close()
    os.remove(f"logs/{session_id}.txt")
    sessions.remove(session_id)

    response = {
        "result": result,
        "logs": logs
    }
    return response
