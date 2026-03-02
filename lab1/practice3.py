# ============================================================
# Practice 3 — Defining the Root Endpoint
# ============================================================
# In this practice you will:
#   1. Import FastAPI and create an app instance
#   2. Define a GET endpoint at the root path "/"
#   3. Return a JSON welcome message
#
# To run:
#   uvicorn practice3:app --port 8000 --reload
#
# Then open your browser at: http://127.0.0.1:8000/
#
# Expected response:
#   {"message": "Greetings from your FastAPI spaceship!"}
# ============================================================


# TODO: Import FastAPI from fastapi
from fastapi import FastAPI

# TODO: Initialize a FastAPI app instance
app = FastAPI()

# TODO: Define a root endpoint using @app.get("/")
#       The function should return:
#       {"message": "Greetings from your FastAPI spaceship!"}
@app.get("/")
def root():
    return {"message": "Greetings from your FastAPI spaceship!"}
    
