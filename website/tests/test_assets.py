from engine.assets import hashed_name


def test_hashed_name_stable():
    assert hashed_name("site.css", b"a{b:1}") == hashed_name("site.css", b"a{b:1}")
    assert hashed_name("site.css", b"x") != hashed_name("site.css", b"y")
