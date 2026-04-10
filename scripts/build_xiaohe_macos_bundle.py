import argparse
import shutil
import zipfile
from datetime import date, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_APP = REPO_ROOT / "macos" / "MathQuestXiaohe.app"
RELEASE_ROOT = REPO_ROOT / "release"
APP_FILES = [
    "gui_admin_app.py",
    "desktop_runtime.py",
    "github_sync_server.py",
    "github_sync_common.py",
    "server.py",
    "index.html",
    "app-client.js",
    "app-extra.css",
]
DOC_FILES = [
    "README.md",
    "小和使用说明-mac.md",
]
EXECUTABLE_SUFFIXES = {
    "MathQuestXiaohe.app/Contents/MacOS/MathQuestXiaohe",
}


def build_release_name(stamp: str) -> str:
    return f"MathQuest-Xiaohe-macOS-{stamp}"


def copy_app_bundle(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(TEMPLATE_APP, destination)
    app_root = destination / "Contents" / "Resources" / "app"
    app_root.mkdir(parents=True, exist_ok=True)
    for relative_name in APP_FILES:
        source = REPO_ROOT / relative_name
        target = app_root / relative_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    launcher = destination / "Contents" / "MacOS" / "MathQuestXiaohe"
    launcher.chmod(0o755)


def copy_docs(destination: Path) -> None:
    for relative_name in DOC_FILES:
        source = REPO_ROOT / relative_name
        target = destination / relative_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def copy_release_manifest(destination: Path) -> None:
    lines = [
        "Math Quest Xiaohe macOS 发布包",
        "",
        "包含内容：",
        "- MathQuestXiaohe.app",
        "- README.md",
        "- 小和使用说明-mac.md",
        "",
        "说明：",
        "- 这是小和专用的 macOS 特别版。",
        "- 第一次打开如果被 macOS 拦住，请右键应用后选择“打开”。",
        "- 需要本机安装 Python 3.10 或更新版本。",
    ]
    (destination / "发布清单.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_zip(source_dir: Path, zip_path: Path) -> None:
    now = datetime.now()
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            relative = path.relative_to(source_dir)
            arcname = f"{source_dir.name}/{relative.as_posix()}"
            info = zipfile.ZipInfo(arcname + ("/" if path.is_dir() else ""))
            info.create_system = 3
            if path.is_dir():
                info.external_attr = (0o755 << 16) | 0x10
                archive.writestr(info, b"")
                continue
            permission = 0o755 if relative.as_posix() in EXECUTABLE_SUFFIXES else 0o644
            info.external_attr = permission << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info.date_time = now.timetuple()[:6]
            archive.writestr(info, path.read_bytes())


def build_release(stamp: str) -> tuple[Path, Path]:
    release_dir = RELEASE_ROOT / build_release_name(stamp)
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)
    app_bundle = release_dir / "MathQuestXiaohe.app"
    copy_app_bundle(app_bundle)
    copy_docs(release_dir)
    copy_release_manifest(release_dir)
    zip_path = RELEASE_ROOT / f"{build_release_name(stamp)}.zip"
    create_zip(release_dir, zip_path)
    return release_dir, zip_path


def main() -> int:
    parser = argparse.ArgumentParser(description="构建小和端 macOS 特别版发布包")
    parser.add_argument("--stamp", default=str(date.today()), help="发布日期，例如 2026-04-10")
    args = parser.parse_args()
    release_dir, zip_path = build_release(args.stamp)
    print(release_dir)
    print(zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
