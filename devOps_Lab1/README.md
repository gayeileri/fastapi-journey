# DevOps Lab 1 — OpenAI API in Python

> **University DevOps Lab Assignment**
> This project demonstrates how to call the OpenAI API directly from Python,
> package the application with Docker, and automate the build pipeline with
> GitHub Actions CI/CD.

---

## Project Structure

```
devOps_Lab1/
├── main.py                        # Main script: API calls, temperature demo, interactive chat
├── requirements.txt               # Python dependencies
├── Dockerfile                     # How to build the Docker image
├── .env.example                   # Template for your API key (copy → .env, never commit .env!)
├── .gitignore                     # Keeps .env and other secrets out of version control
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions: auto-build & push to DockerHub on push
├── DECISIONS.md                   # Architecture & design decisions
├── API_CONTRACT.md                # Function interfaces and OpenAI endpoint contract
└── ERD.md                         # Data model / entity relationship diagram
```

---

## Quick Start (Local Python)

```bash
# 1. Navigate to the project folder
cd devOps_Lab1

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key (never commit .env to GitHub!)
copy .env.example .env
# Open .env and replace "sk-your-api-key-here" with your real OpenAI key

# 5. Run the script
python main.py
```

---

## What the Script Does

When you run `python main.py`:

1. **Temperature comparison demo** — sends the same prompt at `0.0`, `0.7`, and `1.5`
   so you can see how randomness affects the model's output.
2. **Interactive chat** — a simple loop where you type messages and get AI responses.

### Interactive Commands

| Input | Action |
|---|---|
| Any text | Send to the model and print the response |
| `compare` | Run the temperature comparison demo with a custom prompt |
| `exit` / `quit` | Stop the program |

---

## Key API Parameters Explained

| Parameter | What it controls |
|---|---|
| `temperature` | Randomness (0 = always the same answer, 2 = very creative/unpredictable) |
| `max_tokens` | Hard cap on response length — controls cost and speed |
| `system message` | Sets the model's persona and rules before the user speaks |

---

## Running with Docker

Docker lets you run the app in an isolated environment without installing Python locally.

```bash
# 1. Build the image from the Dockerfile
docker build -t openai-api-lab1 .

# 2. Run the container — inject your API key at runtime (never bake it into the image!)
docker run -it -e OPENAI_API_KEY=sk-your-real-key openai-api-lab1
```

> **Why `-e OPENAI_API_KEY=...`?**
> We pass the key as an environment variable so it never gets stored inside the
> Docker image and cannot accidentally be pushed to DockerHub.

---

## CI/CD Pipeline (GitHub Actions)

The file `.github/workflows/ci.yml` automates the following on every `git push` to `main`:

```
git push → GitHub Actions runner starts
         → Checks out code
         → Logs in to DockerHub (using GitHub Secrets — no plain-text passwords)
         → Builds Docker image
         → Pushes image to DockerHub
```

### Setting Up GitHub Secrets

1. Open your GitHub repository in a browser.
2. Go to **Settings → Secrets and variables → Actions**.
3. Click **New repository secret** and add:

| Secret name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your DockerHub username |
| `DOCKERHUB_TOKEN` | A DockerHub Access Token (not your password!) |

> **How to get a DockerHub token:** DockerHub → Account Settings → Security → New Access Token.

---

## Security Rules (Important!)

- ✅ API keys go in `.env` — loaded at runtime by `python-dotenv`
- ✅ `.env` is listed in `.gitignore` — Git will never track it
- ✅ Docker image receives the key via `-e` flag at `docker run` time
- ✅ GitHub Actions reads credentials from **Secrets** — never from the YAML file
- ❌ Never paste `sk-...` into any source file, Dockerfile, or workflow YAML

---

## Design Documents

| Document | Purpose |
|---|---|
| [DECISIONS.md](DECISIONS.md) | Why each architectural choice was made |
| [API_CONTRACT.md](API_CONTRACT.md) | Function interfaces and OpenAI endpoint contract |
| [ERD.md](ERD.md) | Data model and entity relationships |
