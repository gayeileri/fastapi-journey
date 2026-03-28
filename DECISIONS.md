# DECISIONS.md

## 1. What is an ODM and why do we use Beanie instead of writing raw MongoDB queries?

An ODM stands for Object Document Mapper. It basically maps Python objects to MongoDB documents so we don't have to write raw queries every time we want to interact with the database.

Without an ODM, we would have to write things like:

```python
collection.find_one({"_id": ObjectId("...")})
```

and then manually convert the result into a Python object and validate each field ourselves. That gets repetitive and easy to mess up.

With Beanie, we just do:

```python
await Event.get(id)
```

and it handles everything for us. Beanie also uses Pydantic under the hood, so data validation is automatic. If someone sends the wrong type for a field, it catches the error before anything gets saved to the database. Also, Beanie is fully async, which works great with FastAPI.

---

## 2. What is the role of the Database class — why wrap Beanie methods inside it instead of calling them directly in routes?

The Database class acts like a middle layer between the routes and the database. Routes just say what they want to do (like "save this event") and the Database class handles how it actually gets done.

If we called Beanie directly in the routes, we would have to repeat the same error-checking logic everywhere. For example, every time we do a `get`, we would need to check if the document exists and return `False` or raise an error. By putting that logic in the Database class, we only write it once.

Another reason is that if we ever switch to a different database, we only need to update the Database class. The routes stay the same. This makes the code cleaner and easier to maintain.

---

## 3. What happens if initialize_database() is not called on startup? What would break and why?

If we forget to call `initialize_database()`, the app will start without any errors but will crash as soon as the first database request comes in.

The reason is that Beanie needs `init_beanie()` to be called before it can do anything. That function connects to MongoDB and links each Document class to its collection. Without it, Beanie doesn't know where to send queries, so it throws a `CollectionWasNotInitialized` error.

In short:
- No connection to MongoDB is opened
- The `Event` and `User` models are not linked to any collection
- Every route that touches the database will crash

---

## 4. What is the difference between the Event document and the EventUpdate model, and why are they two separate classes?

`Event` is a Beanie Document, meaning it represents what actually gets stored in MongoDB. When creating a new event, all fields are required. You can't save an event with missing information.

`EventUpdate` is a regular Pydantic model where all fields are Optional. This is because when updating, the user might only want to change one or two fields. If we used the `Event` model for updates too, the user would have to send all fields every time, which doesn't make sense.

Also, in the `update` method inside the Database class, we filter out any `None` values before sending the update to MongoDB. This way, only the fields the user actually sent will be changed.

So basically:
- `Event` → used for creating, all fields required, has a database ID
- `EventUpdate` → used for updating, all fields optional, no database ID

Having two separate classes keeps things clear and prevents bugs like accidentally overwriting data with `None`.
