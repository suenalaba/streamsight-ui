import logging
import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# silence multipart logger
logging.getLogger("multipart.multipart").setLevel(logging.WARNING)


class TestSubmitPrediction(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_streamer_predicted = (
            self.create_mock_evaluator_streamer_predicted()
        )
        self.mock_evaluator_streamer_completed = (
            self.create_mock_evaluator_streamer_completed()
        )
        self.mock_evaluator_streamer_submit_prediction_error = (
            self.create_mock_evaluator_streamer_submit_prediction_error()
        )
        self.mock_dataframe_record = self.create_mock_dataframe_record()
        self.mock_prediction_csr_matrix = self.create_mock_prediction_csr_matrix()
        self.mock_prediction_im = self.create_mock_prediction_im()

    def create_mock_evaluator_streamer_predicted(self):
        mock = MagicMock()
        mock.submit_prediction.return_value = None
        mock.get_algorithm_state.return_value.name = "PREDICTED"
        return mock

    def create_mock_evaluator_streamer_completed(self):
        mock = MagicMock()
        mock.submit_prediction.return_value = None
        mock.get_algorithm_state.return_value.name = "COMPLETED"
        return mock

    def create_mock_evaluator_streamer_submit_prediction_error(self):
        mock = MagicMock()
        mock.submit_prediction.side_effect = Exception("Error at submit_prediction()")
        return mock

    def create_mock_dataframe_record(self):
        return [{"interactionid": 12345, "uid": 67890, "iid": 54321, "ts": 1617181920}]

    def create_mock_prediction_csr_matrix(self):
        return {
            "data": [1, 2, 3, 4, 5, 6],
            "indices": [0, 2, 2, 0, 1, 2],
            "indptr": [0, 2, 3, 6],
            "shape": [3, 3],
        }

    def create_mock_prediction_im(self):
        return MagicMock()

    def test_submit_prediction_valid_df(self):
        with patch(
            "src.routers.predictions.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer_predicted,
        ) as mock_get_from_db, patch(
            "src.routers.predictions.InteractionMatrix",
            return_value=self.mock_prediction_im,
        ) as mock_interaction_matrix, patch(
            "src.routers.predictions.update_evaluator_stream", return_value=None
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
                json=self.mock_dataframe_record,
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            mock_interaction_matrix.assert_called_once()
            self.mock_evaluator_streamer_predicted.submit_prediction.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678"), self.mock_prediction_im
            )
            self.mock_evaluator_streamer_predicted.get_algorithm_state.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            mock_update_evaluator_streamer.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer_predicted,
            )

            assert response.status_code == 200
            assert response.json() == {"status": True}

    def test_submit_prediction_valid_csr_matrix(self):
        with patch(
            "src.routers.predictions.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer_completed,
        ) as mock_get_from_db, patch(
            "src.routers.predictions.InteractionMatrix",
            return_value=self.mock_prediction_im,
        ) as mock_interaction_matrix, patch(
            "src.routers.predictions.update_evaluator_stream", return_value=None
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
                json=self.mock_prediction_csr_matrix,
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            mock_interaction_matrix.assert_not_called()
            self.mock_evaluator_streamer_completed.submit_prediction.assert_called_once()
            self.mock_evaluator_streamer_completed.get_algorithm_state.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            mock_update_evaluator_streamer.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer_completed,
            )

            assert response.status_code == 200
            assert response.json() == {"status": True}

    def test_submit_prediction_invalid_stream_id(self):
        response = client.post(
            "/streams/invalid-uuid/algorithms/12345678-1234-5678-1234-567812345678/predictions",
            json=self.mock_dataframe_record,
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid UUID format"}

    def test_submit_prediction_invalid_algorithm_id(self):
        response = client.post(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-uuid/predictions",
            json=self.mock_dataframe_record,
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid UUID format"}

    def test_submit_prediction_evaluator_not_found(self):
        with patch(
            "src.routers.predictions.get_evaluator_stream_from_db", return_value=None
        ) as mock_get_from_db:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
                json=self.mock_dataframe_record,
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_submit_prediction_error_fetching_evaluator_from_db(self):
        with patch(
            "src.routers.predictions.get_evaluator_stream_from_db",
            side_effect=Exception("Error fetching from DB"),
        ) as mock_get_from_db:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
                json=self.mock_dataframe_record,
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream: Error fetching from DB"
            }

    def test_submit_df_prediction_data_error(self):
        with patch(
            "src.routers.predictions.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer_submit_prediction_error,
        ) as mock_get_from_db, patch(
            "src.routers.predictions.InteractionMatrix",
            return_value=self.mock_prediction_im,
        ) as mock_interaction_matrix:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
                json=self.mock_dataframe_record,
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            mock_interaction_matrix.assert_called_once()
            self.mock_evaluator_streamer_submit_prediction_error.submit_prediction.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678"), self.mock_prediction_im
            )

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Submitting Prediction: Error at submit_prediction()"
            }

    def test_submit_csr_matrix_prediction_data_error(self):
        with patch(
            "src.routers.predictions.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer_submit_prediction_error,
        ) as mock_get_from_db, patch(
            "src.routers.predictions.InteractionMatrix",
            return_value=self.mock_prediction_im,
        ) as mock_interaction_matrix:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
                json=self.mock_prediction_csr_matrix,
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer_submit_prediction_error.submit_prediction.assert_called_once()
            mock_interaction_matrix.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Submitting Prediction: Error at submit_prediction()"
            }

    def test_submit_prediction_invalid_format(self):
        with patch(
            "src.routers.predictions.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer_predicted,
        ) as mock_get_from_db:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/predictions",
                json={"invalid": "format"},
            )

            mock_get_from_db.assert_not_called()

            assert response.status_code == 422
