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
        prosentit = [50, 40, 30, 20, 10, 5, 2]
        rajat = {
            'A_to_B': 45,
            'B_to_C': 25,
            'C_to_D': 15,
            'D_to_X': 5
        }
        # percentages:
        # 1: 50 -> A (50 > 45)
        # 2: 40 -> B (40 <= 45 and 40 > 25)
        # 3: 30 -> B (30 <= 45 and 30 > 25)
        # 4: 20 -> C (20 <= 25 and 20 > 15)
        # 5: 10 -> D (10 <= 15 and 10 > 5)
        # 6: 5  -> X (5 <= 5) (edge case)
        # 7: 2  -> X (2 <= 5)

        expected = {
            'A': [1],
            'B': [2, 3],
            'C': [4],
            'D': [5],
            'X': [6, 7]
        }
        assert split_abcd(prosentit, rajat) == expected
