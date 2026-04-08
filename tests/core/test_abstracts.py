import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from core.abstracts import collect_abstracts_for_scope


def test_collect_abstracts_for_scope_current_run_returns_sorted_recursive_files(tmp_path):
    session_dir = tmp_path / "session_3"
    abstracts_dir = session_dir / "abstracts"
    nested_dir = abstracts_dir / "playlist"
    nested_dir.mkdir(parents=True)

    file_a = abstracts_dir / "a.md"
    file_b = nested_dir / "b.md"
    (abstracts_dir / "ignore.txt").write_text("x", encoding="utf-8")
    file_a.write_text("a", encoding="utf-8")
    file_b.write_text("b", encoding="utf-8")

    collected = collect_abstracts_for_scope(session_dir, scope="current_run")

    assert collected == sorted([file_a, file_b])


def test_collect_abstracts_for_scope_selected_dir_uses_explicit_dir(tmp_path):
    selected_dir = tmp_path / "manual-abstracts"
    nested_dir = selected_dir / "topic"
    nested_dir.mkdir(parents=True)

    file_a = selected_dir / "z.md"
    file_b = nested_dir / "x.md"
    file_a.write_text("z", encoding="utf-8")
    file_b.write_text("x", encoding="utf-8")

    collected = collect_abstracts_for_scope(
        current_session_dir=tmp_path / "unused-session",
        scope="selected_dir",
        explicit_dir=selected_dir,
    )

    assert collected == sorted([file_a, file_b])


def test_collect_abstracts_for_scope_returns_empty_on_missing_or_invalid_inputs(tmp_path):
    session_dir = tmp_path / "session_10"

    assert collect_abstracts_for_scope(session_dir, scope="current_run") == []
    assert collect_abstracts_for_scope(session_dir, scope="selected_dir") == []

    not_a_directory = tmp_path / "single.md"
    not_a_directory.write_text("content", encoding="utf-8")
    assert collect_abstracts_for_scope(
        current_session_dir=session_dir,
        scope="selected_dir",
        explicit_dir=not_a_directory,
    ) == []

    assert collect_abstracts_for_scope(session_dir, scope="unsupported") == []
