from typing import Any, List, Optional

import beanie
import motor.motor_asyncio
from beanie import PydanticObjectId
from pydantic_settings import BaseSettings


# reads DATABASE_URL from the .env file
class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None

    model_config = {"env_file": ".env"}


# this class wraps all the beanie calls so we don't call them directly in routes
# the professor asked us to do it this way
class Database:
    def __init__(self, model):
        self.model = model

    # save a new document
    async def save(self, document) -> None:
        await document.create()

    # get one document by id
    async def get(self, id: PydanticObjectId) -> Any:
        doc = await self.model.get(id)
        if not doc:
            return False
        return doc

    # get all documents
    async def get_all(self) -> List[Any]:
        docs = await self.model.find_all().to_list()
        return docs

    # update a document - we skip None values so we don't overwrite existing data
    async def update(self, id: PydanticObjectId, body: dict) -> Any:
        doc = await self.get(id)
        if not doc:
            return False
        filtered = {k: v for k, v in body.items() if v is not None}
        await doc.update({"$set": filtered})
        return doc

    # delete a document
    async def delete(self, id: PydanticObjectId) -> bool:
        doc = await self.get(id)
        if not doc:
            return False
        await doc.delete()
        return True


# this function is called when the app starts
async def initialize_database():
    from models.events import Event
    from models.users import User

    settings = Settings()
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL)

    await beanie.init_beanie(
        database=client.get_default_database(),
        document_models=[Event, User],
    )
