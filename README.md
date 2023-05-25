# Byzantine General Problem Simulator with Oral Message Algorithm


## Description

This is the source code for Server-Side Application of Byzantine General Problem Simulator that solves problems with the Oral Message Algorithm. You can get the result of the Byzantine General Problem and see the generals' log.


## Tech Stack

- FastAPI (Python)


## Install Requirement

```
pip install -r requirement.txt
```


## Run Server-Side Application

```
uvicorn main:app
```
This command will run the application. Open [http://localhost:8000](http://localhost:8000) in browser to view the application.

## FastAPI Endpoint

- `/run/<command>/<roles>`
  <br>
  **Desc:** Run the simulator<br>
  **Args:**
  - **command** (String)<br>
   'attack' or 'retreat'.
  - **roles** (String)<br>
    ‘l’ for ‘loyal’ and ‘t’ for ‘traitor’.<br>
    Example: "lltl"


## Link

Client-Side Application Source Code: [https://github.com/BGP-Sisdis/front-end](https://github.com/BGP-Sisdis/front-end).


## Contributors

- Farzana Hadifa
- Shafira Putri Novia Hartanti
