#!/usr/bin/env python3
"""Copy files that live in one place into the skill folders that need them.

Each file has one home, in shared/ or templates/. COPIES lists where it goes.
Run this after you edit a source file. Never edit a copy.

  python3 tools/sync_shared.py          copy every source that differs
  python3 tools/sync_shared.py --check  copy nothing; fail if a copy differs

Standard library only.
"""

import filecmp
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COPIES = {
    "templates/doc-profile.md": ["skills/doc-setup/profile-template.md"],
    "templates/project-instructions.md": ["skills/doc-setup/project-instructions.md"],
    "templates/claude-md-snippet.md": ["skills/doc-setup/claude-md-snippet.md"],
    "templates/doc-map.md": ["skills/doc-flow/map-template.md"],
    "shared/docx_tool.py": ["skills/human-write/scripts/docx_tool.py", "skills/doc-flow/scripts/docx_tool.py",
                            "skills/doc-check/scripts/docx_tool.py"],
    "shared/check_protected.py": ["skills/human-write/scripts/check_protected.py",
                                  "skills/doc-flow/scripts/check_protected.py"],
    "shared/doc_stats.py": ["skills/human-write/scripts/doc_stats.py", "skills/doc-flow/scripts/doc_stats.py",
                            "skills/doc-check/scripts/doc_stats.py"],
    "shared/word-output.md": ["skills/human-write/word-output.md", "skills/doc-flow/word-output.md"],
    "shared/text-output.md": ["skills/human-write/text-output.md", "skills/doc-flow/text-output.md",
                              "skills/notation-check/text-output.md"],
    "shared/word_diff.py": ["skills/human-write/scripts/word_diff.py", "skills/doc-flow/scripts/word_diff.py",
                            "skills/notation-check/scripts/word_diff.py"],
}


def stale_copies():
    """(source, copy) pairs where the copy is missing or differs."""
    out = []
    for source, copies in COPIES.items():
        for copy in copies:
            src, dst = os.path.join(ROOT, source), os.path.join(ROOT, copy)
            if not (os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)):
                out.append((source, copy))
    return out


def main(argv):
    stale = stale_copies()
    if "--check" in argv:
        for source, copy in stale:
            print("out of sync: %s (source: %s). Run python3 tools/sync_shared.py" % (copy, source))
        return 1 if stale else 0
    for source, copy in stale:
        dst = os.path.join(ROOT, copy)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, source), dst)
        print("copied %s -> %s" % (source, copy))
    if not stale:
        print("all copies are in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
