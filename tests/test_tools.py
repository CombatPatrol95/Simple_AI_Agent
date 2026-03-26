"""
Unit tests for DevOps agent tools.
"""

import pytest
from unittest.mock import patch, MagicMock

from agents.tools.cloud_tools import run_aws_cli, run_gcp_cli, run_azure_cli
from agents.tools.kubernetes_tools import list_pods, scale_deployment, get_pod_logs, apply_manifest
from agents.tools.cicd_tools import generate_github_actions, generate_gitlab_ci, list_workflows
from agents.tools.monitoring_tools import query_metrics, check_alerts, get_service_logs
from agents.tools.scripting_tools import generate_script, run_shell_command


# ─── Cloud Tools Tests ────────────────────────────────────────────────────────

class TestCloudTools:
    """Tests for cloud CLI tool functions."""

    @patch("agents.tools.cloud_tools.subprocess.run")
    def test_run_aws_cli_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Buckets": []}',
            stderr="",
        )
        result = run_aws_cli("aws s3 ls --output json")
        assert result["status"] == "success"
        assert result["cli"] == "aws"
        assert "stdout" in result

    @patch("agents.tools.cloud_tools.subprocess.run")
    def test_run_aws_cli_error(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="An error occurred",
        )
        result = run_aws_cli("aws s3 ls")
        assert result["status"] == "error"

    @patch("agents.tools.cloud_tools.subprocess.run")
    def test_run_gcp_cli_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="project-id", stderr="")
        result = run_gcp_cli("gcloud config get-value project")
        assert result["status"] == "success"
        assert result["cli"] == "gcloud"

    @patch("agents.tools.cloud_tools.subprocess.run")
    def test_run_azure_cli_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="[]", stderr="")
        result = run_azure_cli("az vm list")
        assert result["status"] == "success"
        assert result["cli"] == "az"

    @patch("agents.tools.cloud_tools.subprocess.run")
    def test_cli_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        result = run_aws_cli("aws s3 ls")
        assert result["status"] == "error"
        assert "not installed" in result["error"]


# ─── Kubernetes Tools Tests ───────────────────────────────────────────────────

class TestKubernetesTools:
    """Tests for Kubernetes tool functions."""

    @patch("agents.tools.kubernetes_tools.subprocess.run")
    @patch("agents.tools.kubernetes_tools._get_k8s_client", return_value=None)
    def test_list_pods_kubectl_fallback(self, mock_client, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"items": []}',
            stderr="",
        )
        result = list_pods("default")
        assert result["status"] == "success"

    @patch("agents.tools.kubernetes_tools.subprocess.run")
    @patch("agents.tools.kubernetes_tools._get_k8s_client", return_value=None)
    def test_scale_deployment_kubectl(self, mock_client, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="deployment.apps/nginx scaled",
            stderr="",
        )
        result = scale_deployment("nginx", "default", 3)
        assert result["status"] == "success"

    def test_apply_manifest_invalid_yaml(self):
        result = apply_manifest("not: valid: yaml: [")
        assert result["status"] == "error"

    def test_apply_manifest_missing_kind(self):
        result = apply_manifest("foo: bar\nbaz: 123")
        assert result["status"] == "error"
        assert "kind" in result["error"]


# ─── CI/CD Tools Tests ────────────────────────────────────────────────────────

class TestCICDTools:
    """Tests for CI/CD pipeline generation tools."""

    def test_generate_github_actions_python(self):
        result = generate_github_actions(
            name="CI", language="python", include_lint=True, include_test=True
        )
        assert result["status"] == "success"
        assert result["format"] == "github_actions"
        assert "content" in result
        assert "flake8" in result["content"]
        assert "pytest" in result["content"]

    def test_generate_github_actions_node(self):
        result = generate_github_actions(name="CI", language="node")
        assert result["status"] == "success"
        assert "npm" in result["content"]

    def test_generate_gitlab_ci_python(self):
        result = generate_gitlab_ci(language="python")
        assert result["status"] == "success"
        assert result["format"] == "gitlab_ci"
        assert "content" in result

    def test_list_workflows_empty(self, tmp_path):
        result = list_workflows(str(tmp_path))
        assert result["status"] == "success"
        assert result["count"] == 0


# ─── Scripting Tools Tests ────────────────────────────────────────────────────

class TestScriptingTools:
    """Tests for script generation and shell execution tools."""

    def test_generate_bash_script(self):
        result = generate_script("rotate AWS keys", "bash")
        assert result["status"] == "success"
        assert result["language"] == "bash"
        assert "set -euo pipefail" in result["script"]
        assert "rotate AWS keys" in result["script"]

    def test_generate_python_script(self):
        result = generate_script("backup database", "python")
        assert result["status"] == "success"
        assert result["language"] == "python"
        assert "argparse" in result["script"]
        assert "backup database" in result["script"]

    def test_generate_script_unsupported_language(self):
        result = generate_script("do something", "ruby")
        assert result["status"] == "error"
        assert "Unsupported" in result["error"]

    @patch("agents.tools.scripting_tools.subprocess.run")
    def test_run_shell_command_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="hello world",
            stderr="",
        )
        result = run_shell_command("echo hello world")
        assert result["status"] == "success"
        assert result["stdout"] == "hello world"
