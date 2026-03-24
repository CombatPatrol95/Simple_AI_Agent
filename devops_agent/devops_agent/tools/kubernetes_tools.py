"""
Kubernetes tools for cluster management.
Uses the official Kubernetes Python client for cluster operations.
Falls back to kubectl CLI if the client is not configured.
"""

import yaml
import subprocess


def _get_k8s_client():
    """Attempt to load the Kubernetes client configuration."""
    try:
        from kubernetes import client, config
        config.load_kube_config()
        return client
    except Exception:
        return None


def list_pods(namespace: str = "default") -> dict:
    """List all pods in a given Kubernetes namespace.

    Args:
        namespace: The Kubernetes namespace to list pods from. Defaults to 'default'.

    Returns:
        A dict with status and a list of pods with their name, status, and restart count.
    """
    k8s = _get_k8s_client()
    if k8s:
        try:
            v1 = k8s.CoreV1Api()
            pods = v1.list_namespaced_pod(namespace=namespace)
            pod_list = []
            for pod in pods.items:
                pod_list.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "restarts": sum(
                        cs.restart_count
                        for cs in (pod.status.container_statuses or [])
                    ),
                    "node": pod.spec.node_name,
                })
            return {"status": "success", "pods": pod_list, "count": len(pod_list)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # Fallback to kubectl CLI
    try:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return {"status": "success", "output": result.stdout}
        return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": f"kubectl not available: {e}"}


def scale_deployment(name: str, namespace: str = "default", replicas: int = 1) -> dict:
    """Scale a Kubernetes deployment to the specified number of replicas.

    Args:
        name: The name of the deployment to scale.
        namespace: The Kubernetes namespace. Defaults to 'default'.
        replicas: The desired number of replicas.

    Returns:
        A dict with the scaling result status.
    """
    k8s = _get_k8s_client()
    if k8s:
        try:
            apps_v1 = k8s.AppsV1Api()
            body = {"spec": {"replicas": replicas}}
            apps_v1.patch_namespaced_deployment_scale(
                name=name, namespace=namespace, body=body
            )
            return {
                "status": "success",
                "message": f"Deployment '{name}' in namespace '{namespace}' scaled to {replicas} replicas.",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # Fallback to kubectl
    try:
        result = subprocess.run(
            ["kubectl", "scale", f"deployment/{name}", f"--replicas={replicas}",
             "-n", namespace],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return {"status": "success", "message": result.stdout.strip()}
        return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_pod_logs(name: str, namespace: str = "default", lines: int = 100) -> dict:
    """Retrieve logs from a Kubernetes pod.

    Args:
        name: The name of the pod.
        namespace: The Kubernetes namespace. Defaults to 'default'.
        lines: Number of recent log lines to retrieve. Defaults to 100.

    Returns:
        A dict with the pod logs.
    """
    k8s = _get_k8s_client()
    if k8s:
        try:
            v1 = k8s.CoreV1Api()
            logs = v1.read_namespaced_pod_log(
                name=name, namespace=namespace, tail_lines=lines
            )
            return {"status": "success", "pod": name, "logs": logs}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # Fallback to kubectl
    try:
        result = subprocess.run(
            ["kubectl", "logs", name, "-n", namespace, f"--tail={lines}"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return {"status": "success", "pod": name, "logs": result.stdout}
        return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def apply_manifest(manifest_yaml: str) -> dict:
    """Apply a Kubernetes manifest (YAML) to the cluster.

    Args:
        manifest_yaml: A valid Kubernetes manifest in YAML format.

    Returns:
        A dict with the result of applying the manifest.
    """
    # Validate YAML first
    try:
        parsed = yaml.safe_load(manifest_yaml)
        if not isinstance(parsed, dict) or "kind" not in parsed:
            return {
                "status": "error",
                "error": "Invalid Kubernetes manifest: missing 'kind' field.",
            }
    except yaml.YAMLError as e:
        return {"status": "error", "error": f"Invalid YAML: {e}"}

    # Apply via kubectl (most reliable for arbitrary manifests)
    try:
        result = subprocess.run(
            ["kubectl", "apply", "-f", "-"],
            input=manifest_yaml,
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return {"status": "success", "message": result.stdout.strip()}
        return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}
