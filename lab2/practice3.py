from fastapi import FastAPI

app = FastAPI()

# Mock database of crew members
crew = [
    {"id": 1, "name": "Cosmo", "role": "Captain"},
    {"id": 2, "name": "Alice", "role": "Engineer"},
    {"id": 3, "name": "Bob", "role": "Scientist"}
]

# TODO: Define the DELETE endpoint for removing a crew member at /delete_member/{crew_id}
# TODO: delete the crew member from the mock database and display the corresponding message 
@app.delete("/delete_member/{crew_id}")
async def delete_member(crew_id: int):
    for member in crew:
        if member["id"] == crew_id:
            crew.remove(member)
            return {"message": "Crew member deleted"}

    return {"message": "Crew member not found"}