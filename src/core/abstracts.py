from pathlib import Path


def _is_generated_global_summary(path: Path) -> bool:
    return path.name.lower().startswith("global-summary")


def collect_abstracts_for_scope(
    current_session_dir: Path,
    scope: str,
    explicit_dir: Path | None = None,
) -> list[Path]:
    if scope == "current_run":
        target_dir = current_session_dir / "abstracts"
    elif scope == "selected_dir":
        target_dir = explicit_dir
    else:
        return []

    if target_dir is None or not target_dir.exists() or not target_dir.is_dir():
        return []

    return sorted(
        path
        for path in target_dir.rglob("*.md")
        if path.is_file() and not _is_generated_global_summary(path)
    )
