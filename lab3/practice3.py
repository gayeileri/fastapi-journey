from fastapi import FastAPI

app = FastAPI()
from pydantic import BaseModel
# Mock database of crew members
crew = [
    {"id": 1, "name": "Cosmo", "role": "Captain", "experience": 10, "specialty": "Leadership"},
    {"id": 2, "name": "Alice", "role": "Engineer", "experience": 8, "specialty": "Mechanical"},
    {"id": 3, "name": "Bob", "role": "Scientist", "experience": 5, "specialty": "Biology"}
]


# TODO: Define a Pydantic model for the crew member with:
# - name
# - role
# - experience
# - specialty
class CrewMember(BaseModel):
    name: str
    role: str
    experience: int
    specialty: str


# TODO: Define a POST endpoint receiving a crew member model
# Use the code provided in the description to handle the database and response
@app.post("/crew/")
async def add_crew_member(member: CrewMember):
    member_id = max(c["id"] for c in crew) + 1 if crew else 1

    new_member = {
        "id": member_id,
        "name": member.name,
        "role": member.role,
        "experience": member.experience,
        "specialty": member.specialty
    }

    crew.append(new_member)
    return {"message": "Crew member added successfully", "details": new_member}