# Real-time Poll System 🗳️

A modern, real-time polling application built with FastAPI and WebSocket. Vote on polls instantly with live updates across all connected users.

## Features

✅ **REST API** - Create and manage polls with standard HTTP endpoints
✅ **WebSocket** - Real-time vote updates without page refresh
✅ **In-Memory Storage** - Fast, responsive data handling
✅ **Beautiful UI** - Modern, responsive frontend with gradient design
✅ **Docker Support** - Easy deployment with Docker Compose
✅ **Concurrent Users** - Multiple users can vote simultaneously

## Project Structure

```
mini-project-4/
├── app/
│   ├── main.py                 # FastAPI application & routes
│   ├── models.py               # Pydantic data models
│   ├── storage.py              # In-memory data storage
│   ├── connection_manager.py    # WebSocket connection management
│   └── __init__.py
├── screenshots/                # Project documentation screenshots
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (in .gitignore)
├── .gitignore                  # Git ignore patterns
├── DECISIONS.md                # Architecture & design decisions
└── README.md                   # This file
```

## Quick Start

### Local Development

1. **Clone and navigate to the project**:
   ```bash
   cd fastapi-journey/mini-project-4
   ```

2. **Create and activate virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Access the application**:
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up
   ```

2. **Access the application**:
   - Frontend: http://localhost:8000
   - The application is now running in a containerized environment

3. **Stop the container**:
   ```bash
   docker-compose down
   ```

## API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/polls` | Create a new poll |
| GET | `/polls` | List all polls |
| GET | `/polls/{poll_id}` | Get a specific poll |
| POST | `/polls/{poll_id}/vote` | Vote on a poll |
| DELETE | `/polls/{poll_id}` | Delete a poll |
| GET | `/health` | Health check |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws/polls/{poll_id}` | Connect to real-time poll updates |

#### WebSocket Messages

**Vote Message**:
```json
{
  "type": "vote",
  "option_id": 0
}
```

**Poll State Update**:
```json
{
  "type": "poll_update",
  "data": {
    "id": 1,
    "question": "What is your favorite language?",
    "options": [
      {"id": 0, "text": "Python", "votes": 5},
      {"id": 1, "text": "JavaScript", "votes": 3}
    ]
  }
}
```

## Example Usage

### Create a Poll

```bash
curl -X POST http://localhost:8000/polls \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is your favorite programming language?",
    "options": ["Python", "JavaScript", "Go", "Rust"]
  }'
```

**Response**:
```json
{
  "id": 1,
  "question": "What is your favorite programming language?",
  "options": [
    {"id": 0, "text": "Python", "votes": 0},
    {"id": 1, "text": "JavaScript", "votes": 0},
    {"id": 2, "text": "Go", "votes": 0},
    {"id": 3, "text": "Rust", "votes": 0}
  ]
}
```

### Vote on a Poll

```bash
curl -X POST http://localhost:8000/polls/1/vote \
  -H "Content-Type: application/json" \
  -d '{"option_id": 0}'
```

### Get All Polls

```bash
curl http://localhost:8000/polls
```

## Technology Stack

- **Backend**: FastAPI 0.136+
- **Server**: Uvicorn
- **WebSocket**: Starlette (FastAPI's foundation)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Containerization**: Docker & Docker Compose
- **Python**: 3.11+

## Architecture Highlights

### Real-time Communication
- **WebSocket Protocol**: True bidirectional communication
- **Connection Manager**: Manages all active client connections per poll
- **Broadcast Mechanism**: Updates all connected clients instantly

### Data Management
- **In-Memory Storage**: Fast read/write for real-time performance
- **Dictionary-based**: Simple, efficient data structure
- **Atomic Operations**: Vote counting is thread-safe

### Scalability
- **Stateless Design**: Can be extended to multiple servers with a message queue
- **Modular Architecture**: Storage layer is abstraction-ready for database migration

## Design Decisions

See [DECISIONS.md](DECISIONS.md) for detailed explanations of:
1. Why in-memory storage instead of a database?
2. How does the system handle concurrent votes?
3. How does WebSocket real-time broadcast work?
4. How does the system ensure all users see the same vote count?

## Testing the Real-time Features

1. Open the application in two browser windows/tabs
2. Create a new poll in one tab
3. The poll appears instantly in the other tab
4. Vote in one tab
5. Watch the vote count update in real-time in the other tab (no page refresh needed!)

## Deployment

The application is fully containerized and can be deployed to:
- **Docker**: Use `docker-compose up`
- **Kubernetes**: Convert Docker image to K8s manifests
- **Cloud Platforms**: Deploy Docker image to AWS ECS, Google Cloud Run, Azure Container Instances, etc.

## Development Notes

- The `.env` file is excluded from version control for security
- All poll data is lost when the application restarts (in-memory storage)
- For production, consider adding persistent storage (PostgreSQL, MongoDB)
- The application is single-threaded (due to Python GIL), suitable for I/O-bound operations

## Future Enhancements

- [ ] Persistent database storage
- [ ] User authentication
- [ ] Poll expiration timestamps
- [ ] Vote history/analytics
- [ ] Multiple choice polls
- [ ] Poll sharing/invitations
- [ ] Real-time voting graphs
- [ ] Rate limiting
- [ ] Admin dashboard

## License

This project is part of the FastAPI Journey learning series.

---

**Created**: May 6, 2026
**Status**: Complete ✅
