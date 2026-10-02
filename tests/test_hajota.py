import pytest

from Kelly.hajota import get_category, split_abcd


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

    def test_split_abcd(self):
        rajat = {
            'A_to_B': 30,
            'B_to_C': 20,
            'C_to_D': 10,
            'D_to_X': 5
        }

        prosentit = [
            35, # A
            30, # B (num > 30 is False, num > 20 is True)
            25, # B
            20, # C (num > 20 is False, num > 10 is True)
            15, # C
            10, # D (num > 10 is False, num > 5 is True)
            8,  # D
            5,  # X (num > 5 is False)
            2   # X
        ]

        expected = {
            'A': [1],
            'B': [2, 3],
            'C': [4, 5],
            'D': [6, 7],
            'X': [8, 9]
        }

        result = split_abcd(prosentit, rajat)
        assert result == expected
