#!/usr/bin/env python3
"""Build the SIGAI-Pilot team hub static site.

Reads team.yaml, fetches recent commits for each project_repo via the GitHub
API, and writes site/activity.json. The page itself is the tracked static file
hub/index.html, copied to site/ as-is — it renders entirely from activity.json
in the browser, so there is no HTML templating here.

Run:
    python3 scripts/build_hub.py
"""

from __future__ import annotations

import json
import os
import shutil
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError as e:
    raise SystemExit("PyYAML required: pip install PyYAML") from e

ROOT = Path(__file__).resolve().parent.parent
TEAM_PATH = ROOT / "team.yaml"
SITE_DIR = ROOT / "site"
PAGE_PATH = ROOT / "hub" / "index.html"
HUB_URL = "https://laynieily.github.io/SIGAI-Pilot/"
REPO_URL = "https://github.com/laynieily/SIGAI-Pilot"


def _api_get(url: str, token: str | None) -> list | dict | None:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "SIGAI-Pilot-hub-builder",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  warn: {url} → HTTP {e.code}")
        return None
    except Exception as e:  # noqa: BLE001 — keep build going if one repo fails
        print(f"  warn: {url} → {e}")
        return None


def fetch_commits(repo: str, token: str | None, n: int = 5) -> list[dict]:
    if not repo:
        return []
    data = _api_get(
        f"https://api.github.com/repos/{repo}/commits?per_page={n}", token
    )
    if not isinstance(data, list):
        return []
    out = []
    for c in data:
        commit = c.get("commit") or {}
        author = commit.get("author") or {}
        out.append({
            "sha": (c.get("sha") or "")[:7],
            "message": (commit.get("message") or "").split("\n", 1)[0][:120],
            "date": author.get("date") or "",
            "url": c.get("html_url") or f"https://github.com/{repo}",
        })
    return out


def docs_links(docs_path: str) -> dict[str, str]:
    if not docs_path:
        return {}
    base = f"{REPO_URL}/tree/main/{docs_path}"
    blob = f"{REPO_URL}/blob/main/{docs_path}"
    links = {"folder": base}
    for name in ("timeline.md", "issues.md", "prompts.md"):
        if (ROOT / docs_path / name).exists():
            links[name] = f"{blob}/{name}"
    return links


def status_note(docs_path: str) -> dict[str, str | bool]:
    """Read the trailing '## Current status' block from a member's timeline.md.

    Members already write this by hand; treating it as the status source beats
    maintaining a separate flag. 'complete'/'done' in the block marks the
    project wrapped.
    """
    if not docs_path:
        return {}
    path = ROOT / docs_path / "timeline.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    marker = text.lower().rfind("## current status")
    if marker == -1:
        return {}
    block = text[marker:].split("\n", 1)[1] if "\n" in text[marker:] else ""
    lines = [
        ln.strip().lstrip("-* ").strip()
        for ln in block.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not lines:
        return {}
    joined = " ".join(lines).lower()
    return {
        "note": lines[0][:200],
        "as_of": text[marker:].split("\n", 1)[0].strip("# ").strip(),
        "done": ("all six phases are complete" in joined)
        or ("all phases are complete" in joined)
        or ("project complete" in joined),
    }


def load_team() -> list[dict]:
    data = yaml.safe_load(TEAM_PATH.read_text())
    return list(data.get("members") or [])


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    members = load_team()
    print(f"Loaded {len(members)} members from {TEAM_PATH.name}")

    enriched = []
    for m in members:
        entry = dict(m)
        repo = (m.get("project_repo") or "").strip()
        docs_path = (m.get("docs_path") or "").strip()
        print(f"- {m['name']}: repo={repo or '(none)'} docs={docs_path or '(none)'}")
        entry["commits"] = fetch_commits(repo, token)
        entry["docs"] = docs_links(docs_path)
        entry["status_note"] = status_note(docs_path)
        enriched.append(entry)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    SITE_DIR.mkdir(exist_ok=True)
    activity = {
        "generated_at": generated_at,
        "members": [
            {
                "name": m["name"],
                "github": m["github"],
                "project_repo": m.get("project_repo") or "",
                "docs_path": m.get("docs_path") or "",
                # Which standard docs actually exist on disk, e.g. ["timeline.md", "issues.md"].
                "docs_present": [
                    k for k in ("timeline.md", "issues.md", "prompts.md")
                    if (m.get("docs") or {}).get(k)
                ],
                # Status comes from the member's own timeline.md "## Current status"
                # block; "status: done" in team.yaml overrides it.
                "status": "done"
                if (m.get("status") or "").strip().lower() == "done"
                or (m.get("status_note") or {}).get("done")
                else (m.get("status") or "").strip().lower(),
                "status_note": (m.get("status_note") or {}).get("note", ""),
                "status_as_of": (m.get("status_note") or {}).get("as_of", ""),
                "project_url": m.get("project_url") or "",
                "commits": m.get("commits") or [],
            }
            for m in enriched
        ],
    }
    (SITE_DIR / "activity.json").write_text(json.dumps(activity, indent=2) + "\n")
    print(f"Wrote {SITE_DIR / 'activity.json'}")

    if PAGE_PATH.exists():
        shutil.copyfile(PAGE_PATH, SITE_DIR / "index.html")
        print(f"Copied {PAGE_PATH.relative_to(ROOT)} → {SITE_DIR / 'index.html'}")
    else:
        raise SystemExit(f"Missing {PAGE_PATH.relative_to(ROOT)} — the hub page is tracked there.")


if __name__ == "__main__":
    main()
