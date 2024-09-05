import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid import UUID

from src.main import app  # Assuming your FastAPI app is defined in main.py
from src.routers.algorithm_management import register_algorithm, evaluator_stream_object_map
from src.routers.algorithm_management import AlgorithmRegistrationRequest

client = TestClient(app)

@pytest.fixture
def mock_evaluator_streamer():
    mock = MagicMock()
    mock.register_algorithm.return_value = UUID("12345678-1234-5678-1234-567812345678")
    return mock

def test_register_algorithm_valid(mock_evaluator_streamer):
    with patch.dict(evaluator_stream_object_map, {UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"): mock_evaluator_streamer}):
        response = client.post(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
            json={"algorithm_name": "test_algorithm"}
        )
        mock_evaluator_streamer.register_algorithm.assert_called_once_with(algorithm_name="test_algorithm")

        assert response.status_code == 200
        assert response.json() == {"algorithm_uuid": "12345678-1234-5678-1234-567812345678"}

def test_register_algorithm_invalid_uuid(mock_evaluator_streamer):
    response = client.post(
        "/streams/invalid-uuid/algorithms",
        json={"algorithm_name": "test_algorithm"}
    )

    mock_evaluator_streamer.register_algorithm.assert_not_called()

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}

def test_register_algorithm_evaluator_not_found(mock_evaluator_streamer):
    response = client.post(
        "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
        json={"algorithm_name": "test_algorithm"}
    )

    mock_evaluator_streamer.register_algorithm.assert_not_called()
    
    assert response.status_code == 404
    assert response.json() == {"detail": "EvaluatorStreamer not found"}

def test_register_algorithm_internal_error(mock_evaluator_streamer):
    mock_evaluator_streamer.register_algorithm.side_effect = Exception("Internal error")
    with patch.dict(evaluator_stream_object_map, {UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"): mock_evaluator_streamer}):
        response = client.post(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
            json={"algorithm_name": "test_algorithm"}
        )
        
        mock_evaluator_streamer.register_algorithm.assert_called_once_with(algorithm_name="test_algorithm")
 
        assert response.status_code == 500
        assert response.json() == {"detail": "Error registering algorithm: Internal error"}
      