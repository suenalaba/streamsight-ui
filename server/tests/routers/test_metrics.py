import json
from unittest.mock import MagicMock, call, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


@pytest.fixture
def mock_evaluator_streamer():
    mock = MagicMock()
    mock.metric_results.side_effect = lambda metric_type: MagicMock(
        to_json=lambda: json.dumps({f"{metric_type}_metric": "value"})
    )
    return mock


def test_get_metrics_valid(mock_evaluator_streamer):
    with patch(
        "src.routers.metrics.get_evaluator_stream_from_db"
    ) as mock_get_from_db, patch(
        "src.routers.metrics.update_evaluator_stream"
    ) as mock_update_evaluator_stream:
        mock_get_from_db.return_value = mock_evaluator_streamer
        mock_update_evaluator_stream.return_value = None

        response = client.get("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics")

        mock_get_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        mock_evaluator_streamer.metric_results.assert_has_calls(
            [call("micro"), call("macro")]
        )
        mock_update_evaluator_stream.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"), mock_evaluator_streamer
        )

        assert response.status_code == 200
        response_data = json.loads(response.json())
        assert response_data == {
            "micro_metrics": {"micro_metric": "value"},
            "macro_metrics": {"macro_metric": "value"},
        }


def test_get_metrics_invalid_stream_id(mock_evaluator_streamer):
    response = client.get("/streams/invalid-uuid/metrics")

    mock_evaluator_streamer.metric_results.assert_not_called()

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}


def test_get_metrics_evaluator_not_found(mock_evaluator_streamer):
    with patch("src.routers.metrics.get_evaluator_stream_from_db") as mock_get_from_db:
        mock_get_from_db.return_value = None
        response = client.get("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics")

        mock_get_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        mock_evaluator_streamer.metric_results.assert_not_called()

        assert response.status_code == 404
        assert response.json() == {"detail": "EvaluatorStreamer not found"}


def test_get_metrics_error_fetching_from_db(mock_evaluator_streamer):
    with patch(
        "src.routers.metrics.get_evaluator_stream_from_db",
        side_effect=Exception("Error fetching from DB"),
    ) as mock_get_from_db:
        response = client.get("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics")

        mock_get_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        mock_evaluator_streamer.metric_results.assert_not_called()

        assert response.status_code == 500
        assert response.json() == {
            "detail": "Error Getting Stream: Error fetching from DB"
        }


def test_get_metrics_internal_error(mock_evaluator_streamer):
    with patch(
        "src.routers.metrics.get_evaluator_stream_from_db"
    ) as mock_get_from_db, patch(
        "src.routers.metrics.update_evaluator_stream"
    ) as mock_update_evaluator_stream:
        mock_get_from_db.return_value = mock_evaluator_streamer

        # first call to metric_results throws an error
        mock_evaluator_streamer.metric_results.side_effect = Exception("Internal error")

        response = client.get("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics")

        mock_get_from_db.assert_called_once_with(
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
        )
        assert mock_evaluator_streamer.metric_results.call_count == 1
        mock_evaluator_streamer.metric_results.assert_called_once_with("micro")
        mock_update_evaluator_stream.assert_not_called()

        assert response.status_code == 500
        assert response.json() == {"detail": "Error Getting Metrics: Internal error"}
