# NOTE: Google Fonts origins are allowed until fonts are self-hosted (perf/security
# follow-up). Once self-hosted, drop the two https://fonts.* and tighten to 'self'.
CSP = ("default-src 'self'; img-src 'self' data:; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "script-src 'self'; font-src 'self' https://fonts.gstatic.com; "
       "connect-src 'self' https://formspree.io; form-action 'self' https://formspree.io; "
       "frame-ancestors 'none'; base-uri 'self'; upgrade-insecure-requests")


def headers_file() -> str:
    return (
        "/*\n"
        f"  Content-Security-Policy: {CSP}\n"
        "  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload\n"
        "  X-Content-Type-Options: nosniff\n"
        "  X-Frame-Options: DENY\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: geolocation=(), microphone=(), camera=(), browsing-topics=()\n"
        "\n"
        "/static/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "\n"
        "/images/*\n  Cache-Control: public, max-age=31536000, immutable\n")


def security_txt(email: str) -> str:
    return f"Contact: mailto:{email}\nPreferred-Languages: en\n"
