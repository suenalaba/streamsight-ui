import unittest
from unittest.mock import MagicMock, PropertyMock, call, patch
from uuid import UUID

from fastapi.testclient import TestClient

from src.main import app
from src.supabase_client.authentication import is_user_authenticated
from src.utils.db_utils import DatabaseErrorException, GetEvaluatorStreamErrorException
from src.utils.uuid_utils import InvalidUUIDException

client = TestClient(app)


class TestCreateStream(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[is_user_authenticated] = (
            self.mock_is_user_authenticated
        )
        self.mock_user_id = "mock_user_id"
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

    def mock_is_user_authenticated(self):
        return self.mock_user_id

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
            "src.routers.stream_management.write_stream_to_db",
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
                self.mock_evaluator_stream_instance,
                "amazon_music",
                self.mock_user_id,
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
            == "Input should be 'PrecisionK', 'RecallK', 'DCGK', 'NDCGK' or 'HitK'"
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

    def test_create_stream_error_write_stream_to_db(self):
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
            "src.routers.stream_management.write_stream_to_db",
            side_effect=DatabaseErrorException("error writing to db"),
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
                self.mock_evaluator_stream_instance,
                "amazon_music",
                self.mock_user_id,
            )

            assert response.status_code == 500
            assert response.json() == {"detail": "error writing to db"}


class TestGetStreamStatus(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_stream_not_started = (
            self.get_mock_evaluator_stream_not_started()
        )
        self.mock_evaluator_stream_in_progress = (
            self.get_mock_evaluator_stream_in_progress()
        )
        self.mock_evaluator_stream_completed = (
            self.get_mock_evaluator_stream_completed()
        )

    def get_mock_evaluator_stream_not_started(self):
        mock = MagicMock()
        mock.has_started = False
        return mock

    def get_mock_evaluator_stream_in_progress(self):
        mock = MagicMock()
        mock.has_started = True
        mock_completed = MagicMock()
        mock_completed.name = "COMPLETED"
        mock_ready = MagicMock()
        mock_ready.name = "READY"
        mock.get_all_algorithm_status.return_value = {
            "algorithm1": mock_completed,
            "algorithm2": mock_ready,
        }
        return mock

    def get_mock_evaluator_stream_completed(self):
        mock = MagicMock()
        mock.has_started = True
        mock_completed = MagicMock()
        mock_completed.name = "COMPLETED"
        mock.get_all_algorithm_status.return_value = {
            "algorithm1": mock_completed,
            "algorithm2": mock_completed,
        }
        return mock

    def test_get_stream_not_started(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.mock_evaluator_stream_not_started,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/status"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 200
            assert response.json() == {
                "stream_id": "336e4cb7-861b-4870-8c29-3ffc530711ef",
                "status": "NOT_STARTED",
            }

    def test_get_stream_in_progress(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.mock_evaluator_stream_in_progress,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/status"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 200
            assert response.json() == {
                "stream_id": "336e4cb7-861b-4870-8c29-3ffc530711ef",
                "status": "IN_PROGRESS",
            }

    def test_get_stream_completed(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.mock_evaluator_stream_completed,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/status"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 200
            assert response.json() == {
                "stream_id": "336e4cb7-861b-4870-8c29-3ffc530711ef",
                "status": "COMPLETED",
            }

    def test_get_stream_invalid_uuid(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException(),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.mock_evaluator_stream_not_started,
        ) as mock_get_from_db:
            response = client.get("/streams/invalid_uuid/status")

            mock_get_uuid_obj.assert_called_once_with("invalid_uuid")
            mock_get_from_db.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_stream_stream_not_found(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="Evaluator stream not found", status_code=404
            ),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/status"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 404
            assert response.json() == {"detail": "Evaluator stream not found"}

    def test_get_stream_failed_to_get_from_db(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/status"
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


class TestGetUserStreamStatuses(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[is_user_authenticated] = (
            self.mock_is_user_authenticated
        )
        self.mock_user_id = "mock_user_id"
        self.mock_stream_uuids = [
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
            UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ]
        self.mock_evaluator_stream_not_started = (
            self.get_mock_evaluator_stream_not_started()
        )
        self.mock_evaluator_stream_in_progress = (
            self.get_mock_evaluator_stream_in_progress()
        )
        self.mock_evaluator_stream_completed = (
            self.get_mock_evaluator_stream_completed()
        )

    def get_mock_evaluator_stream_not_started(self):
        mock = MagicMock()
        mock.has_started = False
        return mock

    def get_mock_evaluator_stream_in_progress(self):
        mock = MagicMock()
        mock.has_started = True
        mock_completed = MagicMock()
        mock_completed.name = "COMPLETED"
        mock_ready = MagicMock()
        mock_ready.name = "READY"
        mock.get_all_algorithm_status.return_value = {
            "algorithm1": mock_completed,
            "algorithm2": mock_ready,
        }
        return mock

    def get_mock_evaluator_stream_completed(self):
        mock = MagicMock()
        mock.has_started = True
        mock_completed = MagicMock()
        mock_completed.name = "COMPLETED"
        mock.get_all_algorithm_status.return_value = {
            "algorithm1": mock_completed,
            "algorithm2": mock_completed,
        }
        return mock

    def mock_is_user_authenticated(self):
        return self.mock_user_id

    def test_get_user_stream_statuses_valid(self):
        with patch(
            "src.routers.stream_management.get_user_stream_ids_from_db",
            return_value=self.mock_stream_uuids,
        ) as mock_get_user_stream_ids, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=[
                self.mock_evaluator_stream_not_started,
                self.mock_evaluator_stream_in_progress,
                self.mock_evaluator_stream_completed,
            ],
        ) as mock_get_from_db:
            response = client.get("/streams/user")

            mock_get_user_stream_ids.assert_called_once_with(self.mock_user_id)

            assert mock_get_from_db.call_count == 3
            expected_calls = [
                call(UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")),
                call(UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")),
                call(UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")),
            ]
            mock_get_from_db.assert_has_calls(expected_calls)

            assert response.status_code == 200
            assert response.json() == [
                {
                    "stream_id": "336e4cb7-861b-4870-8c29-3ffc530711ef",
                    "status": "NOT_STARTED",
                },
                {
                    "stream_id": "336e4cb7-861b-4870-8c29-3ffc530711ef",
                    "status": "IN_PROGRESS",
                },
                {
                    "stream_id": "336e4cb7-861b-4870-8c29-3ffc530711ef",
                    "status": "COMPLETED",
                },
            ]

    def test_get_user_stream_statuses_error_getting_user_stream_ids(self):
        with patch(
            "src.routers.stream_management.get_user_stream_ids_from_db",
            side_effect=DatabaseErrorException(),
        ) as mock_get_user_stream_ids, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=[
                self.mock_evaluator_stream_not_started,
                self.mock_evaluator_stream_in_progress,
                self.mock_evaluator_stream_completed,
            ],
        ) as mock_get_from_db:
            response = client.get("/streams/user")

            mock_get_user_stream_ids.assert_called_once_with(self.mock_user_id)
            assert mock_get_from_db.call_count == 0

            assert response.status_code == 500
            assert response.json() == {"detail": "Database CRUD Error"}

    def test_get_user_stream_statuses_error_getting_stream_from_db(self):
        with patch(
            "src.routers.stream_management.get_user_stream_ids_from_db",
            return_value=self.mock_stream_uuids,
        ) as mock_get_user_stream_ids, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_from_db:
            response = client.get("/streams/user")

            mock_get_user_stream_ids.assert_called_once_with(self.mock_user_id)
            assert mock_get_from_db.call_count == 1

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream from database"
            }

    def test_get_user_stream_statuses_error(self):
        with patch(
            "src.routers.stream_management.get_user_stream_ids_from_db",
            side_effect=Exception(),
        ) as mock_get_user_stream_ids, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=[
                self.mock_evaluator_stream_not_started,
                self.mock_evaluator_stream_in_progress,
                self.mock_evaluator_stream_completed,
            ],
        ) as mock_get_from_db:
            response = client.get("/streams/user")

            mock_get_user_stream_ids.assert_called_once_with(self.mock_user_id)
            assert mock_get_from_db.call_count == 0

            assert response.status_code == 500
            assert response.json() == {"detail": "Error getting user stream statuses: "}


class TestGetStreamSettings(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_stream = self.create_mock_evaluator_stream()
        self.unsupported_mock_evaluator_stream = (
            self.create_unsupported_mock_evaluator_stream()
        )
        self.mock_dataset_id = "mock_dataset_id"

    def create_mock_evaluator_stream(self):
        mock = MagicMock()
        mock.metric_k = 10
        sliding_window_setting_mock = MagicMock()
        type(sliding_window_setting_mock).n_seq_data = PropertyMock(return_value=100)
        type(sliding_window_setting_mock).window_size = PropertyMock(return_value=50)
        type(sliding_window_setting_mock).t = PropertyMock(return_value=5)
        type(sliding_window_setting_mock).top_K = PropertyMock(return_value=10)
        type(sliding_window_setting_mock).num_split = PropertyMock(return_value=2)

        type(mock.setting)._sliding_window_setting = PropertyMock(return_value=True)
        mock.setting = sliding_window_setting_mock
        mock._run_step = 1

        mock_precision = MagicMock()
        mock_precision.name = "PrecisionK"
        mock_recall = MagicMock()
        mock_recall.name = "RecallK"
        mock.metric_entries = [mock_precision, mock_recall]

        return mock

    def create_unsupported_mock_evaluator_stream(self):
        mock = MagicMock()
        mock.metric_k = 10
        sliding_window_setting_mock = MagicMock()
        type(sliding_window_setting_mock).n_seq_data = PropertyMock(return_value=100)
        type(sliding_window_setting_mock).window_size = PropertyMock(return_value=50)
        type(sliding_window_setting_mock).t = PropertyMock(return_value=5)
        type(sliding_window_setting_mock).top_K = PropertyMock(return_value=10)
        type(sliding_window_setting_mock).num_split = PropertyMock(return_value=2)
        type(sliding_window_setting_mock)._sliding_window_setting = PropertyMock(
            return_value=False
        )
        mock.setting = sliding_window_setting_mock
        mock._run_step = 1

        mock_precision = MagicMock()
        mock_precision.name = "PrecisionK"
        mock_recall = MagicMock()
        mock_recall.name = "RecallK"
        mock.metric_entries = [mock_precision, mock_recall]

        return mock

    def test_get_stream_settings_valid(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db_with_dataset_id",
            return_value=(self.mock_evaluator_stream, self.mock_dataset_id),
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
                "metrics": ["PrecisionK", "RecallK"],
                "dataset_id": self.mock_dataset_id,
                "number_of_windows": 2,
                "current_window": 1,
            }

    def test_get_stream_setting_not_supported(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db_with_dataset_id",
            return_value=(self.unsupported_mock_evaluator_stream, self.mock_dataset_id),
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
            "src.routers.stream_management.get_stream_from_db_with_dataset_id",
            return_value=(self.mock_evaluator_stream, self.mock_dataset_id),
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
            "src.routers.stream_management.get_stream_from_db_with_dataset_id",
            side_effect=GetEvaluatorStreamErrorException(
                message="Evaluator stream not found", status_code=404
            ),
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

            assert response.status_code == 404
            assert response.json() == {"detail": "Evaluator stream not found"}

    def test_get_stream_settings_get_stream_from_db_error(self):
        with patch(
            "src.routers.stream_management.get_stream_from_db_with_dataset_id",
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
            "src.routers.stream_management.get_stream_from_db_with_dataset_id",
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
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.valid_mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_stream"
        ) as mock_update_evaluator_stream:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
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
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException(),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.valid_mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_stream"
        ) as mock_update_evaluator_stream:
            response = client.post("/streams/invalid_uuid/start")

            mock_get_uuid_obj.assert_called_once_with("invalid_uuid")
            mock_get_from_db.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_start_stream_stream_not_found(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="EvaluatorStreamer not found", status_code=404
            ),
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_stream"
        ) as mock_update_evaluator_stream:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_start_stream_failed_to_get_from_db(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_stream"
        ) as mock_update_evaluator_stream:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream from database"
            }

    def test_start_stream_that_has_already_started(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.already_started_mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_stream"
        ) as mock_update_evaluator_stream:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert (
                self.already_started_mock_evaluator_stream.start_stream.call_count == 1
            )
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 409
            assert response.json() == {
                "detail": "Error Starting Stream: Cannot start the stream again"
            }

    def test_start_stream_error(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.invalid_mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_stream"
        ) as mock_update_evaluator_stream:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert self.invalid_mock_evaluator_stream.start_stream.call_count == 1
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Starting Stream: Stream starting error"
            }

    def test_start_stream_update_stream_error(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.get_stream_from_db",
            return_value=self.valid_mock_evaluator_stream,
        ) as mock_get_from_db, patch(
            "src.routers.stream_management.update_stream",
            side_effect=DatabaseErrorException("Update stream error"),
        ) as mock_update_evaluator_stream:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/start"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert self.valid_mock_evaluator_stream.start_stream.call_count == 1
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.valid_mock_evaluator_stream,
            )

            assert response.status_code == 500
            assert response.json() == {"detail": "Update stream error"}


class TestCheckStreamAccess(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[is_user_authenticated] = (
            self.mock_is_user_authenticated
        )
        self.mock_user_id = "mock_user_id"
        self.mock_evaluator_stream = MagicMock()
        self.mock_evaluator_stream.user_id = "mock_user_id"
        self.mock_user_id = "mock_user_id"

    def mock_is_user_authenticated(self):
        return self.mock_user_id

    def test_has_stream_access_(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.is_user_stream",
            return_value=True,
        ) as mock_is_user_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/check_access"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_is_user_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"), self.mock_user_id
            )

            assert response.status_code == 200
            assert response.json()

    def test_no_stream_access_(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.is_user_stream",
            return_value=False,
        ) as mock_is_user_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/check_access"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_is_user_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"), self.mock_user_id
            )

            assert response.status_code == 200
            assert not response.json()

    def test_check_stream_access_invalid_uuid(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException(),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.is_user_stream",
        ) as mock_is_user_stream:
            response = client.get("/streams/invalid_uuid/check_access")

            mock_get_uuid_obj.assert_called_once_with("invalid_uuid")
            mock_is_user_stream.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_check_stream_access_not_found(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.is_user_stream",
            side_effect=GetEvaluatorStreamErrorException(
                message="Evaluator stream not found", status_code=404
            ),
        ) as mock_is_user_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/check_access"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_is_user_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"), self.mock_user_id
            )

            assert response.status_code == 404
            assert response.json() == {"detail": "Evaluator stream not found"}

    def test_check_stream_access_error(self):
        with patch(
            "src.routers.stream_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.stream_management.is_user_stream",
            side_effect=Exception("Error fetching from DB"),
        ) as mock_is_user_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/check_access"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef",
            )

            mock_is_user_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"), self.mock_user_id
            )

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Checking Stream Access: Error fetching from DB"
            }


class TestGetDatasets(unittest.TestCase):
    def test_get_datasets(self):
        response = client.get("streams/datasets")

        assert response.status_code == 200
        assert response.json() == [
            "amazon_music",
            "amazon_book",
            "amazon_subscription_boxes",
            "amazon_movie",
            "yelp",
            "test",
            "movielens",
            "lastfm",
        ]
