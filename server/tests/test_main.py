import unittest

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestMain(unittest.TestCase):
    def test_healthcheck(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Server is running, STATUS": "HEALTHY"}
