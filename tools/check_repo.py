#!/usr/bin/env python3
"""Check the repo against the mechanical rules in CLAUDE.md.

1. No em or en dash in any tracked text file, except the built samples.
2. Every skills/*/SKILL.md has a valid frontmatter: a name that matches its
   folder, a description under 200 characters, and a body of at most 900 words.
3. Every copy made by tools/sync_shared.py matches its source.
4. The plugin manifests in .claude-plugin/ parse, list the repo itself as the
   one plugin, and carry the same version as every SKILL.md.

  python3 tools/check_repo.py

Standard library only. It asks git for the list of tracked files.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_shared  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHES = ("\u2014", "\u2013")
BINARY = (".docx", ".pdf", ".zip", ".png", ".jpg", ".gif")
MAX_WORDS = 900
MAX_DESCRIPTION = 200


def tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, stdout=subprocess.PIPE, check=True)
    return out.stdout.decode("utf-8").splitlines()


def check_dashes(problems):
    for path in tracked_files():
        if path.endswith(BINARY) or "/built/" in path:
            continue
        with open(os.path.join(ROOT, path), encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                if any(d in line for d in DASHES):
                    problems.append("%s:%d: em or en dash" % (path, n))


def check_skills(problems):
    skills_dir = os.path.join(ROOT, "skills")
    if not os.path.isdir(skills_dir):
        return
    for name in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, name, "SKILL.md")
        if not os.path.isfile(path):
            problems.append("skills/%s: no SKILL.md" % name)
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
        if not m:
            problems.append("skills/%s/SKILL.md: no frontmatter" % name)
            continue
        front, body = m.group(1), m.group(2)
        fields = dict(re.findall(r"^([a-z-]+):\s*(.*)$", front, re.M))
        if fields.get("name") != name:
            problems.append("skills/%s/SKILL.md: name is %r, not the folder name" % (name, fields.get("name")))
        if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
            problems.append("skills/%s: the name must be lowercase letters, digits and hyphens" % name)
        description = fields.get("description", "")
        if not description:
            problems.append("skills/%s/SKILL.md: no description" % name)
        elif len(description) >= MAX_DESCRIPTION:
            problems.append("skills/%s/SKILL.md: description has %d characters" % (name, len(description)))
        words = len(body.split())
        if words > MAX_WORDS:
            problems.append("skills/%s/SKILL.md: body has %d words" % (name, words))


def skill_versions():
    """{skill name: the version in its SKILL.md metadata}"""
    versions = {}
    skills_dir = os.path.join(ROOT, "skills")
    for name in sorted(os.listdir(skills_dir)):
        path = os.path.join(skills_dir, name, "SKILL.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                m = re.search(r'^---\n.*?^\s+version:\s*"?([0-9.]+)"?\s*$.*?^---$', f.read(), re.S | re.M)
            versions[name] = m.group(1) if m else ""
    return versions


def check_plugin(problems):
    folder = os.path.join(ROOT, ".claude-plugin")
    manifests = {}
    for name in ("plugin.json", "marketplace.json"):
        try:
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                manifests[name] = json.load(f)
        except (OSError, ValueError) as err:
            problems.append(".claude-plugin/%s: %s" % (name, err))
    if len(manifests) < 2:
        return
    plugin, market = manifests["plugin.json"], manifests["marketplace.json"]
    for field in ("name", "version", "description"):
        if not plugin.get(field):
            problems.append(".claude-plugin/plugin.json: no %s" % field)
    if not market.get("name") or not market.get("owner", {}).get("name") or not market.get("plugins"):
        problems.append(".claude-plugin/marketplace.json: it needs a name, an owner name and plugins")
    entries = [e for e in market.get("plugins", []) if e.get("name") == plugin.get("name")]
    if len(market.get("plugins", [])) != 1 or len(entries) != 1 or entries[0].get("source") != "./":
        problems.append('.claude-plugin/marketplace.json: list one plugin, named as in plugin.json, with source "./"')
    elif "version" in entries[0]:
        problems.append(".claude-plugin/marketplace.json: give the version in plugin.json only")
    version = plugin.get("version", "")
    for name, v in skill_versions().items():
        if not v or not (version == v or version.startswith(v + ".")):
            problems.append("skills/%s/SKILL.md: version %r does not match plugin.json's %r" % (name, v, version))
    if os.path.exists(os.path.join(ROOT, "bin")):
        problems.append("bin/: claude.ai refuses a plugin with a top-level bin/ folder")


def main():
    problems = []
    check_dashes(problems)
    check_skills(problems)
    check_plugin(problems)
    for source, copy in sync_shared.stale_copies():
        problems.append("%s: out of sync with %s" % (copy, source))
    for line in problems:
        print(line)
    print("check_repo: %s" % ("%d problem(s)" % len(problems) if problems else "all checks pass"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
