from engine.seo import sitemap_xml, robots_txt, localbusiness_jsonld


def test_sitemap_lists_pages():
    xml = sitemap_xml("https://x.com", ["", "projects/villa-x.html"], lastmod="2026-06-14")
    assert "<loc>https://x.com/</loc>" in xml
    assert "<loc>https://x.com/projects/villa-x.html</loc>" in xml


def test_robots_points_to_sitemap():
    assert "Sitemap: https://x.com/sitemap.xml" in robots_txt("https://x.com")


def test_localbusiness_has_name_and_phone():
    j = localbusiness_jsonld("https://x.com", "Isaac Architects", "+201274348575", "Alexandria, Egypt")
    assert "ProfessionalService" in j
    assert "+201274348575" in j
