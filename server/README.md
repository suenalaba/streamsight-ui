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

#### To run ruff as a linter:
```
ruff check                          # Lint all files in the current directory (and any subdirectories).
ruff check path/to/code/            # Lint all files in `/path/to/code` (and any subdirectories).
ruff check path/to/code/*.py        # Lint all `.py` files in `/path/to/code`.
ruff check path/to/code/to/file.py  # Lint `file.py`.
ruff check @arguments.txt           # Lint using an input file, treating its contents as newline-delimited command-line arguments.
```

#### To run ruff as a formatter:
```
ruff format                          # Format all files in the current directory (and any subdirectories).
ruff format path/to/code/            # Format all files in `/path/to/code` (and any subdirectories).
ruff format path/to/code/*.py        # Format all `.py` files in `/path/to/code`.
ruff format path/to/code/to/file.py  # Format `file.py`.
ruff format @arguments.txt           # Format using an input file, treating its contents as newline-delimited command-line arguments.
```

Include `--fix` to automatically fix issues.

#### Commit Messages:
Our commit messages should follow the convention of [Git Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/)