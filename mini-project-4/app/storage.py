# In-memory storage for polls
polls_db = {}
poll_counter = 0


def create_poll(question: str, options: list) -> dict:
    """Create a new poll and store it in memory."""
    global poll_counter
    poll_counter += 1
    
    poll = {
        "id": poll_counter,
        "question": question,
        "options": [{"id": idx, "text": option, "votes": 0} for idx, option in enumerate(options)]
    }
    polls_db[poll_counter] = poll
    return poll


def get_all_polls() -> list:
    """Get all polls."""
    return list(polls_db.values())


def get_poll(poll_id: int) -> dict:
    """Get a single poll by ID."""
    return polls_db.get(poll_id)


def vote_on_poll(poll_id: int, option_id: int) -> dict:
    """Vote on a poll option."""
    if poll_id not in polls_db:
        return None
    
    poll = polls_db[poll_id]
    # Find the option and increment votes
    for option in poll["options"]:
        if option["id"] == option_id:
            option["votes"] += 1
            return poll
    
    return None


def delete_poll(poll_id: int) -> bool:
    """Delete a poll."""
    if poll_id in polls_db:
        del polls_db[poll_id]
        return True
    return False
