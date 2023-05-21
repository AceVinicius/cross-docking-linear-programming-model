import io
import unittest
import instance

from typing import TextIO


class TestSkipFirstLine(unittest.TestCase):
    def test_skips_first_line(self):
        with io.StringIO("first line\nsecond line\nthird line\n") as f:
            instance.skip_first_line(f)
            self.assertEqual(f.readline(), "second line\n")

    def test_raises_value_error_when_title_is_missing(self):
        with io.StringIO("") as f:
            with self.assertRaises(ValueError):
                instance.skip_first_line(f)
