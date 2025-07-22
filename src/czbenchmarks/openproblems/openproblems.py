import os
import subprocess
import yaml

def get_metric_executable(task: str, metric: str) -> str:
    """Get the path to the built Viash executable for a given Open Problems task
    and metric.

    Args:
        task: Name of the task (e.g., "task_batch_integration")
        metric: Name of the metric (e.g., "pcr", "aws_batch")

    Returns:
        Path to the Viash component executable
    """

    task_repo = clone_task_repo(task)

    metric_path = f"src/metrics/{metric}"
    metric_executable = build_viash_component(task_repo, metric_path)

    return metric_executable


def clone_task_repo(task: str) -> str:
    """Clone an Open Problems task repository.

    Args:
        task: Name of the task to clone

    Returns:
        Path to the cloned repository
    """

    repo_url = f"https://github.com/openproblems-bio/{task}.git"
    repo_path = f"./.openproblems/{task}"

    if not os.path.exists(repo_path):
        subprocess.run(["git", "clone", repo_url, repo_path], check=True)
    else:
        subprocess.run(["git", "-C", repo_path, "pull"], check=True)

    return repo_path


def build_viash_component(repo_path: str, component_path: str) -> str:
    """Build a Viash component from the given repository and component path.

    Args:
        repo_path: Path to the cloned repository
        component_path: Path to the component within the repository

    Returns:
        Path to the built Viash component executable
    """

    config_path = os.path.join(component_path, "config.vsh.yaml")

    with open(os.path.join(repo_path, config_path), 'r') as f:
        config = yaml.safe_load(f)

    component_name = config.get("name")
    target_path = os.path.join("target", component_path)
    executable_path = os.path.join(repo_path, target_path, component_name)

    if os.path.exists(executable_path):
        return executable_path

    os.chdir(repo_path)
    subprocess.run(
        [
            "viash", "build",
            "--engine", "docker",
            "--runner", "executable",
            "--setup", "ifneedbepullelsecachedbuild",
            "--output", target_path,
            config_path
        ],
        check=True
    )

    return executable_path
