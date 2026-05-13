# Mini Project 1 – Design Decisions

## Why two files?

I put the models in a separate `models.py` instead of writing everything in `main.py`.
It just felt cleaner. When I was testing things it was easier to find stuff.

## Field types

- `member_id` and `session_id` are `int` because they're just simple IDs, easy to use in URLs too.
- `full_name` and `workout_type` are `str`, names and workout labels are always text.
- `age` and `duration_minutes` are `int` because they're whole numbers, floats don't really make sense here.
- `email` is `EmailStr` from pydantic. I found out this automatically checks if the email looks valid so I used it instead of writing a regex myself.
- `membership_type` is an Enum. I did this so only "Basic", "Premium" or "VIP" are accepted. Otherwise someone could send anything as a string.
- `date` is Python's `date` type. I first used `str` but then changed it because a real date type is better, it won't accept random strings.
- `calories_burned` is `Optional[int]` because not every session will have this info.
- `sessions` is `List[WorkoutSession]` – this is the nested model part. I used `Field(default_factory=list)` because I read that using `= []` directly as a default can cause bugs in Python.

## Validations

I added 5 validation rules total:

1. `age ge=18` – gym shouldn't allow people under 18
2. `duration_minutes gt=0` – a session with 0 minutes doesn't make sense
3. `full_name min_length=2, max_length=50` – just to avoid empty names or weird long inputs
4. `EmailStr` – validates email format automatically
5. `MembershipType` Enum – restricts the value to only the 3 allowed types

## Async and sleep

All endpoints use `async def` and `await asyncio.sleep(1)`.
Since I'm using a Python list as the database, everything is instant. The sleep simulates what would happen with a real database.
The most realistic use is in `GET /members/` and `GET /members/{member_id}` because in a real app, reading from a database takes time. With async, the server can handle other requests while waiting instead of freezing.
