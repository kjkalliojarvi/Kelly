import pytest

from Kelly.hajota import get_category


class TestHajota:
    def test_get_category_found(self):
        abcd = {'A': [1, 2], 'B': [3, 4], 'C': [5], 'D': [6]}
        assert get_category(abcd, 1) == 'A'
        assert get_category(abcd, 2) == 'A'
        assert get_category(abcd, 3) == 'B'
        assert get_category(abcd, 4) == 'B'
        assert get_category(abcd, 5) == 'C'
        assert get_category(abcd, 6) == 'D'

    def test_get_category_not_found(self):
        abcd = {'A': [1, 2], 'B': [3, 4]}
        assert get_category(abcd, 5) is None
