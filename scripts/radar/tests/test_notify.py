import json

import notify


def test_sin_cambios_no_publica(tmp_path, capsys):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"added": [], "moved": [], "removed": [], "updated": [{"name": "x"}]}))
    assert notify.main(["--changes", str(p), "--dry-run"]) == 0
    assert "no se publica" in capsys.readouterr().out


def test_mensaje_con_pr(radar_data):
    e = radar_data["entries"][0]
    msg = notify.build_message(
        {"added": [], "moved": [{**e, "from": "probar"}], "removed": [], "updated": []},
        "https://github.com/agentic-stack-cl/web/pull/1",
    )
    assert "Probar → 🟢 Adoptar" in msg
    assert "<https://github.com/agentic-stack-cl/web/pull/1>" in msg
