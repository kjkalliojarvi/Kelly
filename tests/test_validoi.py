import pytest

from Kelly.validoi import yhdistelma_ok

class TestYhdistelmaOk:
    def test_all_matches(self):
        systeemi = {
            'lahtoja': 3,
            'L1': [1, 2],
            'L2': [3],
            'L3': [4, 5],
            'omia': 2
        }
        yhdistelma = (1, 3, 5) # Matches L1, L2, L3 (3 matches)
        assert yhdistelma_ok(yhdistelma, systeemi) is True

    def test_exact_required_matches(self):
        systeemi = {
            'lahtoja': 3,
            'L1': [1, 2],
            'L2': [3],
            'L3': [4, 5],
            'omia': 2
        }
        yhdistelma = (1, 3, 6) # Matches L1, L2, not L3 (2 matches)
        assert yhdistelma_ok(yhdistelma, systeemi) is True

    def test_too_few_matches(self):
        systeemi = {
            'lahtoja': 3,
            'L1': [1, 2],
            'L2': [3],
            'L3': [4, 5],
            'omia': 2
        }
        yhdistelma = (1, 7, 6) # Matches L1, not L2, not L3 (1 match)
        assert yhdistelma_ok(yhdistelma, systeemi) is False

    def test_zero_matches(self):
        systeemi = {
            'lahtoja': 3,
            'L1': [1, 2],
            'L2': [3],
            'L3': [4, 5],
            'omia': 2
        }
        yhdistelma = (8, 7, 6) # Matches none (0 matches)
        assert yhdistelma_ok(yhdistelma, systeemi) is False
