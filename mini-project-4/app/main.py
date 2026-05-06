from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
from typing import List
import logging

from app.models import PollCreate, Vote, PollResponse
from app.storage import create_poll, get_all_polls, get_poll, vote_on_poll, delete_poll
from app.connection_manager import ConnectionManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Poll API", description="A real-time polling API with WebSocket", version="1.0.0")

# WebSocket Connection Manager
manager = ConnectionManager()

# ==================== REST API ENDPOINTS ====================

@app.post("/polls", response_model=PollResponse, tags=["Polls"])
async def create_new_poll(poll: PollCreate):
    """Create a new poll with multiple options."""
    try:
        new_poll = create_poll(poll.question, poll.options)
        return new_poll
    except Exception as e:
        logger.error(f"Error creating poll: {e}")
        raise HTTPException(status_code=500, detail="Error creating poll")


@app.get("/polls", response_model=List[PollResponse], tags=["Polls"])
async def list_all_polls():
    """Get all polls."""
    return get_all_polls()


@app.get("/polls/{poll_id}", response_model=PollResponse, tags=["Polls"])
async def get_poll_by_id(poll_id: int):
    """Get a specific poll by ID."""
    poll = get_poll(poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll


@app.post("/polls/{poll_id}/vote", response_model=PollResponse, tags=["Polls"])
async def vote_on_option(poll_id: int, vote: Vote):
    """Vote on a poll option."""
    poll = vote_on_poll(poll_id, vote.option_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll or option not found")
    
    # Broadcast the updated poll to all connected WebSocket clients
    await manager.broadcast_poll_update(poll)
    return poll


@app.delete("/polls/{poll_id}", tags=["Polls"])
async def delete_poll_endpoint(poll_id: int):
    """Delete a poll."""
    if not delete_poll(poll_id):
        raise HTTPException(status_code=404, detail="Poll not found")
    return {"message": "Poll deleted successfully"}


# ==================== WEBSOCKET ENDPOINT ====================

@app.websocket("/ws/polls/{poll_id}")
async def websocket_endpoint(websocket: WebSocket, poll_id: int):
    """WebSocket endpoint for real-time poll updates."""
    # Check if poll exists
    poll = get_poll(poll_id)
    if not poll:
        await websocket.close(code=4004, reason="Poll not found")
        return
    
    # Accept the connection
    await manager.connect(websocket, poll_id)
    
    try:
        # Send current poll state to the newly connected client
        await websocket.send_json({
            "type": "poll_state",
            "data": poll
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "vote":
                option_id = message.get("option_id")
                updated_poll = vote_on_poll(poll_id, option_id)
                if updated_poll:
                    # Broadcast to all connected clients
                    await manager.broadcast(poll_id, {
                        "type": "poll_update",
                        "data": updated_poll
                    })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, poll_id)
        logger.info(f"Client disconnected from poll {poll_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, poll_id)


# ==================== FRONTEND ====================

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def get_frontend():
    """Serve the polling frontend."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-time Poll System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: white;
                margin-bottom: 30px;
                text-align: center;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .card {
                background: white;
                border-radius: 10px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #333;
            }
            input, textarea, button {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 1em;
                font-family: inherit;
            }
            textarea {
                resize: vertical;
                min-height: 60px;
            }
            input:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 5px rgba(102, 126, 234, 0.5);
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: 600;
                transition: background 0.3s;
                margin-top: 10px;
            }
            button:hover {
                background: #5568d3;
            }
            button:active {
                transform: scale(0.98);
            }
            .poll-item {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }
            .poll-question {
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }
            .poll-id {
                font-size: 0.85em;
                color: #999;
                margin-bottom: 10px;
            }
            .option {
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .option input[type="radio"] {
                width: auto;
                margin: 0;
            }
            .option label {
                margin: 0;
                flex: 1;
                cursor: pointer;
                display: flex;
                align-items: center;
            }
            .vote-count {
                background: #e8f0ff;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: 600;
                color: #667eea;
                font-size: 0.9em;
            }
            .btn-group {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            .btn-group button {
                flex: 1;
                padding: 10px;
            }
            .btn-secondary {
                background: #6c757d;
            }
            .btn-secondary:hover {
                background: #5a6268;
            }
            .status {
                padding: 10px 15px;
                border-radius: 5px;
                margin-bottom: 15px;
                font-weight: 500;
            }
            .status.connected {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.disconnected {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status.connecting {
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }
            #polls-container {
                margin-top: 30px;
            }
            .loading {
                text-align: center;
                color: #999;
                padding: 20px;
                font-style: italic;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🗳️ Real-time Poll System</h1>
            
            <div class="card">
                <h2>Create New Poll</h2>
                <div class="form-group">
                    <label>Poll Question</label>
                    <textarea id="question" placeholder="What is your question?"></textarea>
                </div>
                <div class="form-group">
                    <label>Options (one per line)</label>
                    <textarea id="options" placeholder="Option 1&#10;Option 2&#10;Option 3"></textarea>
                </div>
                <button onclick="createPoll()">Create Poll</button>
                <div id="error-message" class="error" style="display: none;"></div>
            </div>
            
            <div id="polls-container" class="card">
                <h2>Active Polls</h2>
                <div id="polls-list"></div>
            </div>
        </div>

        <script>
            let activeConnections = {};

            // Create a new poll
            async function createPoll() {
                const question = document.getElementById('question').value.trim();
                const optionsText = document.getElementById('options').value.trim();
                
                if (!question || !optionsText) {
                    showError('Please fill in all fields');
                    return;
                }
                
                const options = optionsText.split('\\n').map(o => o.trim()).filter(o => o);
                if (options.length < 2) {
                    showError('Please provide at least 2 options');
                    return;
                }
                
                try {
                    const response = await fetch('/polls', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question, options })
                    });
                    
                    if (!response.ok) throw new Error('Failed to create poll');
                    
                    const poll = await response.json();
                    document.getElementById('question').value = '';
                    document.getElementById('options').value = '';
                    document.getElementById('error-message').style.display = 'none';
                    
                    loadPolls();
                } catch (error) {
                    showError('Error creating poll: ' + error.message);
                }
            }

            // Load all polls
            async function loadPolls() {
                try {
                    const response = await fetch('/polls');
                    const polls = await response.json();
                    displayPolls(polls);
                } catch (error) {
                    console.error('Error loading polls:', error);
                }
            }

            // Display polls
            function displayPolls(polls) {
                const container = document.getElementById('polls-list');
                if (polls.length === 0) {
                    container.innerHTML = '<div class="loading">No polls yet. Create one above!</div>';
                    return;
                }
                
                container.innerHTML = polls.map(poll => `
                    <div class="poll-item">
                        <div class="poll-id">Poll ID: ${poll.id}</div>
                        <div class="poll-question">${escapeHtml(poll.question)}</div>
                        <div id="status-${poll.id}" class="status connecting">🔄 Connecting...</div>
                        <div id="poll-${poll.id}">
                            ${poll.options.map((option, idx) => `
                                <div class="option">
                                    <input type="radio" id="option-${poll.id}-${idx}" name="poll-${poll.id}" value="${option.id}">
                                    <label for="option-${poll.id}-${idx}">${escapeHtml(option.text)}</label>
                                    <span class="vote-count" id="votes-${poll.id}-${option.id}">${option.votes} votes</span>
                                </div>
                            `).join('')}
                        </div>
                        <div class="btn-group">
                            <button onclick="submitVote(${poll.id})">Vote</button>
                        </div>
                    </div>
                `).join('');
                
                // Connect WebSocket for each poll
                polls.forEach(poll => connectWebSocket(poll.id));
            }

            // Connect WebSocket
            function connectWebSocket(pollId) {
                if (activeConnections[pollId]) return; // Already connected
                
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const ws = new WebSocket(`${protocol}//${window.location.host}/ws/polls/${pollId}`);
                
                ws.onopen = () => {
                    console.log(`Connected to poll ${pollId}`);
                    updateStatus(pollId, 'connected');
                };
                
                ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    if (message.type === 'poll_state' || message.type === 'poll_update') {
                        updatePollDisplay(message.data);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error(`WebSocket error for poll ${pollId}:`, error);
                    updateStatus(pollId, 'disconnected');
                };
                
                ws.onclose = () => {
                    console.log(`Disconnected from poll ${pollId}`);
                    updateStatus(pollId, 'disconnected');
                    delete activeConnections[pollId];
                };
                
                activeConnections[pollId] = ws;
            }

            // Submit a vote
            function submitVote(pollId) {
                const selected = document.querySelector(`input[name="poll-${pollId}"]:checked`);
                if (!selected) {
                    alert('Please select an option');
                    return;
                }
                
                const ws = activeConnections[pollId];
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'vote',
                        option_id: parseInt(selected.value)
                    }));
                }
            }

            // Update poll display
            function updatePollDisplay(poll) {
                poll.options.forEach(option => {
                    const voteElement = document.getElementById(`votes-${poll.id}-${option.id}`);
                    if (voteElement) {
                        voteElement.textContent = `${option.votes} votes`;
                    }
                });
            }

            // Update connection status
            function updateStatus(pollId, status) {
                const statusEl = document.getElementById(`status-${pollId}`);
                if (statusEl) {
                    statusEl.className = `status ${status}`;
                    if (status === 'connected') {
                        statusEl.textContent = '✅ Connected - Receiving real-time updates';
                    } else if (status === 'disconnected') {
                        statusEl.textContent = '❌ Disconnected - Reconnecting...';
                    } else {
                        statusEl.textContent = '🔄 Connecting...';
                    }
                }
            }

            // Escape HTML
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            // Show error
            function showError(message) {
                const errorEl = document.getElementById('error-message');
                errorEl.textContent = message;
                errorEl.style.display = 'block';
            }

            // Load polls on page load
            loadPolls();
        </script>
    </body>
    </html>
    """


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
