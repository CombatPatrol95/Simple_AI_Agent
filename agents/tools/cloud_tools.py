"""
Cloud CLI tools for interacting with AWS, GCP, and Azure.
Each function wraps a subprocess call to the respective CLI.
"""

import subprocess
import shlex


def _run_cli(cli_name: str, command: str) -> dict:
    """Internal helper to execute a CLI command and capture output."""
    try:
        # Split command safely
        args = shlex.split(command)
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=120,
            shell=(subprocess.sys.platform == "win32"),
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "cli": cli_name,
            "command": command,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "cli": cli_name,
            "command": command,
            "error": "Command timed out after 120 seconds",
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "cli": cli_name,
            "command": command,
            "error": f"{cli_name} CLI is not installed or not in PATH",
        }
    except Exception as e:
        return {
            "status": "error",
            "cli": cli_name,
            "command": command,
            "error": str(e),
        }


def run_aws_cli(command: str) -> dict:
    """Execute an AWS CLI command.

    Args:
        command: The full AWS CLI command to execute (e.g., 'aws s3 ls' or 'aws ec2 describe-instances --region us-east-1').

    Returns:
        A dict with status, stdout, stderr, and return_code.
    """
    return _run_cli("aws", command)


def run_gcp_cli(command: str) -> dict:
    """Execute a Google Cloud (gcloud) CLI command.

    Args:
        command: The full gcloud CLI command to execute (e.g., 'gcloud compute instances list' or 'gcloud config get-value project').

    Returns:
        A dict with status, stdout, stderr, and return_code.
    """
    return _run_cli("gcloud", command)


def run_azure_cli(command: str) -> dict:
    """Execute an Azure CLI command.

    Args:
        command: The full Azure CLI command to execute (e.g., 'az vm list' or 'az group list --output json').

    Returns:
        A dict with status, stdout, stderr, and return_code.
    """
    return _run_cli("az", command)
