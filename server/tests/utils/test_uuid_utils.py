import unittest
from uuid import UUID

from src.utils.uuid_utils import (
    InvalidUUIDException,
    get_algo_uuid_object,
    get_stream_uuid_object,
)


class TestUUIDUtils(unittest.TestCase):
    def test_get_algo_uuid_object_valid(self):
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        result = get_algo_uuid_object(valid_uuid)
        self.assertIsInstance(result, UUID)
        self.assertEqual(str(result), valid_uuid)

    def test_get_algo_uuid_object_invalid(self):
        invalid_uuid = "invalid-uuid"
        with self.assertRaises(InvalidUUIDException) as context:
            get_algo_uuid_object(invalid_uuid)
        self.assertEqual(context.exception.message, "Invalid Algorithm UUID format")
        self.assertEqual(context.exception.status_code, 400)

    def test_get_stream_uuid_object_valid(self):
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        result = get_stream_uuid_object(valid_uuid)
        self.assertIsInstance(result, UUID)
        self.assertEqual(str(result), valid_uuid)

    def test_get_stream_uuid_object_invalid(self):
        invalid_uuid = "invalid-uuid"
        with self.assertRaises(InvalidUUIDException) as context:
            get_stream_uuid_object(invalid_uuid)
        self.assertEqual(context.exception.message, "Invalid Stream UUID format")
        self.assertEqual(context.exception.status_code, 400)
