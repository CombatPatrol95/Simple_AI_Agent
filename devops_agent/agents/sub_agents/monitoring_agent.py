"""
Monitoring Agent — observability, metrics, alerts, and log analysis.
"""

from google.adk.agents import Agent

from agents.prompts import MONITORING_INSTRUCTION
from agents.tools.monitoring_tools import (
    query_metrics,
    check_alerts,
    get_service_logs,
)


monitoring_agent = Agent(
    name="monitoring_agent",
    model="gemini-2.0-flash",
    instruction=MONITORING_INSTRUCTION,
    description=(
        "Monitoring and observability specialist. Queries Prometheus-style "
        "metrics, checks active alerts from Alertmanager, and retrieves "
        "service logs from Docker, Kubernetes, or systemd."
    ),
    tools=[query_metrics, check_alerts, get_service_logs],
)
