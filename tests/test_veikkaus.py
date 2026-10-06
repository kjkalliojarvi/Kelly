from Kelly.veikkaus import validate_params

def test_validate_params_all_strings():
    koodi, lahto, peli = validate_params("F", "1", "VOI")
    assert koodi == "F"
    assert lahto == "1"
    assert peli == "voi"

def test_validate_params_ints():
    koodi, lahto, peli = validate_params(1, 2, "T65")
    assert koodi == "1"
    assert lahto == "2"
    assert peli == "t65"

def test_validate_params_mixed():
    koodi, lahto, peli = validate_params(5, "3", "Sij")
    assert koodi == "5"
    assert lahto == "3"
    assert peli == "sij"

def test_validate_params_already_lowercase():
    koodi, lahto, peli = validate_params("1", "1", "kak")
    assert koodi == "1"
    assert lahto == "1"
    assert peli == "kak"
