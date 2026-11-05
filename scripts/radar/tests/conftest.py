import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "forum.json"


@pytest.fixture
def radar_data():
    return json.loads((ROOT / "src" / "data" / "radar.json").read_text(encoding="utf-8"))


@pytest.fixture
def fixture_path():
    return FIXTURE
