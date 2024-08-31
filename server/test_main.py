import pytest
from unittest.mock import call, patch, MagicMock
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Server is running, STATUS": "HEALTHY"}

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
      with patch("main.dataset_map") as mock_dataset_map, \
            patch("main.SlidingWindowSetting") as mock_sliding_window_setting, \
            patch("main.MetricEntry") as mock_metric_entry, \
            patch("main.EvaluatorStreamer") as mock_evaluator_streamer:

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
            mock_sliding_window_instance
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
    with patch("main.dataset_map") as mock_dataset_map:
      mock_dataset_map.__getitem__().return_value.load.side_effect = Exception("Load error")

      response = client.post("/streams", json=valid_stream)

      assert mock_dataset_map.__getitem__().call_count == 1
      assert mock_dataset_map.__getitem__().return_value.load.call_count == 1

      assert response.status_code == 500
      assert response.json() == {"detail": "Error loading dataset: Load error"}

def test_create_stream_error_setting_sliding_window(valid_stream):
    with patch("main.dataset_map") as mock_dataset_map, \
         patch("main.SlidingWindowSetting", side_effect=Exception("Sliding window error")):

        response = client.post("/streams", json=valid_stream)

        assert mock_dataset_map.__getitem__().call_count == 1

        assert response.status_code == 500
        assert response.json() == {"detail": "Error setting up sliding window: Sliding window error"}

def test_create_stream_error_creating_metrics(valid_stream):
    with patch("main.dataset_map") as mock_dataset_map, \
         patch("main.SlidingWindowSetting") as mock_sliding_window_setting, \
         patch("main.MetricEntry", side_effect=Exception("Metrics error")):

        response = client.post("/streams", json=valid_stream)

        assert mock_dataset_map.__getitem__().call_count == 1
        assert mock_sliding_window_setting.call_count == 1

        assert response.status_code == 500
        assert response.json() == {"detail": "Error creating metrics: Metrics error"}

def test_create_stream_error_creating_evaluator_streamer(valid_stream):
    with patch("main.dataset_map") as mock_dataset_map, \
         patch("main.SlidingWindowSetting") as mock_sliding_window_setting, \
         patch("main.MetricEntry") as mock_metric_entry, \
         patch("main.EvaluatorStreamer", side_effect=Exception("Evaluator streamer error")):

        response = client.post("/streams", json=valid_stream)

        assert mock_dataset_map.__getitem__().call_count == 1
        assert mock_sliding_window_setting.call_count == 1
        assert mock_metric_entry.call_count == 2
  
        assert response.status_code == 500
        assert response.json() == {"detail": "Error creating evaluator streamer: Evaluator streamer error"}