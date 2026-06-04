# Mini Project 1 – Design Decisions

## Why two files?

I put the models in a separate `models.py` instead of writing everything in `main.py`.
It felt cleaner and easier to find things when testing.

## Field types

- `id` and `session_id` are `int` because they're just simple IDs, easy to use in URLs too.
- `name` and `workout_type` are `str`, names and workout labels are always text.
- `duration_minutes` is `int` because it's a whole number, floats don't really make sense here.
- `membership_type` is `str`. I thought about using an Enum to restrict it to only "Basic", "Premium" or "VIP" but kept it simple for now. Maybe I'll add validation later.
- `calories_burned` is `Optional[int]` because not every session will have this info.
- `sessions` is `List[WorkoutSession]` – this is the nested model part. I used `= []` as the default so a member can be created without any sessions.

## Validations

I didn't add field validators this time but there are some natural constraints I relied on:

1. `id` and `session_id` are `int` so strings won't be accepted automatically by Pydantic
2. `duration_minutes` is `int` – a negative value wouldn't make sense but I didn't add a constraint yet
3. `Optional[int]` on `calories_burned` means it's fine to leave it out

## Async and sleep

All endpoints use `async def` and `await asyncio.sleep(1)`.
Since I'm using a Python list as the database, everything is instant. The sleep simulates what would happen with a real database.
I think it makes most sense on the GET endpoints because in a real app reading from a database takes time. With async, the server can handle other requests while waiting instead of blocking.
