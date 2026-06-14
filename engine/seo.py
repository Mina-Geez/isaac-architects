import json
from xml.sax.saxutils import escape as xesc


def sitemap_xml(base: str, paths, lastmod: str) -> str:
    urls = []
    for p in paths:
        loc = f"{base}/{p}" if p else f"{base}/"
        urls.append(f"  <url><loc>{xesc(loc)}</loc><lastmod>{lastmod}</lastmod></url>")
    body = "\n".join(urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n</urlset>\n")


def robots_txt(base: str) -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"


def localbusiness_jsonld(base, name, phone, location) -> str:
    data = {"@context": "https://schema.org", "@type": "ProfessionalService",
            "name": name, "url": base + "/", "telephone": phone,
            "image": f"{base}/images/og-image.jpg",
            "address": {"@type": "PostalAddress", "addressLocality": "Alexandria",
                        "addressCountry": "EG"},
            "areaServed": "EG", "description": location}
    return json.dumps(data, ensure_ascii=False)


def creativework_jsonld(base, project) -> str:
    data = {"@context": "https://schema.org", "@type": "CreativeWork",
            "name": project.name, "image": f"{base}/images/{project.slug}.jpg",
            "description": project.lead, "locationCreated": project.location,
            "url": f"{base}/projects/{project.slug}.html"}
    return json.dumps(data, ensure_ascii=False)
