from engine.security import headers_file, security_txt


def test_headers_contains_csp_and_hsts():
    h = headers_file()
    assert "Content-Security-Policy:" in h
    assert "script-src 'self'" in h
    assert "Strict-Transport-Security:" in h
    assert "X-Content-Type-Options: nosniff" in h
    assert "Cache-Control: public, max-age=31536000, immutable" in h


def test_security_txt_has_contact():
    assert "Contact:" in security_txt("ideadesigns.arch@gmail.com")
