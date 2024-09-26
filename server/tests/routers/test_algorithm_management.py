import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID

from fastapi.testclient import TestClient

from src.main import app

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
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_evaluator_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
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
        response = client.post(
            "/streams/invalid-uuid/algorithms",
            json={"algorithm_name": "test_algorithm"},
        )

        self.mock_evaluator_streamer.register_algorithm.assert_not_called()

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid UUID format"}

    def test_register_algorithm_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=None,
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_evaluator_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.register_algorithm.assert_not_called()
            mock_update_evaluator_streamer.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_register_algorithm_error_getting_stream_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            side_effect=Exception("Error fetching from DB"),
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_evaluator_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.register_algorithm.assert_not_called()
            mock_update_evaluator_streamer.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {
                "detail": "Error Getting Stream: Error fetching from DB"
            }

    def test_register_algorithm_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db, patch(
            "src.routers.algorithm_management.update_evaluator_stream",
            return_value=None,
        ) as mock_update_evaluator_streamer:
            response = client.post(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms",
                json={"algorithm_name": "test_algorithm"},
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
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
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
        response = client.get(
            "/streams/invalid-uuid/algorithms/12345678-1234-5678-1234-567812345678/state"
        )

        self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid Stream UUID format"}

    def test_get_algorithm_state_invalid_algorithm_id(self):
        response = client.get(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-uuid/state"
        )

        self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid Algorithm UUID format"}

    def test_get_algorithm_state_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=None,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_algorithm_state_error_getting_evaluator_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            side_effect=Exception("Internal error"),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {"detail": "Error Getting Stream: Internal error"}

    def test_get_algorithm_state_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/state"
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
            UUID("12345678-1234-5678-1234-567812345678"): mock_algorithm_new,
            UUID("87654321-4321-8765-4321-876543218765"): mock_algorithm_completed,
        }
        return mock

    def create_mock_error_evaluator_streamer(self):
        mock = MagicMock()
        mock.get_all_algorithm_status.side_effect = Exception("Internal error")
        return mock

    def test_get_all_algorithm_state_valid(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_all_algorithm_status.assert_called_once()

            assert response.status_code == 200
            assert response.json() == {
                "algorithm_states": {
                    "12345678-1234-5678-1234-567812345678": "NEW",
                    "87654321-4321-8765-4321-876543218765": "COMPLETED",
                }
            }

    def test_get_all_algorithm_state_invalid_stream_id(self):
        response = client.get("/streams/invalid-uuid/algorithms/state")

        self.mock_evaluator_streamer.get_all_algorithm_status.assert_not_called()

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid Stream UUID format"}

    def test_get_all_algorithm_state_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=None,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_all_algorithm_status.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_get_all_algorithm_state_error_fetching_evaluator_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            side_effect=Exception("Internal error"),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_all_algorithm_status.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {"detail": "Error Getting Stream: Internal error"}

    def test_get_all_algorithm_state_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/state"
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
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_completed_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
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
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
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
        response = client.get(
            "/streams/invalid-uuid/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
        )

        self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid Stream UUID format"}

    def test_is_algo_streaming_completed_invalid_algorithm_id(self):
        response = client.get(
            "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/invalid-uuid/is-completed"
        )

        self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid Algorithm UUID format"}

    def test_is_algo_streaming_completed_evaluator_not_found(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=None,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 404
            assert response.json() == {"detail": "EvaluatorStreamer not found"}

    def test_is_algo_streaming_completed_error_getting_evaluator_from_db(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            side_effect=Exception("Internal error"),
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
            )

            mock_get_from_db.assert_called_once_with(
                UUID("336e4cb7-861b-4870-8c29-3ffc530711ef")
            )
            self.mock_evaluator_streamer.get_algorithm_state.assert_not_called()

            assert response.status_code == 500
            assert response.json() == {"detail": "Error Getting Stream: Internal error"}

    def test_is_algo_streaming_completed_internal_error(self):
        with patch(
            "src.routers.algorithm_management.get_evaluator_stream_from_db",
            return_value=self.mock_error_evaluator_streamer,
        ) as mock_get_from_db:
            response = client.get(
                "/streams/336e4cb7-861b-4870-8c29-3ffc530711ef/algorithms/12345678-1234-5678-1234-567812345678/is-completed"
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
