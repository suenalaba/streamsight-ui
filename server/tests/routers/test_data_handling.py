from unittest.mock import MagicMock, patch
from uuid import UUID

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


@pytest.fixture
def mock_interaction_matrix():
    mock = MagicMock()
    mock.shape = (3, 3)
    data = {
        "interactionid": [0, 1, 2, 3],
        "uid": [0, 1, 2, 0],
        "iid": [0, 0, 1, 2],
        "ts": [0, 1, 2, 3],
    }

    # Create the DataFrame
    df = pd.DataFrame(data)
    mock.copy_df.return_value = df
    return mock


@pytest.fixture
def mock_evaluator_streamer(mock_interaction_matrix):
    mock = MagicMock()
    mock.get_data.return_value = mock_interaction_matrix
    return mock


def test_get_training_data_valid(mock_evaluator_streamer, mock_interaction_matrix):
    with patch(
        "src.routers.data_handling.get_evaluator_stream_from_db",
        return_value=mock_evaluator_streamer,
    ) as mock_get_evaluator_stream_from_db, patch(
        "src.routers.data_handling.update_evaluator_stream", return_value=None
    ) as mock_update_evaluator_stream:
        response = client.get(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
        )

        mock_get_evaluator_stream_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        mock_evaluator_streamer.get_data.assert_called_once_with(
            UUID("12345678-1234-5678-1234-567812345678")
        )
        mock_interaction_matrix.copy_df.assert_called_once()
        mock_update_evaluator_stream.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"), mock_evaluator_streamer
        )

        assert response.status_code == 200
        assert response.json() == {
            "shape": [3, 3],
            "training_data": [
                {"interactionid": 0, "uid": 0, "iid": 0, "ts": 0},
                {"interactionid": 1, "uid": 1, "iid": 0, "ts": 1},
                {"interactionid": 2, "uid": 2, "iid": 1, "ts": 2},
                {"interactionid": 3, "uid": 0, "iid": 2, "ts": 3},
            ],
        }


def test_get_training_data_invalid_stream_uuid():
    response = client.get(
        "/streams/invalid-stream-uuid/algorithms/12345678-1234-5678-1234-567812345678/training-data"
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}


def test_get_training_data_invalid_algo_uuid():
    response = client.get(
        "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-algo-uuid/training-data"
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}


def test_get_training_data_stream_not_found(mock_evaluator_streamer):
    with patch(
        "src.routers.data_handling.get_evaluator_stream_from_db", return_value=None
    ) as mock_get_evaluator_stream_from_db:
        response = client.get(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
        )

        mock_get_evaluator_stream_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        mock_evaluator_streamer.get_data.assert_not_called()

        assert response.status_code == 404
        assert response.json() == {"detail": "EvaluatorStreamer not found"}


def test_get_training_get_stream_error(mock_evaluator_streamer):
    with patch(
        "src.routers.data_handling.get_evaluator_stream_from_db",
        side_effect=Exception("Error getting stream"),
    ) as mock_get_evaluator_stream_from_db:
        response = client.get(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
        )

        mock_get_evaluator_stream_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        mock_evaluator_streamer.get_data.assert_not_called()

        assert response.status_code == 500
        assert response.json() == {
            "detail": "Error Getting Stream: Error getting stream"
        }


def test_get_training_data_error(mock_evaluator_streamer):
    mock_evaluator_streamer.get_data.side_effect = Exception(
        "Error getting training data"
    )
    with patch(
        "src.routers.data_handling.get_evaluator_stream_from_db",
        return_value=mock_evaluator_streamer,
    ) as mock_get_evaluator_stream_from_db, patch(
        "src.routers.data_handling.update_evaluator_stream", return_value=None
    ) as mock_update_evaluator_stream:
        response = client.get(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
        )

        mock_get_evaluator_stream_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        mock_evaluator_streamer.get_data.assert_called_once_with(
            UUID("12345678-1234-5678-1234-567812345678")
        )
        mock_update_evaluator_stream.assert_not_called()

        assert response.status_code == 500
        assert response.json() == {
            "detail": "Error Getting Training Data: Error getting training data"
        }
