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
fastapi dev main.py
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
pytest -s
```
