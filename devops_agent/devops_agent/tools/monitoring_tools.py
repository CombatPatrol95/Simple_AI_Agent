"""
Monitoring and observability tools.
Provides interfaces for querying metrics, checking alerts, and retrieving logs.
These simulate interactions with monitoring systems (Prometheus, Grafana, ELK, etc.)
and can be extended to connect to real backends.
"""

import subprocess
import json


def query_metrics(query: str, time_range: str = "1h") -> dict:
    """Query metrics from a monitoring system using a PromQL-style query.

    This tool simulates querying a Prometheus-compatible metrics endpoint.
    In production, replace the implementation with actual Prometheus API calls.

    Args:
        query: A PromQL query string (e.g., 'rate(http_requests_total[5m])' or 'up{job="api-server"}').
        time_range: Time range for the query (e.g., '1h', '30m', '7d'). Defaults to '1h'.

    Returns:
        A dict with status and the query results, including metric values and metadata.
    """
    # Attempt to query a local Prometheus instance via curl/CLI
    try:
        result = subprocess.run(
            [
                "curl", "-s",
                f"http://localhost:9090/api/v1/query",
                "--data-urlencode", f"query={query}",
            ],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return {"status": "success", "query": query, "time_range": time_range, "data": data}
            except json.JSONDecodeError:
                return {"status": "success", "query": query, "raw_output": result.stdout}
        return {"status": "error", "error": result.stderr}
    except FileNotFoundError:
        return {
            "status": "info",
            "message": (
                "No Prometheus endpoint reachable. In production, configure "
                "PROMETHEUS_URL environment variable. Query attempted: " + query
            ),
        }
    except Exception as e:
        return {"status": "error", "query": query, "error": str(e)}


def check_alerts(severity: str = "all") -> dict:
    """Check active alerts from the alerting system.

    Queries the alerting system (e.g., Prometheus Alertmanager) for currently
    firing alerts filtered by severity level.

    Args:
        severity: Alert severity to filter by ('critical', 'warning', 'info', or 'all'). Defaults to 'all'.

    Returns:
        A dict with status and a list of active alerts.
    """
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:9093/api/v2/alerts?active=true"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            try:
                alerts = json.loads(result.stdout)
                if severity != "all":
                    alerts = [
                        a for a in alerts
                        if a.get("labels", {}).get("severity") == severity
                    ]
                return {
                    "status": "success",
                    "severity_filter": severity,
                    "alerts": alerts,
                    "count": len(alerts),
                }
            except json.JSONDecodeError:
                return {"status": "success", "raw_output": result.stdout}
        return {"status": "error", "error": result.stderr}
    except FileNotFoundError:
        return {
            "status": "info",
            "message": (
                "No Alertmanager endpoint reachable. In production, configure "
                "ALERTMANAGER_URL environment variable. Severity filter: " + severity
            ),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_service_logs(service: str, lines: int = 50) -> dict:
    """Retrieve recent logs from a service.

    Attempts to get logs via journalctl (systemd), docker logs, or kubectl logs.

    Args:
        service: The name of the service or container to get logs from.
        lines: Number of recent log lines to retrieve. Defaults to 50.

    Returns:
        A dict with status and the log content.
    """
    errors = []

    # Try Docker logs first
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(lines), service],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return {
                "status": "success",
                "source": "docker",
                "service": service,
                "logs": result.stdout + result.stderr,
                "lines_requested": lines,
            }
        errors.append(f"docker: {result.stderr.strip()}")
    except FileNotFoundError:
        errors.append("docker: not installed")
    except Exception as e:
        errors.append(f"docker: {e}")

    # Try kubectl logs
    try:
        result = subprocess.run(
            ["kubectl", "logs", f"deployment/{service}", f"--tail={lines}"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return {
                "status": "success",
                "source": "kubernetes",
                "service": service,
                "logs": result.stdout,
                "lines_requested": lines,
            }
        errors.append(f"kubectl: {result.stderr.strip()}")
    except FileNotFoundError:
        errors.append("kubectl: not installed")
    except Exception as e:
        errors.append(f"kubectl: {e}")

    # Try journalctl (Linux systemd)
    try:
        result = subprocess.run(
            ["journalctl", "-u", service, "-n", str(lines), "--no-pager"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return {
                "status": "success",
                "source": "journalctl",
                "service": service,
                "logs": result.stdout,
                "lines_requested": lines,
            }
        errors.append(f"journalctl: {result.stderr.strip()}")
    except FileNotFoundError:
        errors.append("journalctl: not installed")
    except Exception as e:
        errors.append(f"journalctl: {e}")

    return {
        "status": "error",
        "service": service,
        "error": "Could not retrieve logs from any source",
        "tried": errors,
    }
