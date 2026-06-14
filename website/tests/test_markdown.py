from engine.markdown import render_paragraphs


def test_wraps_paragraphs():
    html = render_paragraphs("One.\n\nTwo.")
    assert html == "<p>One.</p>\n<p>Two.</p>"


def test_emphasis_and_escaping():
    html = render_paragraphs("a *b* & c")
    assert html == "<p>a <em>b</em> &amp; c</p>"
