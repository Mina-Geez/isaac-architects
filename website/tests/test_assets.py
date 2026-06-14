from engine.assets import hashed_name, minify_css


def test_hashed_name_stable():
    assert hashed_name("site.css", b"a{b:1}") == hashed_name("site.css", b"a{b:1}")
    assert hashed_name("site.css", b"x") != hashed_name("site.css", b"y")


def test_minify_css_strips_comments_ws():
    out = minify_css("a {  color : red ; } /* c */")
    assert "/*" not in out and out.count(" ") < 4
