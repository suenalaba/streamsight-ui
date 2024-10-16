import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID

import pandas as pd
from fastapi.testclient import TestClient

from src.main import app
from src.utils.db_utils import DatabaseErrorException, GetEvaluatorStreamErrorException
from src.utils.uuid_utils import InvalidUUIDException

client = TestClient(app)


class TestGetTrainingData(unittest.TestCase):
    def setUp(self):
        self.mock_interaction_matrix = self.create_mock_interaction_matrix()
        self.mock_evaluator_streamer = self.create_mock_evaluator_streamer()
        self.mock_evaluator_streamer_error = self.create_mock_evaluator_streamer_error()

    def create_mock_interaction_matrix(self):
        mock = MagicMock()
        mock.shape = (3, 3)
        data = {
            "interactionid": [0, 1, 2, 3],
            "uid": [0, 1, 2, 0],
            "iid": [0, 0, 1, 2],
            "ts": [0, 1, 2, 3],
            "additional_feature_1": [10, 8, 2, 6],
        }

        # Create the DataFrame
        df = pd.DataFrame(data)
        mock.copy_df.return_value = df
        return mock

    def create_mock_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_data.return_value = self.mock_interaction_matrix
        return mock

    def create_mock_evaluator_streamer_error(self):
        mock = MagicMock()
        mock.get_data.side_effect = Exception("Error getting training data")
        return mock

    def test_get_training_data_valid(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            self.mock_interaction_matrix.copy_df.assert_called_once()
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
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

    def test_get_training_data_additional_features(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data?includeAdditionalFeatures=true"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            self.mock_interaction_matrix.copy_df.assert_called_once()
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 200
            assert response.json() == {
                "shape": [3, 3],
                "training_data": [
                    {
                        "interactionid": 0,
                        "uid": 0,
                        "iid": 0,
                        "ts": 0,
                        "additional_feature_1": 10,
                    },
                    {
                        "interactionid": 1,
                        "uid": 1,
                        "iid": 0,
                        "ts": 1,
                        "additional_feature_1": 8,
                    },
                    {
                        "interactionid": 2,
                        "uid": 2,
                        "iid": 1,
                        "ts": 2,
                        "additional_feature_1": 2,
                    },
                    {
                        "interactionid": 3,
                        "uid": 0,
                        "iid": 2,
                        "ts": 3,
                        "additional_feature_1": 6,
                    },
                ],
            }

    def test_get_training_data_invalid_stream_uuid(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            side_effect=InvalidUUIDException("Invalid UUID format"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/invalid-stream-uuid/algorithms/12345678-1234-5678-1234-567812345678/training-data"
            )

            mock_get_stream_uuid.assert_called_once_with("invalid-stream-uuid")
            mock_get_algo_uuid.assert_not_called()
            mock_get_evaluator_stream_from_db.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_training_data_invalid_algo_uuid(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            side_effect=InvalidUUIDException("Invalid UUID format"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-algo-uuid/training-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with("invalid-algo-uuid")
            mock_get_evaluator_stream_from_db.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_training_data_stream_not_found(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="EvaluatorStreamer not found", status_code=404
            ),
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_data.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_training_get_stream_error(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_data.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream from database"
            }

    def test_get_training_data_error(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer_error,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer_error.get_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Getting Training Data: Error getting training data"
            }

    def test_get_training_data_error_updating_stream(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream",
            side_effect=DatabaseErrorException("error updating db"),
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/training-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 500
            assert response.json() == {"detail": "error updating db"}


class TestGetUnlabeledData(unittest.TestCase):
    def setUp(self):
        self.mock_interaction_matrix = self.create_mock_interaction_matrix()
        self.mock_evaluator_streamer = self.create_mock_evaluator_streamer()
        self.mock_evaluator_streamer_error = self.create_mock_evaluator_streamer_error()

    def create_mock_interaction_matrix(self):
        mock = MagicMock()
        mock.shape = (3, 3)
        data = {
            "interactionid": [0, 1, 2, 3],
            "uid": [0, 1, 2, 0],
            "iid": [0, 0, 1, 2],
            "ts": [0, 1, 2, 3],
            "additional_feature_1": [10, 8, 2, 6],
        }

        # Create the DataFrame
        df = pd.DataFrame(data)
        mock.copy_df.return_value = df
        return mock

    def create_mock_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_unlabeled_data.return_value = self.mock_interaction_matrix
        return mock

    def create_mock_evaluator_streamer_error(self):
        mock = MagicMock()
        mock.get_unlabeled_data.side_effect = Exception("Error in get_unlabeled_data")
        return mock

    def test_get_unlabeled_data_endpoint_valid(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/unlabeled-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_unlabeled_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            self.mock_interaction_matrix.copy_df.assert_called_once()
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 200
            assert response.json() == {
                "shape": [3, 3],
                "unlabeled_data": [
                    {"interactionid": 0, "uid": 0, "iid": 0, "ts": 0},
                    {"interactionid": 1, "uid": 1, "iid": 0, "ts": 1},
                    {"interactionid": 2, "uid": 2, "iid": 1, "ts": 2},
                    {"interactionid": 3, "uid": 0, "iid": 2, "ts": 3},
                ],
            }

    def test_get_unlabeled_data_endpoint_additional_features(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/unlabeled-data?includeAdditionalFeatures=true"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_unlabeled_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            self.mock_interaction_matrix.copy_df.assert_called_once()
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 200
            assert response.json() == {
                "shape": [3, 3],
                "unlabeled_data": [
                    {
                        "interactionid": 0,
                        "uid": 0,
                        "iid": 0,
                        "ts": 0,
                        "additional_feature_1": 10,
                    },
                    {
                        "interactionid": 1,
                        "uid": 1,
                        "iid": 0,
                        "ts": 1,
                        "additional_feature_1": 8,
                    },
                    {
                        "interactionid": 2,
                        "uid": 2,
                        "iid": 1,
                        "ts": 2,
                        "additional_feature_1": 2,
                    },
                    {
                        "interactionid": 3,
                        "uid": 0,
                        "iid": 2,
                        "ts": 3,
                        "additional_feature_1": 6,
                    },
                ],
            }

    def test_get_unlabeled_data_endpoint_invalid_stream_uuid(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            side_effect=InvalidUUIDException("Invalid UUID format"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/invalid-stream-uuid/algorithms/12345678-1234-5678-1234-567812345678/unlabeled-data"
            )

            mock_get_stream_uuid.assert_called_once_with("invalid-stream-uuid")
            mock_get_algo_uuid.assert_not_called()
            mock_get_evaluator_stream_from_db.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_unlabeled_data_endpoint_invalid_algo_uuid(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            side_effect=InvalidUUIDException("Invalid UUID format"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-algo-uuid/unlabeled-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with("invalid-algo-uuid")
            mock_get_evaluator_stream_from_db.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_get_unlabeled_data_endpoint_stream_not_found(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="EvaluatorStreamer not found", status_code=404
            ),
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/unlabeled-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_unlabeled_data.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_unlabeled_data_endpoint_get_stream_error(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/unlabeled-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_unlabeled_data.assert_not_called()
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream from database"
            }

    def test_get_unlabeled_data_endpoint_error(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer_error,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream", return_value=None
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/unlabeled-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer_error.get_unlabeled_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            mock_update_evaluator_stream.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Getting Unlabeled Data: Error in get_unlabeled_data"
            }

    def test_get_unlabeled_data_endpoint_error_updating_stream(self):
        with patch(
            "src.routers.data_handling.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.data_handling.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.data_handling.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_evaluator_stream_from_db, patch(
            "src.routers.data_handling.update_stream",
            side_effect=DatabaseErrorException("error updating db"),
        ) as mock_update_evaluator_stream:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/unlabeled-data"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_evaluator_stream_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_unlabeled_data.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )
            mock_update_evaluator_stream.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 500
            assert response.json() == {"detail": "error updating db"}
