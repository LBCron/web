import json

import radar
import sync


def test_count_votes_ignora_otros_emojis():
    msg = {
        "reactions": [{"count": 4, "emoji": {"name": "🟢"}}, {"count": 9, "emoji": {"name": "🔥"}}]
    }
    assert sync.count_votes(msg) == {"adoptar": 4, "probar": 0, "evaluar": 0, "esperar": 0}


def test_winning_ring_quorum_y_empate():
    assert sync.winning_ring({"adoptar": 2, "probar": 1, "evaluar": 0, "esperar": 0}, 5) is None
    assert (
        sync.winning_ring({"adoptar": 4, "probar": 1, "evaluar": 0, "esperar": 0}, 5) == "adoptar"
    )
    # empate → el más conservador (externo)
    assert (
        sync.winning_ring({"adoptar": 0, "probar": 3, "evaluar": 3, "esperar": 0}, 5) == "evaluar"
    )


def run_fixture(radar_data, fixture_path):
    threads = sync.read_forum(sync.FixtureSource(fixture_path))
    return sync.apply(radar_data, threads, quorum=5, today="2026-11-10")


def test_apply_contra_fixture(radar_data, fixture_path):
    result = run_fixture(radar_data, fixture_path)
    by_id = {e["id"]: e for e in result.data["entries"]}

    # MCP: adoptado por nombre, mismo anillo → solo se vincula al hilo
    mcp = by_id["model-context-protocol"]
    assert (mcp["ring"], mcp["status"], mcp["threadId"]) == (
        "adoptar",
        "votado",
        "1500000000000000001",
    )
    assert (
        mcp["discussion"] == "https://discord.com/channels/1200000000000000001/1500000000000000001"
    )

    # A2A: evaluar → probar, sube
    a2a = by_id["agent2agent"]
    assert (a2a["ring"], a2a["moved"], a2a["date"]) == ("probar", 1, "2026-11-10")

    # LangGraph (hilo archivado): empate 3-3 → evaluar, baja
    lg = by_id["langgraph"]
    assert (lg["ring"], lg["moved"]) == ("evaluar", -1)

    # Hilo nuevo con quórum → blip nuevo
    vibe = by_id["vibe-coding-sin-revision"]
    assert (vibe["quadrant"], vibe["ring"], vibe["moved"], vibe["status"]) == (
        "tecnicas",
        "esperar",
        2,
        "votado",
    )
    assert vibe["description"] == "Aceptar código generado sin leerlo ni testearlo."

    # DSPy bajo quórum, hilo sin cuadrante y canal ajeno → fuera
    assert "dspy" not in by_id
    assert len(result.skipped) == 2
    assert "hilo-de-otro-canal" not in by_id

    assert result.data["updated"] == "2026-11-10"
    assert radar.validate(result.data) == []


def test_changes_resumen(radar_data, fixture_path):
    c = run_fixture(radar_data, fixture_path).changes
    assert [e["id"] for e in c["added"]] == ["vibe-coding-sin-revision"]
    assert sorted(e["id"] for e in c["moved"]) == ["agent2agent", "langgraph"]
    assert [e["id"] for e in c["updated"]] == ["model-context-protocol"]
    assert c["removed"] == []


def test_idempotente(radar_data, fixture_path):
    first = run_fixture(radar_data, fixture_path).data
    threads = sync.read_forum(sync.FixtureSource(fixture_path))
    second = sync.apply(first, threads, quorum=5, today="2026-11-11")
    assert not any(second.changes.values())
    assert second.data == first


def test_moved_se_apaga_con_el_tiempo(radar_data, fixture_path):
    first = run_fixture(radar_data, fixture_path).data
    later = sync.apply(first, [], quorum=5, today="2027-06-01").data
    assert all(e["moved"] == 0 for e in later["entries"])


def test_main_dry_run_no_escribe(tmp_path, radar_data, fixture_path):
    path = tmp_path / "radar.json"
    path.write_text(json.dumps(radar_data), encoding="utf-8")
    changes = tmp_path / "c.json"
    body = tmp_path / "pr.md"
    rc = sync.main(
        [
            "--radar",
            str(path),
            "--fixture",
            str(fixture_path),
            "--today",
            "2026-11-10",
            "--dry-run",
            "--changes-out",
            str(changes),
            "--pr-body-out",
            str(body),
        ]
    )
    assert rc == 0
    assert json.loads(path.read_text()) == radar_data
    assert "Agent2Agent" in body.read_text()
    assert json.loads(changes.read_text())["added"][0]["name"] == "Vibe coding sin revisión"


def test_main_sin_credenciales(monkeypatch):
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("FORUM_CHANNEL_ID", raising=False)
    assert sync.main(["--dry-run"]) == 2
