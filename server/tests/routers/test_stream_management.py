import unittest
from unittest.mock import MagicMock, PropertyMock, call, patch
from uuid import UUID

from fastapi.testclient import TestClient

from src.main import app
from src.utils.db_utils import GetEvaluatorStreamErrorException
from src.utils.uuid_utils import InvalidUUIDException

client = TestClient(app)


class TestCreateStream(unittest.TestCase):
    def setUp(self):
        self.valid_stream = {
            "dataset_id": "amazon_music",
            "top_k": 10,
            "metrics": ["PrecisionK", "RecallK"],
            "background_t": 1406851200,
            "window_size": 25920000,
            "n_seq_data": 3,
        }
        self.invalid_dataset_stream = {
            "dataset_id": "invalid_dataset",
            "top_k": 10,
            "metrics": ["PrecisionK", "RecallK"],
            "background_t": 1406851200,
            "window_size": 25920000,
            "n_seq_data": 3,
        }
        self.invalid_metric_stream = {
            "dataset_id": "amazon_music",
            "top_k": 10,
            "metrics": ["InvalidMetric"],
            "background_t": 1406851200,
            "window_size": 60 * 60 * 24 * 300,
            "n_seq_data": 3,
        }
        self.mock_sliding_window_instance = self.get_mock_sliding_window_instance()
        self.mock_evaluator_stream_instance = self.get_mock_evaluator_stream_instance()
        self.mock_dataset_instance = self.get_mock_dataset_instance()

    def get_mock_sliding_window_instance(self):
        mock = MagicMock()
        mock.split.return_value = ""
        return mock

    def get_mock_evaluator_stream_instance(self):
        mock = MagicMock()
        return mock

    def get_mock_dataset_instance(self):
        mock = MagicMock()
        mock().load.return_value = "data"
        return mock

    def test_create_stream_valid(self):
        with patch(
            "src.routers.stream_management.dataset_map",
            **{"__getitem__.return_value": self.mock_dataset_instance},
        ) as mock_dataset_map, patch(
            "src.routers.stream_management.SlidingWindowSetting",
            return_value=self.mock_sliding_window_instance,
        ) as mock_sliding_window_setting, patch(
            "src.routers.stream_management.MetricEntry",
            side_effect=["PrecisionK", "RecallK"],
        ) as mock_metric_entry, patch(
            "src.routers.stream_management.EvaluatorStreamer",
            return_value=self.mock_evaluator_stream_instance,
        ) as mock_evaluator_streamer, patch(
            "src.routers.stream_management.write_evaluator_stream_to_db",
            return_value="336e4cb7-861b-4870-8c29-3ffc530711ef",
        ) as mock_write_to_db:
            response = client.post("/streams", json=self.valid_stream)

            mock_dataset_map.__getitem__.assert_called_once_with("amazon_music")
            self.mock_dataset_instance().load.assert_called_once()

            mock_sliding_window_setting.assert_called_once_with(
                background_t=1406851200,
                window_size=60 * 60 * 24 * 300,  # day times N
                n_seq_data=3,
                top_K=10,
            )
            self.mock_sliding_window_instance.split.assert_called_once_with("data")

            assert mock_metric_entry.call_count == 2
            expected_calls = [call("PrecisionK", K=10), call("RecallK", K=10)]
            mock_metric_entry.assert_has_calls(expected_calls)

            mock_evaluator_streamer.assert_called_once_with(
                ["PrecisionK", "RecallK"], self.mock_sliding_window_instance, 10
            )

            mock_write_to_db.assert_called_once_with(
                self.mock_evaluator_stream_instance
            )

            assert response.status_code == 200
            assert response.json() == {
                "evaluator_stream_id": "336e4cb7-861b-4870-8c29-3ffc530711ef"
            }

    def test_create_stream_invalid_dataset(self):
        response = client.post("/streams", json=self.invalid_dataset_stream)
        assert response.status_code == 404
        assert response.json() == {"detail": "Invalid Dataset ID"}

    def test_create_stream_invalid_metric(self):
        response = client.post("/streams", json=self.invalid_metric_stream)
        assert response.status_code == 422
        assert (
            response.json()["detail"][0]["msg"]
            == "Input should be 'PrecisionK', 'RecallK' or 'DCGK'"
        )

    def test_create_stream_error_loading_dataset(self):
        with patch("src.routers.stream_management.dataset_map") as mock_dataset_map:
            mock_dataset_map.__getitem__().return_value.load.side_effect = Exception(
                "Load error"
            )

            response = client.post("/streams", json=self.valid_stream)

            assert mock_dataset_map.__getitem__().call_count == 1
            assert mock_dataset_map.__getitem__().return_value.load.call_count == 1

            assert response.status_code == 500
            assert response.json() == {"detail": "Error loading dataset: Load error"}

    def test_create_stream_error_setting_sliding_window(self):
        with patch(
            "src.routers.stream_management.dataset_map"
        ) as mock_dataset_map, patch(
            "src.routers.stream_management.SlidingWindowSetting",
            side_effect=Exception("Sliding window error"),
        ):
            response = client.post("/streams", json=self.valid_stream)

            assert mock_dataset_map.__getitem__().call_count == 1

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error setting up sliding window: Sliding window error"
            }

    def test_create_stream_error_creating_metrics(self):
        with patch(
            "src.routers.stream_management.dataset_map"
        ) as mock_dataset_map, patch(
            "src.routers.stream_management.SlidingWindowSetting"
        ) as mock_sliding_window_setting, patch(
            "src.routers.stream_management.MetricEntry",
            side_effect=Exception("Metrics error"),
        ):
            response = client.post("/streams", json=self.valid_stream)

            assert mock_dataset_map.__getitem__().call_count == 1
            assert mock_sliding_window_setting.call_count == 1

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error creating metrics: Metrics error"
            }

    def test_create_stream_error_creating_evaluator_streamer(self):
        with patch(
            "src.routers.stream_management.dataset_map"
        ) as mock_dataset_map, patch(
            "src.routers.stream_management.SlidingWindowSetting"
        ) as mock_sliding_window_setting, patch(
            "src.routers.stream_management.MetricEntry"
        ) as mock_metric_entry, patch(
            "src.routers.stream_management.EvaluatorStreamer",
            side_effect=Exception("Evaluator streamer error"),
        ):
            response = client.post("/streams", json=self.valid_stream)

            assert mock_dataset_map.__getitem__().call_count == 1
            assert mock_sliding_window_setting.call_count == 1
            assert mock_metric_entry.call_count == 2

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error creating evaluator streamer: Evaluator streamer error"
            }


class TestGetStreamSettings(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_stream = self.create_mock_evaluator_stream()
        self.unsupported_mock_evaluator_stream = (
            self.create_unsupported_mock_evaluator_stream()
        )

    def create_mock_evaluator_stream(self):
        mock = MagicMock()
        mock.metric_k = 10
        sliding_window_setting_mock = MagicMock()
        type(sliding_window_setting_mock).n_seq_data = PropertyMock(return_value=100)
        type(sliding_window_setting_mock).window_size = PropertyMock(return_value=50)
        type(sliding_window_setting_mock).t = PropertyMock(return_value=5)
        type(sliding_window_setting_mock).top_K = PropertyMock(return_value=10)

        type(mock.setting)._sliding_window_setting = PropertyMock(return_value=True)
        mock.setting = sliding_window_setting_mock
        return mock

    def create_unsupported_mock_evaluator_stream(self):
        mock = MagicMock()
        mock.metric_k = 10
        sliding_window_setting_mock = MagicMock()
        type(sliding_window_setting_mock).n_seq_data = PropertyMock(return_value=100)
        type(sliding_window_setting_mock).window_size = PropertyMock(return_value=50)
        type(sliding_window_setting_mock).t = PropertyMock(return_value=5)
        type(sliding_window_setting_mock).top_K = PropertyMock(return_value=10)
        type(sliding_window_setting_mock)._sliding_window_setting = PropertyMock(
            return_value=False
        )
        mock.setting = sliding_window_setting_mock
        return mock

    def test_get_stream_settings_valid(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/settings"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 200
            assert response.json() == {
                "n_seq_data": 100,
                "window_size": 50,
                "background_t": 5,
                "top_k": 10,
            }

    def test_get_stream_setting_not_supported(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.unsupported_mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/settings"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 501
            assert response.json() == {
                "detail": "Other settings are currently not supported"
            }

    def test_get_stream_settings_invalid_uuid(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException(),
        ) as mock_get_uuid_obj:
            response = client.get("/streams/invalid_uuid/settings")

            mock_get_uuid_obj.assert_called_once_with("invalid_uuid")
            mock_get_from_db.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_stream_settings_stream_not_found(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/settings"
            )
            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream from database"
            }

    def test_get_stream_settings_error(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=Exception("Error fetching from DB"),
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/settings"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert response.status_code == 500
            assert response.json() == {"detail": "Error fetching from DB"}


class TestGetStream(unittest.TestCase):
    def setUp(self):
        self.valid_mock_evaluator_stream = self.get_mock_evaluator_stream()

    def get_mock_evaluator_stream(self):
        mock = MagicMock()
        mock.metric_k = 10
        return mock

    def test_get_stream_valid(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            return_value=self.valid_mock_evaluator_stream,
        ) as mock_get_from_db:
            response = client.get("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef")

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 200
            assert response.json() == 10

    def test_get_stream_invalid_uuid(self):
        response = client.get("/streams/invalid_uuid")
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_stream_stream_not_found(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            return_value=None,
        ) as mock_get_from_db:
            response = client.get("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef")

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_stream_failed_to_get_from_db(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            side_effect=Exception("Failed to fetch from DB"),
        ) as mock_get_from_db:
            response = client.get("/streams/336e4cb7-861b-4870-8c29-3ffc530711ef")

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Getting Stream: Failed to fetch from DB"
            }


class TestStartStream(unittest.TestCase):
    def setUp(self):
        self.valid_mock_evaluator_stream = self.create_mock_evaluator_streamer(
            return_value=""
        )
        self.already_started_mock_evaluator_stream = (
            self.create_mock_evaluator_streamer(
                side_effect=ValueError("Cannot start the stream again")
            )
        )
        self.invalid_mock_evaluator_stream = self.create_mock_evaluator_streamer(
            side_effect=Exception("Stream starting error")
        )

    def create_mock_evaluator_streamer(self, side_effect=None, return_value=None):
        mock = MagicMock()
        mock.start_stream.side_effect = side_effect
        mock.start_stream.return_value = return_value
        return mock

    def test_start_stream_valid(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            return_value=self.valid_mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_evaluator_stream"
        ) as mock_update_evaluator_stream:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert self.valid_mock_evaluator_stream.start_stream.call_count == 1
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.valid_mock_evaluator_stream,
            )

            assert response.status_code == 200
            assert response.json() == {"status": True}

    def test_start_stream_invalid_uuid(self):
        response = client.post("/streams/invalid_uuid/start")
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid UUID format"}

    def test_start_stream_stream_not_found(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            return_value=None,
        ) as mock_get_from_db:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_start_stream_failed_to_get_from_db(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            side_effect=Exception("Failed to fetch from DB"),
        ) as mock_get_from_db:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Getting Stream: Failed to fetch from DB"
            }

    def test_start_stream_that_has_already_started(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            return_value=self.already_started_mock_evaluator_stream,
        ) as mock_get_from_db:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert (
                self.already_started_mock_evaluator_stream.start_stream.call_count == 1
            )

            assert response.status_code == 409
            assert response.json() == {
                "detail": "Error Starting Stream: Cannot start the stream again"
            }

    def test_start_stream_error(self):
        with patch(
            "src.routers.stream_management.get_evaluator_stream_from_db",
            return_value=self.invalid_mock_evaluator_stream,
        ) as mock_get_from_db:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert self.invalid_mock_evaluator_stream.start_stream.call_count == 1

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Starting Stream: Stream starting error"
            }
