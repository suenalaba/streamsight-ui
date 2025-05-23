import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID

from fastapi.testclient import TestClient

from src.main import app
from src.utils.db_utils import DatabaseErrorException, GetEvaluatorStreamErrorException
from src.utils.uuid_utils import InvalidUUIDException

client = TestClient(app)


class TestRegisterAlgorithm(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_streamer = self.create_mock_evaluator_streamer()
        self.mock_error_evaluator_streamer = self.create_mock_error_evaluator_streamer()

    def create_mock_evaluator_streamer(self):
        mock = MagicMock()
        mock.register_algorithm.return_value = UUID(
            "12345678-1234-5678-1234-567812345678"
        )
        return mock

    def create_mock_error_evaluator_streamer(self):
        mock = MagicMock()
        mock.register_algorithm.side_effect = Exception("Error registering algorithm")
        return mock

    def test_register_algorithm_valid(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.register_algorithm.assert_called_once_with(
                algorithm_name="test_algorithm"
            )
            mock_update_evaluator_streamer.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 200
            assert response.json() == {
                "algorithm_uuid": "12345678-1234-5678-1234-567812345678"
            }

    def test_register_algorithm_invalid_uuid(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException(),
        ) as mock_get_uuid_obj, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/invalid-uuid/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_uuid_obj.assert_called_once_with("invalid-uuid")
            mock_get_from_db.assert_not_called()
            self.mock_evaluator_streamer.register_algorithm.assert_not_called()
            mock_update_evaluator_streamer.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid UUID format"}

    def test_register_algorithm_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="Evaluator stream with ID not found", status_code=404
            ),
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.register_algorithm.assert_not_called()
            mock_update_evaluator_streamer.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "Evaluator stream with ID not found"}

    def test_register_algorithm_error_getting_stream_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(),
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.register_algorithm.assert_not_called()
            mock_update_evaluator_streamer.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting evaluator stream from database"
            }

    def test_register_algorithm_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_error_evaluator_streamer.register_algorithm.assert_called_once_with(
                algorithm_name="test_algorithm"
            )
            mock_update_evaluator_streamer.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error registering algorithm: Error registering algorithm"
            }

    def test_register_algorithm_update_stream_error(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_uuid_obj, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_stream",
            side_effect=DatabaseErrorException("error updating db"),
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_uuid_obj.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.register_algorithm.assert_called_once_with(
                algorithm_name="test_algorithm"
            )
            mock_update_evaluator_streamer.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
                self.mock_evaluator_streamer,
            )

            assert response.status_code == 500
            assert response.json() == {"detail": "error updating db"}


class TestGetAlgorithmState(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_streamer = self.create_mock_evaluator_streamer()
        self.mock_error_evaluator_streamer = self.create_mock_error_evaluator_streamer()

    def create_mock_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_algorithm_state.return_value.name = "NEW"
        return mock

    def create_mock_error_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_algorithm_state.side_effect = Exception("Internal error")
        return mock

    def test_get_algorithm_state_valid(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )

            assert response.status_code == 200
            assert response.json() == {"algorithm_state": "NEW"}

    def test_get_algorithm_state_invalid_stream_id(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException("Invalid Stream UUID format"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/invalid-uuid/algorithms/12345678-1234-5678-1234-567812345678/state"
            )

            mock_get_stream_uuid.assert_called_once_with("invalid-uuid")
            mock_get_algo_uuid.assert_not_called()
            mock_get_from_db.assert_not_called()
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid Stream UUID format"}

    def test_get_algorithm_state_invalid_algorithm_id(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            side_effect=InvalidUUIDException("Invalid Algorithm UUID format"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-uuid/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with("invalid-uuid")
            mock_get_from_db.assert_not_called()
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid Algorithm UUID format"}

    def test_get_algorithm_state_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="EvaluatorStreamer not found", status_code=404
            ),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_algorithm_state_error_getting_evaluator_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException("Internal error"),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {"detail": "Internal error"}

    def test_get_algorithm_state_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_error_evaluator_streamer.get_algorithm_state.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting algorithm state: Internal error"
            }


class TestGetAllAlgorithmState(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_streamer = self.create_mock_evaluator_streamer()
        self.mock_error_evaluator_streamer = self.create_mock_error_evaluator_streamer()

    def create_mock_evaluator_streamer(self):
        mock = MagicMock()
        mock_algorithm_new = MagicMock()
        mock_algorithm_new.name = "NEW"
        mock_algorithm_completed = MagicMock()
        mock_algorithm_completed.name = "COMPLETED"
        mock.get_all_algorithm_status.return_value = {
            "algo1_12345678-1234-5678-1234-567812345678": mock_algorithm_new,
            "algo2_87654321-4321-8765-4321-876543218765": mock_algorithm_completed,
        }
        return mock

    def create_mock_error_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_all_algorithm_status.side_effect = Exception("Internal error")
        return mock

    def test_get_all_algorithm_state_valid(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_all_algorithm_status.assert_called_once()

            assert response.status_code == 200
            assert response.json() == {
                "algorithm_states": [
                    {
                        "algorithm_uuid": "12345678-1234-5678-1234-567812345678",
                        "algorithm_name": "algo1",
                        "state": "NEW",
                    },
                    {
                        "algorithm_uuid": "87654321-4321-8765-4321-876543218765",
                        "algorithm_name": "algo2",
                        "state": "COMPLETED",
                    },
                ]
            }

    def test_get_all_algorithm_state_invalid_stream_id(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException("Invalid Stream UUID format"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get("/streams/invalid-uuid/algorithms/state")

            mock_get_stream_uuid.assert_called_once_with("invalid-uuid")
            mock_get_from_db.assert_not_called()
            self.mock_evaluator_streamer.get_all_algorithm_status.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid Stream UUID format"}

    def test_get_all_algorithm_state_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="EvaluatorStreamer not found", status_code=404
            ),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_all_algorithm_status.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_all_algorithm_state_error_fetching_evaluator_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException("Internal error"),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_all_algorithm_status.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {"detail": "Internal error"}

    def test_get_all_algorithm_state_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_error_evaluator_streamer.get_all_algorithm_status.assert_called_once()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error getting all algorithm states: Internal error"
            }


class TestIsAlgoStreamingCompleted(unittest.TestCase):
    def setUp(self):
        self.mock_evaluator_streamer = self.create_mock_evaluator_streamer()
        self.mock_completed_evaluator_streamer = (
            self.create_mock_completed_evaluator_streamer()
        )
        self.mock_error_evaluator_streamer = self.create_mock_error_evaluator_streamer()

    def create_mock_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_algorithm_state.return_value.name = "NEW"
        return mock

    def create_mock_completed_evaluator_streamer(self):
        mock = MagicMock()
        mock.register_algorithm.return_value = UUID(
            "12345678-1234-5678-1234-567812345678"
        )
        mock.get_algorithm_state.return_value.name = "COMPLETED"
        return mock

    def create_mock_error_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_algorithm_state.side_effect = Exception("Internal error")
        return mock

    def test_is_algo_streaming_completed_completed(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_completed_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_completed_evaluator_streamer.get_algorithm_state.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )

            assert response.status_code == 200
            assert response.json()

    def test_is_algo_streaming_completed_new(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )

            assert response.status_code == 200
            assert not response.json()

    def test_is_algo_streaming_completed_invalid_stream_id(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            side_effect=InvalidUUIDException("Invalid Stream UUID format"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/invalid-uuid/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_stream_uuid.assert_called_once_with("invalid-uuid")
            mock_get_algo_uuid.assert_not_called()
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()
            mock_get_from_db.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid Stream UUID format"}

    def test_is_algo_streaming_completed_invalid_algorithm_id(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            side_effect=InvalidUUIDException("Invalid Algorithm UUID format"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-uuid/is-completed"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with("invalid-uuid")
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()
            mock_get_from_db.assert_not_called()

            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid Algorithm UUID format"}

    def test_is_algo_streaming_completed_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException(
                message="EvaluatorStreamer not found", status_code=404
            ),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_is_algo_streaming_completed_error_getting_evaluator_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            side_effect=GetEvaluatorStreamErrorException("Internal error"),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {"detail": "Internal error"}

    def test_is_algo_streaming_completed_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_stream_uuid_object",
            return_value=UUID("336e4cb7-861b-4870-8c29-3ffc530711ef"),
        ) as mock_get_stream_uuid, patch(
            "src.routers.algorithm_management.get_algo_uuid_object",
            return_value=UUID("12345678-1234-5678-1234-567812345678"),
        ) as mock_get_algo_uuid, patch(
            "src.routers.algorithm_management.get_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_stream_uuid.assert_called_once_with(
                "336e4cb7-861b-4870-8c29-3ffc530711ef"
            )
            mock_get_algo_uuid.assert_called_once_with(
                "12345678-1234-5678-1234-567812345678"
            )
            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_error_evaluator_streamer.get_algorithm_state.assert_called_once_with(
                UUID("12345678-1234-5678-1234-567812345678")
            )

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error checking if algorithm streaming is completed: Internal error"
            }
