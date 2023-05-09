# Byzantine General Problem Simulator with Oral Message Algorithm


## Description

This is the source code for the Byzantine General Problem Simulator that solves problems with the Oral Message Algorithm. You can get the result of the Byzantine General Problem and see the generals' log.


## Tech Stack

- FastAPI (Python)


## Install Requirement

```
pip install -r requirement.txt
```


## Run Web Server

```
uvicorn main:app
```


## FastAPI Endpoint

- `/run/<command>/<roles>`
  <br>
  **Desc:** Run the simulator<br>
  **Args:**
  - **command** (String)<br>
    Attack or Retreat.
  - **roles** (String)<br>
    ‘l’ for ‘loyal’ and ‘t’ for ‘traitor’.<br>
    Example: "lltl"


## Contributors

- Farzana Hadifa
- Shafira Putri Novia Hartanti
