import os
import sys
from pathlib import Path


def bundled_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    return bundled_root().joinpath(*parts)


def default_reports_dir() -> Path:
    override = os.getenv("ITRAIN_REPORTS_DIR")
    if override:
        return Path(override)

    if getattr(sys, "frozen", False):
        local_appdata = os.getenv("LOCALAPPDATA")
        candidates = []
        if local_appdata:
            candidates.append(Path(local_appdata) / "iTrain" / "reports")
        candidates.append(Path.home() / "Documents" / "iTrain" / "reports")
        candidates.append(Path.home() / "iTrain" / "reports")

        for candidate in candidates:
            try:
                candidate.mkdir(parents=True, exist_ok=True)
                return candidate
            except OSError:
                continue

        return Path.cwd() / "reports"

    return resource_path("app", "reports")
