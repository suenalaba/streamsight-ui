# Streamsight UI Server

## Getting Started

**Pre-requisite**:
1. Ensure that you are in the `server` directory
2. Create a virtual environment via
```
python -m venv venv
```
3. Activate the virtual environment
```
source venv/bin/activate
```
4. Install requirements
```
pip install requirements.txt
```

### Development
1. Run
```
fastapi dev src/main.py
```
2. Check health via: http://127.0.0.1:8000
3. Access OPENAPI Spec via: http://127.0.0.1:8000/docs

### Testing
* To run test in streamlined mode:
```
pytest
```

* To run test and include Verbose:
```
pytest -s -vv
```
* To obtain test coverage:
1. To compile coverage, run:
```
coverage run -m pytest
```
2. To get report in terminal, run:
```
coverage report -m
```
3. To get a more comprehensive report, run:
```
coverage html
```
and open htmlcov/index.html in a web browser.

### Commits
We use [Ruff](https://github.com/astral-sh/ruff) as our code formatter.
The rules can be found under `ruff.toml`. The rules are part of our pre-commit hook.

#### Linting with ruff:
```
ruff check                          # Lint all files and nested files under the current directory.
ruff check your_path                # Lint all files and nested files under `/your_path`.
ruff check your_path/*.py           # Lint all `.py` files under `/your_path`.
ruff check your_path/your_file.py   # Lint `your_file.py`.
```
NOTE: Include `--fix` to automatically fix issues.

#### Formatting with ruff:
```
ruff format                          # Format all files and nested files under the current directory.
ruff format your_path/               # Format all files and nested files under `/your_path`.
ruff format your_path/*.py           # Format all `.py` files under `/your_path`.
ruff format your_path/your_file.py   # Format `your_file.py`.
```


#### Commit Messages:
Our commit messages should follow the convention of [Git Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/)