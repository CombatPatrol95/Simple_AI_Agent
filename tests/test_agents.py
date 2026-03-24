"""
Integration tests for DevOps agent definitions.
Validates that agents are properly instantiated with correct tools and sub-agents.
"""

import pytest


class TestAgentDefinitions:
    """Tests that all agents are properly defined and configured."""

    def test_root_agent_exists(self):
        from devops_agent import root_agent
        assert root_agent is not None
        assert root_agent.name == "devops_coordinator"

    def test_root_agent_has_sub_agents(self):
        from devops_agent import root_agent
        sub_agent_names = [a.name for a in root_agent.sub_agents]
        assert "dispatch_agent" in sub_agent_names
        assert "cloud_infra_agent" in sub_agent_names
        assert "kubernetes_agent" in sub_agent_names
        assert "cicd_agent" in sub_agent_names
        assert "monitoring_agent" in sub_agent_names
        assert "scripting_agent" in sub_agent_names
        assert "incident_response_workflow" in sub_agent_names
        assert "deploy_pipeline_workflow" in sub_agent_names

    def test_root_agent_has_callbacks(self):
        from devops_agent import root_agent
        assert root_agent.before_agent_callback is not None
        assert root_agent.after_agent_callback is not None
        assert root_agent.before_tool_callback is not None
        assert root_agent.after_tool_callback is not None

    def test_dispatch_agent_has_no_tools(self):
        from devops_agent.sub_agents.dispatch_agent import dispatch_agent
        assert dispatch_agent.tools is None or len(dispatch_agent.tools) == 0

    def test_cloud_infra_agent_tools(self):
        from devops_agent.sub_agents.cloud_infra_agent import cloud_infra_agent
        tool_names = [t.__name__ if callable(t) else t.name for t in cloud_infra_agent.tools]
        assert "run_aws_cli" in tool_names
        assert "run_gcp_cli" in tool_names
        assert "run_azure_cli" in tool_names

    def test_kubernetes_agent_tools(self):
        from devops_agent.sub_agents.kubernetes_agent import kubernetes_agent
        tool_names = [t.__name__ if callable(t) else t.name for t in kubernetes_agent.tools]
        assert "list_pods" in tool_names
        assert "scale_deployment" in tool_names
        assert "get_pod_logs" in tool_names
        assert "apply_manifest" in tool_names

    def test_cicd_agent_tools(self):
        from devops_agent.sub_agents.cicd_agent import cicd_agent
        tool_names = [t.__name__ if callable(t) else t.name for t in cicd_agent.tools]
        assert "generate_github_actions" in tool_names
        assert "generate_gitlab_ci" in tool_names
        assert "list_workflows" in tool_names

    def test_monitoring_agent_tools(self):
        from devops_agent.sub_agents.monitoring_agent import monitoring_agent
        tool_names = [t.__name__ if callable(t) else t.name for t in monitoring_agent.tools]
        assert "query_metrics" in tool_names
        assert "check_alerts" in tool_names
        assert "get_service_logs" in tool_names

    def test_scripting_agent_tools(self):
        from devops_agent.sub_agents.scripting_agent import scripting_agent
        tool_names = [t.__name__ if callable(t) else t.name for t in scripting_agent.tools]
        assert "generate_script" in tool_names
        assert "run_shell_command" in tool_names


class TestWorkflowAgents:
    """Tests for workflow agent configurations."""

    def test_incident_response_is_sequential(self):
        from devops_agent.workflows.incident_response import incident_response_workflow
        assert incident_response_workflow.name == "incident_response_workflow"
        sub_names = [a.name for a in incident_response_workflow.sub_agents]
        assert sub_names == ["wf_monitoring_agent", "wf_cloud_infra_agent", "wf_scripting_agent"]

    def test_deploy_pipeline_structure(self):
        from devops_agent.workflows.deploy_pipeline import deploy_pipeline_workflow
        assert deploy_pipeline_workflow.name == "deploy_pipeline_workflow"
        # First sub-agent should be the parallel checks
        parallel = deploy_pipeline_workflow.sub_agents[0]
        assert parallel.name == "deploy_parallel_checks"
        parallel_names = [a.name for a in parallel.sub_agents]
        assert "wf_cicd_agent" in parallel_names
        assert "wf_kubernetes_agent" in parallel_names


class TestCallbacks:
    """Tests for callback functions."""

    def test_dangerous_detection(self):
        from devops_agent.callbacks import _is_dangerous
        assert _is_dangerous("kubectl delete pod my-pod") is True
        assert _is_dangerous("aws ec2 terminate-instances") is True
        assert _is_dangerous("rm -rf /tmp/test") is True
        assert _is_dangerous("kubectl get pods") is False
        assert _is_dangerous("aws s3 ls") is False

    def test_shared_state_helpers(self):
        from devops_agent.shared_state import (
            get_state, set_state, append_to_state_list,
            append_execution_log, append_subtask_result,
        )
        state = {}
        set_state(state, "key1", "value1")
        assert get_state(state, "key1") == "value1"
        assert get_state(state, "missing", "default") == "default"

        append_to_state_list(state, "items", "a")
        append_to_state_list(state, "items", "b")
        assert state["items"] == ["a", "b"]

        append_execution_log(state, "test_agent", "test_action", "ok")
        assert len(state["execution_log"]) == 1
        assert state["execution_log"][0]["agent"] == "test_agent"

        append_subtask_result(state, "cloud", "list vms", {"vms": []})
        assert len(state["subtask_results"]) == 1
