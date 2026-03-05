from fastapi import FastAPI, Request

app = FastAPI()

# Mock database of crew members
crew = [
    {"id": 1, "name": "Cosmo", "role": "Captain"},
    {"id": 2, "name": "Alice", "role": "Engineer"},
    {"id": 3, "name": "Bob", "role": "Scientist"}
]

# TODO: Define an endpoint to update existing crew members using PUT method
# - Use the @app.put decorator
# - Set the URL to /update_crew/{crew_id}
# - Parse the incoming JSON request body to get the new name and role
# - Find the crew member and update the details
# - Return the updated crew member details
# - Return a "Crew member not found" message if the crew member does not exist
@app.put("/update_crew/{crew_id}")
async def update_crew(crew_id: int, request: Request):
    data = await request.json()

    name = data["name"]
    role = data["role"]

    for member in crew:
        if member["id"] == crew_id:
            member["name"] = name
            member["role"] = role
            return member

    return {"message": "Crew member not found"}
