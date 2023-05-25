from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sim_main import execution

import os
import re
import uuid


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = set()


@app.get("/")
async def root():
    return {"message": "Hello! This BGP Simulator with Oral Messages. To run simulator use '/run/{command}/{roles}'."}

@app.get('/run/{command}/{roles}')
async def run_simulator(command: str, roles: str):
    roles_pattern = re.compile("^([lt])+$")

    session_id = str(uuid.uuid4())
    sessions.add(session_id)

    if command.lower() != "attack" and command.lower() != "retreat":
        msg = "Command not found. Acceptable commands are 'attack' or 'retreat'."
        raise HTTPException(status_code=422, detail={"msg": msg})
    if bool(roles_pattern.match(roles.lower())) == False:
        msg = "The roles pattern doesn't match. Roles is a combination of 'l' and 't' characters."
        raise HTTPException(status_code=422, detail={"msg": msg})

    roles = [True if i == "t" else False for i in roles.lower()]

    if len(roles) < 3:
        msg = f"The number of generals not reach the minimum. The minimum number of nodes is 3, but you have {len(roles)} generals."
        raise HTTPException(status_code=422, detail={"msg": msg})
    if len(roles) > 30:
        msg = f"The number of generals exceeds the maximum limit. The maximum number of nodes is 30, but you have {len(roles)} generals."
        raise HTTPException(status_code=422, detail={"msg": msg})

    # Run simulator
    generals_action, general_consensus = execution(roles, command.upper(), session_id)

    for i in range(len(roles)):
        if roles[i]:
            general_name = "Supreme General" if i == 0 else f"General {i}"
            generals_action.append(f"{general_name}: NO ACTION (TRAITOR)")

    # Sorting general action
    generals_action.sort()
    last_element = generals_action.pop()
    generals_action.insert(0, last_element)

    logs = get_logs(session_id)
    sessions.remove(session_id)

    response = {
        "generals_action": generals_action,
        "general_consensus": general_consensus,
        "logs": logs
    }

    return response

def get_logs(session_id):
    log_file = open(f"logs/{session_id}.txt", "r")
    logs_lines = log_file.readlines()
    log_file.close()
    logs = []

    for log in logs_lines:
        log = log.replace("\n", "")
        log = log.split("-")
        logs.append({"time": log[0], "node": log[1], "step":log[2], "message": log[3]})

    os.remove(f"logs/{session_id}.txt")

    return logs
