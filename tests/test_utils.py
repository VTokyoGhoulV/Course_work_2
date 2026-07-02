import pytest

from src.utils import find_project_root, user_interaction


def test_user_interaction_reads_and_converts_console_input(monkeypatch) -> None:
    answers = iter(["Belarus", "5", "Belarus Germany", "1000-10000"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    result = user_interaction()

    assert result == ("Belarus", 5, ["Belarus", "Germany"], "1000-10000")


def test_user_interaction_raises_value_error_for_non_integer_top_n(monkeypatch) -> None:
    answers = iter(["Belarus", "not-int"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    with pytest.raises(ValueError):
        user_interaction()


def test_find_project_root_finds_marker_in_current_directory(tmp_path, monkeypatch) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = find_project_root()

    assert result == tmp_path


def test_find_project_root_finds_marker_in_parent_directory(tmp_path, monkeypatch) -> None:
    project_root = tmp_path / "project"
    nested_dir = project_root / "src" / "package"
    nested_dir.mkdir(parents=True)
    (project_root / "requirements.txt").write_text("requests", encoding="utf-8")
    monkeypatch.chdir(nested_dir)

    result = find_project_root(marker_files=("pyproject.toml", "requirements.txt"))

    assert result == project_root


def test_find_project_root_accepts_custom_marker_tuple(tmp_path, monkeypatch) -> None:
    nested_dir = tmp_path / "a" / "b"
    nested_dir.mkdir(parents=True)
    (tmp_path / "custom.marker").write_text("", encoding="utf-8")
    monkeypatch.chdir(nested_dir)

    result = find_project_root(marker_files=("custom.marker",))

    assert result == tmp_path


def test_find_project_root_raises_runtime_error_when_marker_is_missing(tmp_path, monkeypatch) -> None:
    nested_dir = tmp_path / "without" / "markers"
    nested_dir.mkdir(parents=True)
    monkeypatch.chdir(nested_dir)

    with pytest.raises(RuntimeError, match="Не удалось найти корень проекта"):
        find_project_root(marker_files=("definitely-missing.marker",))
