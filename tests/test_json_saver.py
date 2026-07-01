import json

import pytest

from src.classes import BaseJsonSaver, JsonSaver


def _prepare_data_file(tmp_path, text: str = "[]"):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_file = data_dir / "data.json"
    data_file.write_text(text, encoding="utf-8")
    return data_file


def test_base_json_saver_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseJsonSaver()


def test_json_saver_is_not_instantiable_while_save_and_delete_are_abstract() -> None:
    with pytest.raises(TypeError):
        JsonSaver()


def test_add_aeroplane_writes_plane_to_json(tmp_path, monkeypatch, sample_plane) -> None:
    data_file = _prepare_data_file(tmp_path)
    monkeypatch.setattr("src.classes.find_project_root", lambda: tmp_path)

    JsonSaver.add_aeroplane(sample_plane)

    saved_data = json.loads(data_file.read_text(encoding="utf-8"))
    assert saved_data == [sample_plane.__dict__]


def test_add_aeroplane_handles_empty_json_file(tmp_path, monkeypatch, sample_plane) -> None:
    data_file = _prepare_data_file(tmp_path, text="")
    monkeypatch.setattr("src.classes.find_project_root", lambda: tmp_path)

    JsonSaver.add_aeroplane(sample_plane)

    saved_data = json.loads(data_file.read_text(encoding="utf-8"))
    assert saved_data == [sample_plane.__dict__]


def test_load_returns_json_data(tmp_path, monkeypatch, sample_plane) -> None:
    _prepare_data_file(tmp_path, text=json.dumps([sample_plane.__dict__]))
    monkeypatch.setattr("src.classes.find_project_root", lambda: tmp_path)

    result = JsonSaver.load()

    assert result == [sample_plane.__dict__]


def test_delete_aeroplane_removes_plane_from_json(tmp_path, monkeypatch, sample_plane, aeroplane_factory) -> None:
    other_plane = aeroplane_factory(icao24="ABC999", callsign="OTHER")
    data_file = _prepare_data_file(tmp_path, text=json.dumps([sample_plane.__dict__, other_plane.__dict__]))
    monkeypatch.setattr("src.classes.find_project_root", lambda: tmp_path)

    JsonSaver.delete_aeroplane(sample_plane)

    saved_data = json.loads(data_file.read_text(encoding="utf-8"))
    assert saved_data == [other_plane.__dict__]


def test_delete_aeroplane_does_nothing_when_file_is_empty(tmp_path, monkeypatch, sample_plane) -> None:
    data_file = _prepare_data_file(tmp_path, text="")
    monkeypatch.setattr("src.classes.find_project_root", lambda: tmp_path)

    JsonSaver.delete_aeroplane(sample_plane)

    assert data_file.read_text(encoding="utf-8") == ""


def test_delete_aeroplane_prints_message_when_plane_not_found(tmp_path, monkeypatch, sample_plane, capsys) -> None:
    _prepare_data_file(tmp_path, text="[]")
    monkeypatch.setattr("src.classes.find_project_root", lambda: tmp_path)

    JsonSaver.delete_aeroplane(sample_plane)

    captured = capsys.readouterr()
    assert "Aeroplane not found" in captured.out
