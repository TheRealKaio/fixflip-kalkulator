from pathlib import Path
import re
import sys

PATCH_RE = re.compile(r"_v8(\d{3})\.py$")
VISIBLE_RE = re.compile(r"V8\.\d{3}")
SW_QUERY_RE = re.compile(r"service-worker\.js\?v=8\.\d{3}")
SW_CACHE_RE = re.compile(r"neustart-immocheck-v8\.\d{3}")


def detect_release(repo_root=Path(".")):
    versions = []
    for patch in (repo_root / "scripts").glob("patch*_v8*.py"):
        m = PATCH_RE.search(patch.name)
        if m:
            versions.append(int(m.group(1)))
    if not versions:
        raise SystemExit("Release contract failed - no release patch version found")
    build = max(versions)
    plain = f"8.{build:03d}"
    display = f"V{plain}"
    return build, plain, display


def normalize(site_dir=Path("_site"), repo_root=Path(".")):
    _, plain, display = detect_release(repo_root)
    index_path = site_dir / "index.html"
    sw_path = site_dir / "service-worker.js"
    index = index_path.read_text(encoding="utf-8")
    sw = sw_path.read_text(encoding="utf-8")

    index = VISIBLE_RE.sub(display, index)
    index = SW_QUERY_RE.sub(f"service-worker.js?v={plain}", index)
    sw = SW_CACHE_RE.sub(f"neustart-immocheck-v{plain}", sw)

    index_path.write_text(index, encoding="utf-8")
    sw_path.write_text(sw, encoding="utf-8")
    admin_path=site_dir / "admin.html"
    if admin_path.exists():
        admin_path.write_text(VISIBLE_RE.sub(display, admin_path.read_text(encoding="utf-8")), encoding="utf-8")
    (site_dir / ".release-version").write_text(display, encoding="utf-8")
    print(f"Release contract normalized to {display}")


def verify(site_dir=Path("_site"), repo_root=Path(".")):
    _, plain, expected = detect_release(repo_root)
    marker = site_dir / ".release-version"
    if not marker.exists():
        raise SystemExit("Release contract failed - .release-version missing")
    actual = marker.read_text(encoding="utf-8").strip()
    if actual != expected:
        raise SystemExit(f"Release contract failed - marker {actual!r} != detected {expected!r}")

    index = (site_dir / "index.html").read_text(encoding="utf-8")
    sw = (site_dir / "service-worker.js").read_text(encoding="utf-8")

    visible = sorted(set(VISIBLE_RE.findall(index)))
    registrations = sorted(set(SW_QUERY_RE.findall(index)))
    caches = sorted(set(SW_CACHE_RE.findall(sw)))

    checks = {
        "visible version": visible == [expected],
        "admin version": sorted(set(VISIBLE_RE.findall((site_dir / "admin.html").read_text(encoding="utf-8")))) == [expected],
        "service-worker registration": registrations == [f"service-worker.js?v={plain}"],
        "service-worker cache": caches == [f"neustart-immocheck-v{plain}"],
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Release contract failed - "
            + ", ".join(failed)
            + f" | expected={expected}, visible={visible}, registrations={registrations}, caches={caches}"
        )
    print(f"Release contract verified: {expected}")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "verify"
    site = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("_site")
    if action == "normalize":
        normalize(site)
    elif action == "verify":
        verify(site)
    elif action == "detect":
        print(detect_release()[2])
    else:
        raise SystemExit(f"Unknown release contract action: {action}")


if __name__ == "__main__":
    main()
