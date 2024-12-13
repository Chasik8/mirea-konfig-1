import os
import subprocess
import argparse
from datetime import datetime
from graphviz import Digraph
import pytest


def get_commit_dependencies(repo_path, since_date):
    command = [
        'git', '-C', repo_path, 'log', '--name-only', '--pretty=format:%H', f'--since={since_date}'
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)
    log = result.stdout

    commit_dependencies = {}
    current_commit = None

    for line in log.splitlines():
        if line.startswith(" ") or line == "":
            continue

        if not line.startswith(" ") and len(line) == 40:  # Commit hash
            current_commit = line
            commit_dependencies[current_commit] = []
        else:  # File or folder path
            if current_commit:
                commit_dependencies[current_commit].append(line)

    return commit_dependencies


def build_graphviz_graph(dependencies, output_file):
    graph = Digraph(format='png')

    for commit, files in dependencies.items():
        label = f"{commit}\n" + "\n".join(files)
        graph.node(commit, label=label)

        for other_commit in dependencies.keys():
            if other_commit != commit and set(files).intersection(dependencies[other_commit]):
                graph.edge(commit, other_commit)

    graph.render(output_file, cleanup=True)


def main():
    parser = argparse.ArgumentParser(description="Visualize Git repository dependencies.")
    parser.add_argument('--repo-path', required=True, help="Path to the Git repository.")
    parser.add_argument('--output-file', required=True, help="Path to save the dependency graph PNG.")
    parser.add_argument('--since-date', required=True, help="Date for filtering commits (YYYY-MM-DD).")

    args = parser.parse_args()

    try:
        datetime.strptime(args.since_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    dependencies = get_commit_dependencies(args.repo_path, args.since_date)
    build_graphviz_graph(dependencies, args.output_file)

    print(f"Dependency graph successfully generated at {args.output_file}.png")


# Tests
@pytest.fixture
def mock_repo(tmp_path):
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)

    # Add test commits
    (repo_path / "file1.txt").write_text("content1")
    subprocess.run(["git", "add", "file1.txt"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "First commit"], cwd=repo_path, check=True)

    (repo_path / "file2.txt").write_text("content2")
    subprocess.run(["git", "add", "file2.txt"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "Second commit"], cwd=repo_path, check=True)

    return repo_path


def test_get_commit_dependencies(mock_repo):
    since_date = "2000-01-01"
    dependencies = get_commit_dependencies(str(mock_repo), since_date)

    assert len(dependencies) == 2
    assert any("file1.txt" in files for files in dependencies.values())
    assert any("file2.txt" in files for files in dependencies.values())


def test_build_graphviz_graph(tmp_path):
    dependencies = {
        "commit1": ["file1.txt", "file2.txt"],
        "commit2": ["file2.txt", "file3.txt"],
    }
    output_file = str(tmp_path / "test_graph")
    build_graphviz_graph(dependencies, output_file)

    assert os.path.exists(f"{output_file}.png")


if __name__ == "__main__":
    main()
