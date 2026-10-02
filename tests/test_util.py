from types import SimpleNamespace

from Kelly.util import footer, RULE


class ZeroDivisionFormatFloat:
    """A dummy class that triggers ZeroDivisionError when formatted as float."""
    def __format__(self, format_spec):
        raise ZeroDivisionError("division by zero")


def test_footer_normal(capsys):
    """Test that footer prints correctly under normal circumstances."""
    metadata = SimpleNamespace(vaihto=1000.0, jako=650.0)

    footer(
        omatn=0.5,
        total=10.0,
        metadata=metadata,
        minlunde=15.0,
        avelunde=20.0,
        maxlunde=25.0
    )

    captured = capsys.readouterr()
    expected_tomatn = 10.0 / 0.5  # 20.0

    # We check if lines are correctly printed
    assert RULE in captured.out
    assert "Oma todennäköisyys    : 50.0 %  (kerroin 20.00)" in captured.out
    assert "Vaihto / Jako         : 1000.0 / 650.0" in captured.out
    assert "Lunastus min/ka/max   : 15.0 / 20.0 / 25.0" in captured.out


def test_footer_type_error(capsys):
    """Test that footer handles TypeError when formatting fails (e.g., None)."""
    metadata = SimpleNamespace(vaihto=1000.0, jako=650.0)

    footer(
        omatn=0.5,
        total=10.0,
        metadata=metadata,
        minlunde=None,  # This will cause TypeError in f-string formatting
        avelunde=20.0,
        maxlunde=25.0
    )

    captured = capsys.readouterr()

    # Print function for lunastus should be skipped
    assert "Vaihto / Jako" in captured.out
    assert "Lunastus min/ka/max" not in captured.out


def test_footer_zero_division_error(capsys):
    """Test that footer handles ZeroDivisionError during formatting."""
    metadata = SimpleNamespace(vaihto=1000.0, jako=650.0)

    footer(
        omatn=0.5,
        total=10.0,
        metadata=metadata,
        minlunde=ZeroDivisionFormatFloat(),  # Triggers ZeroDivisionError
        avelunde=20.0,
        maxlunde=25.0
    )

    captured = capsys.readouterr()

    # Print function for lunastus should be skipped, no error raised
    assert "Vaihto / Jako" in captured.out
    assert "Lunastus min/ka/max" not in captured.out
