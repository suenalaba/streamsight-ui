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