from types import SimpleNamespace

import pytest

from Kelly import get_data, bet_calc, veikkaus, validoi


class TestTPeliPros:
    """Regression test for the ``peli ... --prosentit`` T-pool path.

    Exercises ``bet_calc.t_peli_pros`` end-to-end on synthetic data,
    isolated from the filesystem. Guards against three past defects:
      * ``yhdistelma_tn`` called with too few arguments (TypeError),
      * ``bet_size`` fed a string instead of the combination tuple,
      * ``split_abcd`` fed a dict (keys) instead of a probability list.
    """

    CONF = {
        'lahtoja': 2, 'panos': 1, 'moninkertaistus': False,
        'min_kelly': 0.0, 'min_lunastus': 1.0,
        'rajat': {'A_to_B': 35, 'B_to_C': 15,  # prosenttiyksiköitä
                  'C_to_D': 5, 'D_to_X': 0},
        'hajotus': ['AB'],
    }

    def test_t_peli_pros(self, monkeypatch):
        captured = []

        def fake_write(bets, peli, args, metadata, huomio=''):
            captured.append(bets)

        monkeypatch.setattr(bet_calc, 'get_json', lambda _f: dict(self.CONF))
        monkeypatch.setattr(bet_calc, 'write_to_file', fake_write)

        args = SimpleNamespace(lahto='1', pelimuoto='t4')
        prosentit = {'1': [50, 30, 20], '2': [40, 35, 25]}      # omat, %
        peliprosentit = {'1': [60, 25, 15], '2': [45, 10, 45]}  # pooli, %
        meta = SimpleNamespace(vaihto=10000.0, jako=6500.0)

        bet_calc.t_peli_pros(args, prosentit, meta, peliprosentit)

        bets = captured[0]
        # Rivit ['AB']: (1,2),(1,3),(2,1),(3,1); vain (1,2) on arvopeli.
        assert len(bets) == 1
        bet = bets[0]
        assert bet.yhdistelma == '1/2'  # tuple, ei merkkijono
        # kerroin = (jako/vaihto) / (pooli_p1 * pooli_p2)
        assert bet.kerroin == pytest.approx(0.65 / (0.60 * 0.10))
        # oma_kerroin = 1 / (oma_p1 * oma_p2)
        assert bet.oma_kerroin == pytest.approx(1 / (0.50 * 0.35))


class TestMethods:
    def test_get_prosentit(self):
        prosentit = [6, 4, 1, 40, 16, 8, 1, 12, 4, 6, 2]
        p1 = get_data.p_1(prosentit)
        assert p1 == {1: 0.06, 2: 0.04, 3: 0.01, 4: 0.4, 5: 0.16, 6: 0.08,
                      7: 0.01, 8: 0.12, 9: 0.04, 10: 0.06, 11: 0.02}
        p2 = get_data.p_2(prosentit)
        assert p2 == pytest.approx({1: 0.09239653512993262, 2: 0.07699711260827719,
                      3: 0.019249278152069296, 4: 0.178055822906641,
                      5: 0.15784408084696822, 6: 0.10779595765158806,
                      7: 0.019249278152069296, 8: 0.13859480269489893,
                      9: 0.07699711260827719, 10: 0.09239653512993262,
                      11: 0.04042348411934552})
        p3 = get_data.p_3(prosentit)
        assert p3 == pytest.approx({1: 0.10676835081029551, 2: 0.09056244041944708,
                      3: 0.038131553860819824, 4: 0.10295519542421354,
                      5: 0.12583412774070543, 6: 0.11439466158245948,
                      7: 0.038131553860819824, 8: 0.12392755004766444,
                      9: 0.09056244041944708, 10: 0.10676835081029551,
                      11: 0.06196377502383222})
