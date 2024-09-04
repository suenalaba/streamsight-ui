from uuid import UUID
import pytest
from unittest.mock import call, patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.constants import evaluator_stream_object_map

client = TestClient(app)

@pytest.fixture
def valid_stream():
    return {
        "dataset_id": "amazon_music",
        "top_k": 10,
        "metrics": ["PrecisionK", "RecallK"]
    }

@pytest.fixture
def invalid_dataset_stream():
    return {
        "dataset_id": "invalid_dataset",
        "top_k": 10,
        "metrics": ["PrecisionK", "RecallK"]
    }

@pytest.fixture
def invalid_metric_stream():
    return {
        "dataset_id": "amazon_music",
        "top_k": 10,
        "metrics": ["InvalidMetric"]
    }

def test_create_stream_valid(valid_stream):
      with patch("src.routers.stream_management.dataset_map") as mock_dataset_map, \
            patch("src.routers.stream_management.SlidingWindowSetting") as mock_sliding_window_setting, \
            patch("src.routers.stream_management.MetricEntry") as mock_metric_entry, \
            patch("src.routers.stream_management.EvaluatorStreamer") as mock_evaluator_streamer:

          # mock sliding window setting
          mock_sliding_window_instance = MagicMock()
          mock_sliding_window_setting.return_value = mock_sliding_window_instance
          mock_sliding_window_instance.split.return_value = ''

          # mock return values of MetricEntry calls
          mock_metric_entry.side_effect = ['PrecisionK', 'RecallK'] # return values of mock metric entry

          response = client.post("/streams", json=valid_stream)

          mock_dataset_map.__getitem__.assert_called_once_with("amazon_music")

          mock_sliding_window_setting.assert_called_once_with(
            background_t=1406851200,
            window_size=60 * 60 * 24 * 300,  # day times N
            n_seq_data=3,
            top_K=10
          )

          assert mock_metric_entry.call_count == 2
          expected_calls = [
            call("PrecisionK", K=10),
            call("RecallK", K=10)
        ]
          mock_metric_entry.assert_has_calls(expected_calls)

          mock_evaluator_streamer.assert_called_once_with(
            ['PrecisionK', 'RecallK'],
            mock_sliding_window_instance,
            10
          )

          assert response.status_code == 200
          assert "evaluator_stream_id" in response.json()

def test_create_stream_invalid_dataset(invalid_dataset_stream):
    response = client.post("/streams", json=invalid_dataset_stream)
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid Dataset ID"}

def test_create_stream_invalid_metric(invalid_metric_stream):
    response = client.post("/streams", json=invalid_metric_stream)
    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Input should be 'PrecisionK', 'RecallK' or 'DCGK'"

def test_create_stream_error_loading_dataset(valid_stream):
    with patch("src.routers.stream_management.dataset_map") as mock_dataset_map:
      mock_dataset_map.__getitem__().return_value.load.side_effect = Exception("Load error")

      response = client.post("/streams", json=valid_stream)

      assert mock_dataset_map.__getitem__().call_count == 1
      assert mock_dataset_map.__getitem__().return_value.load.call_count == 1

      assert response.status_code == 500
      assert response.json() == {"detail": "Error loading dataset: Load error"}

def test_create_stream_error_setting_sliding_window(valid_stream):
    with patch("src.routers.stream_management.dataset_map") as mock_dataset_map, \
         patch("src.routers.stream_management.SlidingWindowSetting", side_effect=Exception("Sliding window error")):

        response = client.post("/streams", json=valid_stream)

        assert mock_dataset_map.__getitem__().call_count == 1

        assert response.status_code == 500
        assert response.json() == {"detail": "Error setting up sliding window: Sliding window error"}

def test_create_stream_error_creating_metrics(valid_stream):
    with patch("src.routers.stream_management.dataset_map") as mock_dataset_map, \
         patch("src.routers.stream_management.SlidingWindowSetting") as mock_sliding_window_setting, \
         patch("src.routers.stream_management.MetricEntry", side_effect=Exception("Metrics error")):

        response = client.post("/streams", json=valid_stream)

        assert mock_dataset_map.__getitem__().call_count == 1
        assert mock_sliding_window_setting.call_count == 1

        assert response.status_code == 500
        assert response.json() == {"detail": "Error creating metrics: Metrics error"}

def test_create_stream_error_creating_evaluator_streamer(valid_stream):
    with patch("src.routers.stream_management.dataset_map") as mock_dataset_map, \
         patch("src.routers.stream_management.SlidingWindowSetting") as mock_sliding_window_setting, \
         patch("src.routers.stream_management.MetricEntry") as mock_metric_entry, \
         patch("src.routers.stream_management.EvaluatorStreamer", side_effect=Exception("Evaluator streamer error")):

        response = client.post("/streams", json=valid_stream)

        assert mock_dataset_map.__getitem__().call_count == 1
        assert mock_sliding_window_setting.call_count == 1
        assert mock_metric_entry.call_count == 2
  
        assert response.status_code == 500
        assert response.json() == {"detail": "Error creating evaluator streamer: Evaluator streamer error"}

def test_start_stream_valid():
    mock_evaluator_streamer_instance = MagicMock()
    mock_evaluator_streamer_instance.start_stream.return_value = ''

    evaluator_stream_object_map[UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")] = mock_evaluator_streamer_instance

    response = client.post("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start")
    
    assert mock_evaluator_streamer_instance.start_stream.call_count == 1
    assert response.status_code == 200
    assert response.json() == {"status": True}

    evaluator_stream_object_map.clear()

def test_start_stream_invalid_uuid():
    response = client.post("/streams/invalid_uuid/start")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid UUID format"}

def test_start_stream_stream_not_found():
    response = client.post("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start")
    assert response.status_code == 404
    assert response.json() == {"detail": "EvaluatorStreamer not found"}

def test_start_stream_that_has_already_started():
    mock_evaluator_streamer_instance = MagicMock()
    mock_evaluator_streamer_instance.start_stream.side_effect = ValueError("Cannot start the stream again")

    evaluator_stream_object_map[UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")] = mock_evaluator_streamer_instance

    response = client.post("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start")
    
    assert mock_evaluator_streamer_instance.start_stream.call_count == 1
    assert response.status_code == 409
    assert response.json() == {"detail": "Error Starting Stream: Cannot start the stream again"}

    evaluator_stream_object_map.clear()

def test_start_stream_error():
    mock_evaluator_streamer_instance = MagicMock()
    mock_evaluator_streamer_instance.start_stream.side_effect = Exception("Stream starting error")

    evaluator_stream_object_map[UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")] = mock_evaluator_streamer_instance

    response = client.post("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start")
    
    assert mock_evaluator_streamer_instance.start_stream.call_count == 1
    assert response.status_code == 500
    assert response.json() == {"detail": "Error Starting Stream: Stream starting error"}

    evaluator_stream_object_map.clear()
