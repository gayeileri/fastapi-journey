# Architecture Decisions - Real-time Poll System

## 1. Why did you choose to store data in-memory instead of using a database?

For this mini-project, I chose in-memory storage (Python dictionaries) for several key reasons:

**Speed & Simplicity**: In-memory storage provides instant read/write access without the overhead of database queries, network calls, or connection pooling. For a real-time polling system where responsiveness is critical, this was the optimal choice for the prototype phase.

**Real-time Requirements**: The core focus of this project is demonstrating WebSocket functionality and real-time broadcast capabilities. A database would introduce latency that could complicate the real-time updates. With in-memory storage, vote updates are instantaneous and can be broadcast to all connected clients immediately.

**Development Efficiency**: During development and testing, in-memory storage allowed me to iterate quickly without setting up database migrations, managing connections, or dealing with ORM complexities.

**Scalability Path**: For a production system, this architecture can be easily upgraded to use a database (PostgreSQL, MongoDB, etc.) without changing the API contract. The storage layer is completely abstracted in `storage.py`, making it database-agnostic.

**Demo Purpose**: This project is designed to showcase real-time WebSocket capabilities. A simple in-memory store keeps the focus on the WebSocket implementation rather than database configuration.

---

## 2. What happens when two people vote at the same time?

The system handles concurrent votes gracefully through Python's Global Interpreter Lock (GIL) and asynchronous handling:

**Race Condition Prevention**: When two simultaneous votes arrive on the same poll, they are processed sequentially at the Python interpreter level due to the GIL. The `vote_on_poll()` function atomically:
1. Finds the correct option in the poll
2. Increments the vote count
3. Returns the updated poll state

Since these operations happen in sequence (not truly parallel), there's no race condition where votes could be lost.

**Broadcasting Consistency**: After each vote, the Connection Manager broadcasts the updated poll state to ALL connected WebSocket clients. This ensures all browsers see the same vote count, preventing discrepancies.

**Demonstration**: 
- User A and User B are both connected to Poll #1
- User A votes for Python at the same moment User B votes for JavaScript
- Both votes are recorded (Python: 1 vote, JavaScript: 1 vote)
- Both User A and User B instantly see the updated vote counts through WebSocket
- If new clients connect, they receive the current state with both votes counted

**For Production**: In a distributed system with multiple servers, this would require either:
- A distributed lock mechanism (Redis locks, database transactions)
- An event queue (RabbitMQ, Kafka) with a single consumer
- Optimistic concurrency control with versioning

---

## 3. How does the WebSocket real-time broadcast work?

The WebSocket broadcast system consists of three main components:

**Connection Manager (`ConnectionManager` class)**:
- Maintains a dictionary mapping `poll_id` to a set of WebSocket connections
- When a client connects via `/ws/polls/{poll_id}`, it's added to that poll's connection set
- When a vote is cast, the manager broadcasts the updated poll to all connections for that poll
- Automatically removes disconnected clients

**Vote Flow**:
1. Client votes via either REST API (`/polls/{poll_id}/vote`) or WebSocket message
2. Server updates the poll data in memory
3. Server triggers `manager.broadcast(poll_id, updated_poll)`
4. Manager iterates through all WebSocket connections for that poll
5. Each connected client receives the update in real-time
6. JavaScript on client side immediately updates the vote count in the UI

**Key Implementation Details**:
```
REST API Vote → vote_on_poll() → manager.broadcast_poll_update()
WebSocket Vote → vote_on_poll() → manager.broadcast()
```

Both paths lead to the same broadcast result, ensuring consistency.

**Why No Polling**: 
The system uses true WebSocket connections, NOT polling (setInterval). This means:
- Zero latency: Updates arrive instantly
- Zero unnecessary requests: Only real events are sent
- Reduced server load: No constant "check for updates" requests
- True bidirectional communication

---

## 4. How does the system ensure all users see the same vote count?

The system guarantees consistency through several mechanisms:

**Single Source of Truth**:
- All poll data is stored in a single Python dictionary (`polls_db`) on the server
- All users query this same source for poll state
- No client-side state divergence

**Real-time Synchronization**:
- When a vote is cast, the server immediately broadcasts the NEW state to all connected clients
- Clients don't calculate or predict new counts; they receive authoritative data from the server
- Every client gets the same data in the same update

**Connection Handling**:
- New clients connecting to a poll receive the current poll state immediately
- They see the exact vote count at that moment
- WebSocket messages confirm receipt and synchronization

**Consistency Guarantees**:
1. **Strong Consistency**: All clients see the latest vote count because they receive updates directly from the authoritative server
2. **Atomic Updates**: Each vote increments the count atomically before broadcasting
3. **Sequential Processing**: Due to Python's GIL, votes are processed one at a time, preventing count inconsistencies

**Example Scenario**:
- Poll has 5 votes total (Python: 2, JavaScript: 3)
- User A opens browser: sees Python: 2, JavaScript: 3
- User B votes for Python at exact moment User C votes for JavaScript
- Server processes both votes: Python becomes 3, JavaScript becomes 4
- Server broadcasts new state to both User A and User B
- All three users immediately see the same: Python: 3, JavaScript: 4

**Testing Verification**:
The demonstration with two open browser tabs showed this consistency in action. Votes cast on one tab were instantly visible on the other tab, confirming the real-time broadcast system maintains data consistency across all connected clients.

---

## Technical Stack

- **Framework**: FastAPI (async Python web framework)
- **WebSocket**: Built-in FastAPI WebSocket support via Starlette
- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks needed)
- **Storage**: In-memory Python dictionary
- **Deployment**: Docker & Docker Compose
- **Server**: Uvicorn (ASGI server)

## Conclusion

This architecture demonstrates the core principles of real-time systems: low latency communication via WebSocket, centralized data management, and consistent state synchronization across multiple clients. The design prioritizes responsiveness and demonstrates modern web development practices for building real-time applications.
