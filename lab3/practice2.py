from fastapi import FastAPI
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
# - title (str)
# - author (str)
# - year (int)
class Book(BaseModel):
    title: str
    author: str
    year: int

# POST endpoint to add a new book receiving Book model
@app.post("/books/")
async def add_book(book: Book):
    # Generating new id
    book_id = max(b["id"] for b in books) + 1 if books else 1
    # TODO: Modify the code to create new_book
    new_book = {
        "id": book_id,
        "title": book.title,
        "author": book.author,
        "year": book.year
    }
    # Adding new book to database
    books.append(new_book)
    # Returning message and new book details
    return {"message": "Book added successfully", "details": new_book}