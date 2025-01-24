# Streamsight UI Server

## Getting Started

**Pre-requisite**:
1. Change directory to the root of the project and ensure that you are in the `server` directory
```
cd server
```
2. Our project is managed using [astral-uv](https://docs.astral.sh/uv/) ensure you have uv installed via:
```
pip install uv
```
- Check out alternative installation options [here](https://docs.astral.sh/uv/getting-started/installation/)
3. After installing uv, install dependencies using:
```
uv sync --all-extras
```
- NOTE: This command will automatically create a virtual environment in the `.venv` folder.
4. Run the following command and fill in the empty `.env` details
```
cp .env.example .env
```
5. Run `source .venv/bin/activate

### Development
1. Run
```
uv run fastapi dev src/main.py
```
2. Check health via: http://127.0.0.1:8000
3. Access OPENAPI Spec via: http://127.0.0.1:8000/docs

### Migrations
- For updating database with additional data attributes
1. In root directory run 
```
uv run python3 -m migrations.scripts.<script_name>
```

### Testing
* To run test in streamlined mode:
```
uv run pytest
```

* To run test and include Verbose:
```
uv run pytest -s -vv
```
* To obtain test coverage:
1. To compile coverage, run:
```
uv run coverage run -m pytest
```
2. To get report in terminal, run:
```
uv run coverage report -m
```
3. To get a more comprehensive report, run:
```
uv run coverage html
```
and open htmlcov/index.html in a web browser.

### Commits
We use [Ruff](https://github.com/astral-sh/ruff) as our code formatter.
The rules can be found under `ruff.toml`. The rules are part of our pre-commit hook.

#### Linting with ruff:
```
uv run ruff check                          # Lint all files and nested files under the current directory.
uv run ruff check your_path                # Lint all files and nested files under `/your_path`.
uv run ruff check your_path/*.py           # Lint all `.py` files under `/your_path`.
uv run ruff check your_path/your_file.py   # Lint `your_file.py`.
```
- NOTE: Include `--fix` to automatically fix issues.

#### Formatting with ruff:
```
uv run ruff format                          # Format all files and nested files under the current directory.
uv run ruff format your_path/               # Format all files and nested files under `/your_path`.
uv run ruff format your_path/*.py           # Format all `.py` files under `/your_path`.
uv run ruff format your_path/your_file.py   # Format `your_file.py`.
```


#### Commit Messages:
Our commit messages should follow the convention of [Git Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/)


#### Folder Structure:
```
.
├── src
│   ├── __init__.py
│   ├── constants.py
│   ├── database.py
│   ├── events.py
│   ├── main.py
│   ├── settings.py
│   └── routers
│   │   ├── __init__.py
│   │   ├── algorithm_management.py
│   │   ├── authentication.py
│   │   ├── data_handling.py
│   │   ├── metrics.py
│   │   └── predictions.py
│   │   └── stream_management.py
│   └── models
│   │   ├── __init__.py
│   │   └── algorithm_management_models.py
│   │   └── metadata.py
│   │   └── metrics_models.py
│   │   └── stream_management_models.py
│   └── supabase_client
│   │   ├── __init__.py
│   │   └── authentication.py
│   │   └── client.py
│   └── utils
│       ├── __init__.py
│       └── db_utils.py
│       └── string_utils.py
│       └── uuid_utils.py
```
