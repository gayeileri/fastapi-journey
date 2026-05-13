from fastapi import FastAPI

# TODO: Import BaseModel from pydantic
from pydantic import BaseModel

app = FastAPI()

# Mock database of books
books = [
    {"id": 1, "title": "1984", "author": "George Orwell", "year": 1949},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960},
    {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925}
]


# TODO: Define a Pydantic model for the book
# Include:
# - title
# - author
# - year
class Book(BaseModel):
    title: str
    author: str
    year: int

@app.get("/books/{book_id}", response_model=Book)
async def read_book(book_id: int):
# TODO: Define a GET endpoint receiving the id and use the response model
# Use the URL: /books/{book_id}
    # Finding the book in books
    for book in books:
        if book["id"] == book_id:
            return book
    return {"message": "Book not found"}