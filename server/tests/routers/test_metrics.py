import unittest
from unittest.mock import MagicMock, call, patch
from uuid import UUID

import pandas as pd
from fastapi.testclient import TestClient

from src.main import app
from src.utils.db_utils import DatabaseErrorException, GetEvaluatorStreamErrorException
from src.utils.uuid_utils import InvalidUUIDException

client = TestClient(app)


class TestGetMetrics(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_streamer = self.get_mock_evaluator_streamer()
        self.mock_metric_error_evaluator_streamer = (
            self.get_mock_metric_error_evaluator_streamer()
        )
        self.mock_not_predicted_evaluator_streamer = (
            self.get_mock_not_predicted_evaluator_streamer()
        )

    def get_mock_evaluator_streamer(self):
        mock = MagicMock()
        micro_mock_data = pd.DataFrame(
            [
                {
                    "Algorithm": "algo_1",
                    "Metric": "accuracy",
                    "micro_score": 0.9,
                    "num_user": 100,
                },
                {
                    "Algorithm": "algo_2",
                    "Metric": "precision",
                    "micro_score": 0.8,
                    "num_user": 200,
                },
            ]
        )

        macro_mock_data = pd.DataFrame(
            [
                {
                    "Algorithm": "algo_1",
                    "Metric": "accuracy",
                    "macro_score": 0.85,
                    "num_window": 10,
                },
                {
                    "Algorithm": "algo_2",
                    "Metric": "precision",
                    "macro_score": 0.75,
                    "num_window": 20,
                },
            ]
        )

        mock.metric_results.side_effect = (
            lambda metric_type: micro_mock_data
            if metric_type == "micro"
            else macro_mock_data
        )
        return mock

    def get_mock_metric_error_evaluator_streamer(self):
        mock = MagicMock()
        mock.metric_results.side_effect = Exception("Internal error")
        return mock

    def get_mock_not_predicted_evaluator_streamer(self):
        mock = MagicMock()
        mock.has_predicted = False
        return mock

    def test_get_metrics_valid(self):
        with patch(
            "src.routers.metrics.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.metrics.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.metrics.update_stream",
            return_value=None,
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.metric_results.assert_has_calls(
                [call("micro"), call("macro")]
            )
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 200
            # response_data = json.loads(response.json())
            assert response.json() == {
                "micro_metrics": [
                    {
                        "algorithm_name": "algo",
                        "algorithm_id": "1",
                        "metric": "accuracy",
                        "micro_score": 0.9,
                        "num_user": 100,
                    },
                    {
                        "algorithm_name": "algo",
                        "algorithm_id": "2",
                        "metric": "precision",
                        "micro_score": 0.8,
                        "num_user": 200,
                    },
                ],
                "macro_metrics": [
                    {
                        "algorithm_name": "algo",
                        "algorithm_id": "1",
                        "metric": "accuracy",
                        "macro_score": 0.85,
                        "num_window": 10,
                    },
                    {
                        "algorithm_name": "algo",
                        "algorithm_id": "2",
                        "metric": "precision",
                        "macro_score": 0.75,
                        "num_window": 20,
                    },
                ],
            }

    def test_get_metrics_invalid_stream_id(self):
        with patch(
            "src.routers.metrics.get_stream_uuid_object",
            side_effect=InvalidUUIDException(),
        ) as mock_get_uuid_obj, patch(
            "src.routers.metrics.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.metrics.update_stream",
            return_value=None,
        ) as mock_update_evaluator_stream:
            response = client.get("/streams/invalid-uuid/metrics")

            mock_get_uuid_obj.assert_called_once_with("invalid-uuid")
            mock_get_from_db.assert_not_called()
            self.mock_evaluator_streamer.metric_results.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_metrics_evaluator_not_found(self):
        with patch(
            "src.routers.metrics.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.metrics.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="EvaluatorStreamer not found", status_code=404
            ),
        ) as mock_get_from_db, patch(
            "src.routers.metrics.update_stream",
            return_value=None,
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.metric_results.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_metrics_error_fetching_from_db(self):
        with patch(
            "src.routers.metrics.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.metrics.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_from_db, patch(
            "src.routers.metrics.update_stream",
            return_value=None,
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.metric_results.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream from database"
            }

    def test_get_metrics_internal_error(self):
        with patch(
            "src.routers.metrics.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.metrics.get_stream_from_db",
            return_value=self.mock_metric_error_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.metrics.update_stream",
            return_value=None,
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            assert (
                self.mock_metric_error_evaluator_streamer.metric_results.call_count == 1
            )
            self.mock_metric_error_evaluator_streamer.metric_results.assert_called_once_with(
                "micro"
            )
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Getting Metrics: Internal error"
            }

    def test_get_metrics_update_stream_error(self):
        with patch(
            "src.routers.metrics.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.metrics.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.metrics.update_stream",
            side_effect=DatabaseErrorException("Error updating stream"),
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.metric_results.assert_has_calls(
                [call("micro"), call("macro")]
            )
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 500
            assert response.json() == {"detail": "Error updating stream"}

    def test_get_metrics_not_predicted(self):
        with patch(
            "src.routers.metrics.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.metrics.get_stream_from_db",
            return_value=self.mock_not_predicted_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.metrics.update_stream",
            return_value=None,
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/metrics"
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_not_predicted_evaluator_streamer.metric_results.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 200
            assert response.json() == {
                "micro_metrics": [],
                "macro_metrics": [],
            }


class TestGetMetricsList(unittest.TestCase):
    def test_get_metrics_list(self):
        response = client.get("/metrics")

        assert response.status_code == 200
        assert response.json() == ["PrecisionK", "RecallK", "NDCGK", "DCGK", "HitK"]
