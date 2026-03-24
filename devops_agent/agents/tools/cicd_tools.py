"""
CI/CD pipeline tools for generating and managing workflow configurations.
Supports GitHub Actions and GitLab CI.
"""

import yaml
import subprocess


def generate_github_actions(
    name: str,
    language: str,
    branches: list[str] | None = None,
    include_lint: bool = True,
    include_test: bool = True,
    include_build: bool = False,
    include_deploy: bool = False,
    python_version: str = "3.12",
    node_version: str = "20",
) -> dict:
    """Generate a GitHub Actions workflow YAML configuration.

    Args:
        name: Name of the workflow (e.g., 'CI Pipeline').
        language: Programming language of the project ('python', 'node', 'go').
        branches: List of branches to trigger on. Defaults to ['main'].
        include_lint: Whether to include a linting step.
        include_test: Whether to include a testing step.
        include_build: Whether to include a build step.
        include_deploy: Whether to include a deploy step.
        python_version: Python version to use (if language is python).
        node_version: Node.js version to use (if language is node).

    Returns:
        A dict with status and the generated YAML content.
    """
    if branches is None:
        branches = ["main"]

    workflow = {
        "name": name,
        "on": {
            "push": {"branches": branches},
            "pull_request": {"branches": branches},
        },
        "jobs": {},
    }

    steps = [
        {"name": "Checkout code", "uses": "actions/checkout@v4"},
    ]

    # Language-specific setup
    if language == "python":
        steps.append({
            "name": "Set up Python",
            "uses": "actions/setup-python@v5",
            "with": {"python-version": python_version},
        })
        steps.append({
            "name": "Install dependencies",
            "run": "pip install -r requirements.txt",
        })
        if include_lint:
            steps.append({
                "name": "Lint with flake8",
                "run": "pip install flake8 && flake8 . --count --show-source --statistics",
            })
        if include_test:
            steps.append({
                "name": "Run tests",
                "run": "pip install pytest && pytest -v",
            })
    elif language == "node":
        steps.append({
            "name": "Set up Node.js",
            "uses": "actions/setup-node@v4",
            "with": {"node-version": node_version, "cache": "npm"},
        })
        steps.append({"name": "Install dependencies", "run": "npm ci"})
        if include_lint:
            steps.append({"name": "Lint", "run": "npm run lint"})
        if include_test:
            steps.append({"name": "Run tests", "run": "npm test"})
    elif language == "go":
        steps.append({
            "name": "Set up Go",
            "uses": "actions/setup-go@v5",
            "with": {"go-version": "stable"},
        })
        if include_lint:
            steps.append({
                "name": "Lint with golangci-lint",
                "uses": "golangci/golangci-lint-action@v4",
            })
        if include_test:
            steps.append({"name": "Run tests", "run": "go test ./..."})

    if include_build:
        steps.append({"name": "Build", "run": f"echo 'Add build commands for {language}'"})

    if include_deploy:
        steps.append({
            "name": "Deploy",
            "run": f"echo 'Add deploy commands for {language}'",
            "if": "github.ref == 'refs/heads/main' && github.event_name == 'push'",
        })

    workflow["jobs"]["ci"] = {
        "runs-on": "ubuntu-latest",
        "steps": steps,
    }

    generated_yaml = yaml.dump(workflow, default_flow_style=False, sort_keys=False)

    return {
        "status": "success",
        "format": "github_actions",
        "filename": ".github/workflows/ci.yml",
        "content": generated_yaml,
    }


def generate_gitlab_ci(
    language: str,
    stages: list[str] | None = None,
    include_lint: bool = True,
    include_test: bool = True,
    include_build: bool = False,
    include_deploy: bool = False,
) -> dict:
    """Generate a GitLab CI pipeline YAML configuration.

    Args:
        language: Programming language of the project ('python', 'node', 'go').
        stages: List of pipeline stages. Defaults to auto-generated based on flags.
        include_lint: Whether to include a linting stage.
        include_test: Whether to include a testing stage.
        include_build: Whether to include a build stage.
        include_deploy: Whether to include a deploy stage.

    Returns:
        A dict with status and the generated YAML content.
    """
    if stages is None:
        stages = []
        if include_lint:
            stages.append("lint")
        if include_test:
            stages.append("test")
        if include_build:
            stages.append("build")
        if include_deploy:
            stages.append("deploy")

    # Base image by language
    images = {"python": "python:3.12-slim", "node": "node:20-alpine", "go": "golang:1.22"}
    image = images.get(language, "alpine:latest")

    pipeline = {"image": image, "stages": stages}

    if include_lint:
        if language == "python":
            pipeline["lint"] = {
                "stage": "lint",
                "script": ["pip install flake8", "flake8 . --count --show-source"],
            }
        elif language == "node":
            pipeline["lint"] = {
                "stage": "lint",
                "script": ["npm ci", "npm run lint"],
            }

    if include_test:
        if language == "python":
            pipeline["test"] = {
                "stage": "test",
                "script": ["pip install -r requirements.txt", "pytest -v"],
            }
        elif language == "node":
            pipeline["test"] = {
                "stage": "test",
                "script": ["npm ci", "npm test"],
            }
        elif language == "go":
            pipeline["test"] = {"stage": "test", "script": ["go test ./..."]}

    if include_build:
        pipeline["build"] = {
            "stage": "build",
            "script": [f"echo 'Add build commands for {language}'"],
        }

    if include_deploy:
        pipeline["deploy"] = {
            "stage": "deploy",
            "script": [f"echo 'Add deploy commands for {language}'"],
            "only": ["main"],
        }

    generated_yaml = yaml.dump(pipeline, default_flow_style=False, sort_keys=False)

    return {
        "status": "success",
        "format": "gitlab_ci",
        "filename": ".gitlab-ci.yml",
        "content": generated_yaml,
    }


def list_workflows(repo_path: str = ".") -> dict:
    """List CI/CD workflow files found in a repository.

    Args:
        repo_path: Path to the repository root. Defaults to current directory.

    Returns:
        A dict with status and a list of discovered workflow files.
    """
    import os

    workflows = []

    # Check GitHub Actions
    gh_dir = os.path.join(repo_path, ".github", "workflows")
    if os.path.isdir(gh_dir):
        for f in os.listdir(gh_dir):
            if f.endswith((".yml", ".yaml")):
                workflows.append({
                    "platform": "github_actions",
                    "file": os.path.join(gh_dir, f),
                    "name": f,
                })

    # Check GitLab CI
    gitlab_file = os.path.join(repo_path, ".gitlab-ci.yml")
    if os.path.isfile(gitlab_file):
        workflows.append({
            "platform": "gitlab_ci",
            "file": gitlab_file,
            "name": ".gitlab-ci.yml",
        })

    # Check Jenkinsfile
    jenkins_file = os.path.join(repo_path, "Jenkinsfile")
    if os.path.isfile(jenkins_file):
        workflows.append({
            "platform": "jenkins",
            "file": jenkins_file,
            "name": "Jenkinsfile",
        })

    return {
        "status": "success",
        "workflows": workflows,
        "count": len(workflows),
    }
