import pytest
from engine.frontmatter import parse


def test_parses_toml_and_body():
    raw = '+++\nname = "Villa Tadros"\norder = 5\n+++\nFirst para.\n\nSecond para.'
    meta, body = parse(raw)
    assert meta["name"] == "Villa Tadros"
    assert meta["order"] == 5
    assert body.strip() == "First para.\n\nSecond para."


def test_missing_fences_raises():
    with pytest.raises(ValueError):
        parse("no fences here")
