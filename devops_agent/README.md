# DevOps Engineer Agent

A multi-agent DevOps automation system built with [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/).

## Architecture

A root **DevOpsCoordinator** delegates to specialized sub-agents:

| Agent | Role |
|---|---|
| **DispatchAgent** | Decomposes complex requests into subtasks |
| **CloudInfraAgent** | AWS / GCP / Azure CLI operations |
| **KubernetesAgent** | K8s cluster management |
| **CICDAgent** | CI/CD pipeline generation (GitHub Actions, GitLab CI) |
| **MonitoringAgent** | Metrics, alerts, and log analysis |
| **ScriptingAgent** | Bash/Python automation scripts |

### Workflow Agents

- **IncidentResponseWorkflow** (`SequentialAgent`): Monitor → Diagnose → Fix
- **DeployPipelineWorkflow** (`ParallelAgent` + `SequentialAgent`): Parallel CI/CD + K8s checks → Deploy

## Quick Start

### 1. Setup

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `.env` and set your Google API key:

```
GOOGLE_API_KEY=your-actual-api-key-here
```

### 3. Run with ADK Developer UI

```bash
adk web devops_agent
```

Open `http://localhost:8000` in your browser to interact with the agent.

### 4. Run with Docker

```bash
docker compose up --build
```

## Project Structure

```
devops_agent/
├── .env                          # API key config
├── requirements.txt              # Dependencies
├── Dockerfile / docker-compose   # Container deployment
├── devops_agent/                 # ADK agent package
│   ├── agent.py                  # Root coordinator agent
│   ├── prompts.py                # System instructions
│   ├── callbacks.py              # Lifecycle & safety callbacks
│   ├── shared_state.py           # State management
│   ├── sub_agents/               # 6 specialist agents
│   ├── tools/                    # 15+ DevOps tool functions
│   └── workflows/                # Orchestrated multi-step workflows
└── tests/                        # Unit & integration tests
```

## Example Prompts

- *"List all pods in the production namespace"*
- *"Generate a GitHub Actions CI pipeline for a Python project with linting and tests"*
- *"There's a P1 alert on the payment service — investigate and propose a fix"*
- *"Write a bash script to rotate AWS IAM access keys"*
- *"Scale the api-gateway deployment to 5 replicas"*

## Safety

Destructive operations (delete, terminate, scale-to-zero) are automatically flagged by the `before_tool_callback` and require user confirmation before execution.
