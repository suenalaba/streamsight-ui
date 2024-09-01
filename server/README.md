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

**Pre-requisite**:
1. Run to get the path to your project
```
pwd
```
2. Set Python PATH
```
export PYTHONPATH="${PYTHONPATH}:<PASTE PATH TO YOUR PROJECT HERE>"
```

* To run test in streamlined mode:
```
pytest
```

* To run test and include Verbose:
```
pytest -s
```
