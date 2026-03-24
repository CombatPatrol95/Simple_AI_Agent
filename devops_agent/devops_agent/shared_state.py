"""
Shared state keys and helper functions for session state management.
All agents read/write state through these constants and utilities
to ensure consistency across the multi-agent system.
"""


# ─── State Key Constants ─────────────────────────────────────────────────────

# Written by DispatchAgent, read by Coordinator
TASK_PLAN = "task_plan"

# Accumulated results from sub-agent tool executions
SUBTASK_RESULTS = "subtask_results"

# Active cloud provider context (aws | gcp | azure)
CURRENT_CLOUD_PROVIDER = "current_cloud_provider"

# Active Kubernetes cluster/namespace context
K8S_CONTEXT = "k8s_context"

# Flag set by before_tool_callback for dangerous operations
REQUIRES_CONFIRMATION = "requires_confirmation"

# Audit trail of all agent actions
EXECUTION_LOG = "execution_log"


# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_state(state: dict, key: str, default=None):
    """Safely retrieve a value from session state."""
    return state.get(key, default)


def set_state(state: dict, key: str, value):
    """Set a value in session state."""
    state[key] = value


def append_to_state_list(state: dict, key: str, item):
    """Append an item to a list stored in session state. Creates the list if needed."""
    if key not in state:
        state[key] = []
    state[key].append(item)


def append_execution_log(state: dict, agent_name: str, action: str, result: str):
    """Add an entry to the execution audit log."""
    entry = {
        "agent": agent_name,
        "action": action,
        "result": result,
    }
    append_to_state_list(state, EXECUTION_LOG, entry)


def append_subtask_result(state: dict, agent_name: str, task: str, output):
    """Record a sub-agent's task result."""
    entry = {
        "agent": agent_name,
        "task": task,
        "output": output,
    }
    append_to_state_list(state, SUBTASK_RESULTS, entry)
