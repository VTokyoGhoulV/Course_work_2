import runpy
from pathlib import Path


def test_main_pipeline_filters_sorts_limits_and_saves(monkeypatch) -> None:
    project_root = Path(__file__).resolve().parents[1]
    saved_callsigns = []

    class FakeAeroplanesAPI:
        def get_aeroplanes(self, country: str) -> dict:
            assert country == "Belarus"
            return {
                "states": [
                    ["abc001", "LOW", "Belarus", 1, 2, 27.56, 53.90, 1_000, False, 200, 90],
                    ["abc002", "HIGH", "Belarus", 1, 2, 27.56, 53.90, 9_000, False, 300, 90],
                    ["abc003", "OTHER", "Germany", 1, 2, 13.40, 52.52, 8_000, False, 400, 90],
                    ["abc004", "OUT", "Belarus", 1, 2, 27.56, 53.90, 20_000, False, 500, 90],
                ]
            }

    class FakeJsonSaver:
        @staticmethod
        def add_aeroplane(plane) -> None:
            saved_callsigns.append(plane.callsign)

    monkeypatch.setattr("src.utils.user_interaction", lambda: ("Belarus", 2, ["Belarus"], "1000-10000"))
    monkeypatch.setattr("src.classes.AeroplanesAPI", FakeAeroplanesAPI)
    monkeypatch.setattr("src.classes.JsonSaver", FakeJsonSaver)
    monkeypatch.syspath_prepend(str(project_root))

    runpy.run_path(str(project_root / "main.py"), run_name="__main__")

    assert saved_callsigns == ["HIGH", "LOW"]
