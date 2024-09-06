import logging
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid import UUID
from io import BytesIO

from src.main import app
from src.constants import evaluator_stream_object_map

client = TestClient(app)

# silence multipart logger
logging.getLogger("multipart.multipart").setLevel(logging.WARNING)

@pytest.fixture
def mock_evaluator_streamer():
    mock = MagicMock()
    mock.get_data.return_value = pd.DataFrame({
        "interactionid": [1, 2],
        "uid": [1, 2],
        "iid": [1, 2],
        "ts": [1, 2]
    })
    mock.get_unlabeled_data.return_value = pd.DataFrame({
        "interactionid": [3, 4],
        "uid": [3, 4],
        "iid": [3, 4],
        "ts": [3, 4]
    })
    mock.get_algorithm_state.return_value.name = "PREDICTED"
    return mock

@pytest.fixture
def mock_algorithm():
    mock = MagicMock()
    mock.predict.return_value = pd.DataFrame({
        "interactionid": [5, 6],
        "uid": [5, 6],
        "iid": [5, 6],
        "ts": [5, 6]
    })
    mock.fit.return_value = None
    return mock

def test_submit_prediction_valid(mock_evaluator_streamer, mock_algorithm):
    with patch.dict(evaluator_stream_object_map, {UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"): mock_evaluator_streamer}), \
         patch("src.routers.predictions.ItemKNNStatic", return_value=mock_algorithm) as mock_item_knn_static:
        
        csv_content = "interactionid,uid,iid,ts\n1,1,1,1\n2,2,2,2"
        response = client.post(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
            files={"file": ("filename.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
        )

        mock_item_knn_static.assert_called_once()
        mock_item_knn_static.return_value.fit.assert_called_once()
        mock_item_knn_static.return_value.predict.assert_called_once()
        mock_evaluator_streamer.get_data.assert_called_once()
        mock_evaluator_streamer.get_unlabeled_data.assert_called_once()
        mock_evaluator_streamer.submit_prediction.assert_called_once()

        assert response.status_code == 200
        assert response.json() == {"status": True}

def test_submit_prediction_invalid_stream_id():
    csv_content = "interactionid,uid,iid,ts\n1,1,1,1\n2,2,2,2"
    response = client.post(
        "/streams/invalid-uuid/algorithms/12345678-1234-5678-1234-567812345678/predictions",
        files={"file": ("filename.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}

def test_submit_prediction_invalid_algorithm_id():
    csv_content = "interactionid,uid,iid,ts\n1,1,1,1\n2,2,2,2"
    response = client.post(
        "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-uuid/predictions",
        files={"file": ("filename.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}

def test_submit_prediction_evaluator_not_found():
    csv_content = "interactionid,uid,iid,ts\n1,1,1,1\n2,2,2,2"
    response = client.post(
        "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
        files={"file": ("filename.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "EvaluatorStreamer not found"}

def test_submit_prediction_missing_columns(mock_evaluator_streamer):
    with patch.dict(evaluator_stream_object_map, {UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"): mock_evaluator_streamer}):
        csv_content = "interactionid,uid,iid\n1,1,1\n2,2,2"
        response = client.post(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
            files={"file": ("filename.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "CSV file is missing required columns"}

def test_submit_prediction_internal_error(mock_evaluator_streamer, mock_algorithm):
    mock_evaluator_streamer.submit_prediction.side_effect = Exception("Internal error")
    
    with patch.dict(evaluator_stream_object_map, {UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"): mock_evaluator_streamer}), \
         patch("src.routers.predictions.ItemKNNStatic", return_value=mock_algorithm) as mock_item_knn_static:
        
        csv_content = "interactionid,uid,iid,ts\n1,1,1,1\n2,2,2,2"
        response = client.post(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
            files={"file": ("filename.csv", BytesIO(csv_content.encode('utf-8')), "text/csv")}
        )
        
        mock_item_knn_static.assert_called_once()
        mock_item_knn_static.return_value.fit.assert_called_once()
        mock_item_knn_static.return_value.predict.assert_called_once()
        mock_evaluator_streamer.get_data.assert_called_once()
        mock_evaluator_streamer.get_unlabeled_data.assert_called_once()
        mock_evaluator_streamer.submit_prediction.assert_called_once()

        assert response.status_code == 500
        assert response.json() == {"detail": "Error Submitting Prediction: Internal error"}
