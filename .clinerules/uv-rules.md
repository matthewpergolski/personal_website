# UV for Python Dependency Management Rule

Use uv as the exclusive tool for managing Python projects, including virtual environments, dependencies, and Python versions, to ensure consistency, reproducibility, and efficiency across development workflows.

- Initialize projects with `uv init <project_name> --python <version>` (e.g., `uv init personal_website --python 3.12`) to set up a project directory, Git repository, and .gitignore with a specified Python version.
- Add dependencies declaratively using `uv add <package>` (e.g., `uv add flask`), which updates pyproject.toml and installs packages in the project’s virtual environment.
- Synchronize the environment with `uv sync` to align it with pyproject.toml after cloning or updating dependencies.
- Run scripts or applications with `uv run <command>` (e.g., `uv run python app.py`) to execute them in the project’s isolated environment without manual activation.
- Leverage `uv python` to manage multiple Python versions if needed (e.g., `uv python install 3.12`).

This approach ensures a modern, streamlined, and reproducible Python development process. Always prefer uv over tools like pip, venv, or poetry unless explicitly overridden.