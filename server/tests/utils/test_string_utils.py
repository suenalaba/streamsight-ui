import unittest

from src.utils.string_utils import split_string_by_last_underscore


class TestStringUtils(unittest.TestCase):
    def test_split_string_by_last_underscore(self):
        s = "algorithm_name_algorithm_id"
        result = split_string_by_last_underscore(s)
        self.assertEqual(result, ("algorithm_name_algorithm", "id"))
