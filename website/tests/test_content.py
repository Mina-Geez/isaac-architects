import pytest

from engine.content import load_project, load_projects, ContentError


def _write_project(d, **over):
    d.mkdir(parents=True, exist_ok=True)
    (d / "hero.jpg").write_bytes(b"x")
    (d / "01.jpg").write_bytes(b"x")
    fm = dict(name="Villa X", location="Cairo", category="Residential",
              type="Villa", status="Built", lead="A lead.", hero="hero.jpg", order=1)
    fm.update(over)

    def toml_val(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return f'"{v}"'
        return repr(v)

    lines = "\n".join(f'{k}={toml_val(v)}' for k, v in fm.items())
    (d / "index.md").write_text(
        f'+++\n{lines}\n[[gallery]]\nsrc="01.jpg"\nalt="A shot"\n+++\nBody para.',
        encoding="utf-8")


def test_loads_valid_project(tmp_path):
    d = tmp_path / "villa-x"
    _write_project(d)
    p = load_project(d)
    assert p.slug == "villa-x"
    assert p.name == "Villa X"
    assert p.gallery[0].src == "01.jpg"
    assert "<p>Body para.</p>" in p.body_html


def test_missing_required_field_raises(tmp_path):
    d = tmp_path / "bad"
    d.mkdir()
    (d / "index.md").write_text('+++\nname="No Lead"\n+++\nx', encoding="utf-8")
    with pytest.raises(ContentError):
        load_project(d)


def test_missing_gallery_image_raises(tmp_path):
    d = tmp_path / "g"
    d.mkdir()
    (d / "hero.jpg").write_bytes(b"x")
    (d / "index.md").write_text(
        '+++\nname="G"\nlocation="x"\ncategory="x"\ntype="x"\nstatus="x"\nlead="x"\n'
        'hero="hero.jpg"\norder=1\n[[gallery]]\nsrc="missing.jpg"\nalt="x"\n+++\nb',
        encoding="utf-8")
    with pytest.raises(ContentError):
        load_project(d)


def test_draft_excluded_and_sorted(tmp_path):
    _write_project(tmp_path / "b", order=2)
    _write_project(tmp_path / "a", order=1)
    _write_project(tmp_path / "d", order=3, draft=True)
    items = load_projects(tmp_path)
    assert [p.slug for p in items] == ["a", "b"]
