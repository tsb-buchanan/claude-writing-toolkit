#!/usr/bin/env python3
"""Build the release zips in dist/.

1. One zip per skill, for claude.ai: dist/<skill>.zip holds the folder <skill>/.
2. One zip with every skill, for Claude Code: dist/writing-toolkit-skills.zip.
3. The web guide as a Word file: dist/web-guide.docx, from docs/web-guide.md.

Run tools/check_repo.py first. The zips are not tracked in git.
Standard library only.
"""

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
DIST = os.path.join(ROOT, "dist")
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def skill_files(name):
    base = os.path.join(SKILLS, name)
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for filename in sorted(filenames):
            full = os.path.join(dirpath, filename)
            yield full, os.path.relpath(full, SKILLS)


def add_skill(z, name):
    folders = set()
    for full, arc in skill_files(name):
        parts = arc.split(os.sep)
        for i in range(1, len(parts)):
            folder = "/".join(parts[:i]) + "/"
            if folder not in folders:
                folders.add(folder)
                info = zipfile.ZipInfo(folder, date_time=FIXED_TIME)
                info.external_attr = 0o40755 << 16
                z.writestr(info, b"")
        info = zipfile.ZipInfo("/".join(parts), date_time=FIXED_TIME)
        info.external_attr = (0o100755 if full.endswith(".py") else 0o100644) << 16
        with open(full, "rb") as f:
            z.writestr(info, f.read(), compress_type=zipfile.ZIP_DEFLATED)


def main():
    names = sorted(n for n in os.listdir(SKILLS) if os.path.isfile(os.path.join(SKILLS, n, "SKILL.md")))
    os.makedirs(DIST, exist_ok=True)
    for name in names:
        path = os.path.join(DIST, name + ".zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            add_skill(z, name)
        print("wrote %s" % os.path.relpath(path, ROOT))
    path = os.path.join(DIST, "writing-toolkit-skills.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names:
            add_skill(z, name)
    print("wrote %s" % os.path.relpath(path, ROOT))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_guide
    print("wrote %s" % os.path.relpath(build_guide.build(out=os.path.join(DIST, "web-guide.docx")), ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
