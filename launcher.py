import os
import sys
from pathlib import Path

from streamlit.web import cli as stcli


def bundled_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def configure_runtime_environment(base_dir: Path):
    os.chdir(base_dir)
    candidates = []
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        candidates.append(Path(local_appdata) / "iTrain" / "reports")
    candidates.append(Path.home() / "Documents" / "iTrain" / "reports")
    candidates.append(Path.home() / "iTrain" / "reports")
    candidates.append(base_dir / "reports")

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("ITRAIN_REPORTS_DIR", str(candidate))
            return
        except OSError:
            continue


def main():
    base_dir = bundled_root()
    configure_runtime_environment(base_dir)
    app_path = base_dir / "app" / "main.py"
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",
    ]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
