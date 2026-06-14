from engine.settings import load_settings


def test_loads_settings(tmp_path):
    (tmp_path / "settings.toml").write_text(
        'canonical_base="https://x.com/"\nstudio_name="Isaac"\n'
        '[contact]\nphone_e164="+201274348575"\n', encoding="utf-8")
    s = load_settings(tmp_path / "settings.toml")
    assert s["canonical_base"] == "https://x.com"
    assert s["contact"]["phone_e164"] == "+201274348575"
