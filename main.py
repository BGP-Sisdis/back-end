from fastapi import FastAPI
from datetime import datetime
from sim_main import execution
from fastapi.middleware.cors import CORSMiddleware
from state import State, client_logs
from dotenv import load_dotenv

import os


load_dotenv()

app = FastAPI()


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

@app.get('/run')
async def stream():
    return {"message": "Hello World"}