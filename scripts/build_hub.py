#!/usr/bin/env python3
"""Build the SIGAI-Pilot team hub static site.

Reads team.yaml, optionally fetches recent commits for each project_repo via
the GitHub API, and writes site/index.html + site/activity.json.

Run:
    python3 scripts/build_hub.py
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

try:
    import yaml
except ImportError as e:
    raise SystemExit("PyYAML required: pip install PyYAML") from e

ROOT = Path(__file__).resolve().parent.parent
TEAM_PATH = ROOT / "team.yaml"
SITE_DIR = ROOT / "site"
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


def load_team() -> list[dict]:
    data = yaml.safe_load(TEAM_PATH.read_text())
    return list(data.get("members") or [])


def render_html(members: list[dict], generated_at: str) -> str:
    cards = []
    for m in members:
        name = escape(m["name"])
        gh = escape(m["github"])
        repo = m.get("project_repo") or ""
        project_url = (m.get("project_url") or "").strip()
        commits = m.get("commits") or []
        docs = m.get("docs") or {}

        if project_url:
            label = project_url.replace("https://github.com/", "")
            repo_html = f'<a href="{escape(project_url)}">{escape(label)}</a>'
        elif repo:
            repo_html = (
                f'<a href="https://github.com/{escape(repo)}">{escape(repo)}</a>'
            )
        else:
            repo_html = "<em>no project repo listed yet</em>"
        docs_bits = []
        if docs.get("folder"):
            docs_bits.append(f'<a href="{escape(docs["folder"])}">docs folder</a>')
        for key in ("timeline.md", "issues.md", "prompts.md"):
            if docs.get(key):
                docs_bits.append(f'<a href="{escape(docs[key])}">{escape(key)}</a>')
        docs_html = " · ".join(docs_bits) if docs_bits else "<em>no SIGAI docs folder yet</em>"

        if commits:
            commit_lis = "".join(
                f'<li><a href="{escape(c["url"])}"><code>{escape(c["sha"])}</code></a> '
                f'{escape(c["message"])} '
                f'<span class="muted">{escape((c["date"] or "")[:10])}</span></li>'
                for c in commits
            )
            activity = f"<ul class='commits'>{commit_lis}</ul>"
        else:
            activity = "<p class='muted'>No recent commits fetched.</p>"

        cards.append(f"""
      <article class="card">
        <h2>{name}</h2>
        <p class="meta">
          <a href="https://github.com/{gh}">@{gh}</a><br>
          Project: {repo_html}<br>
          Docs: {docs_html}
        </p>
        <h3>Recent activity</h3>
        {activity}
      </article>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SIGAI Pilot — Team Hub</title>
<style>
  :root {{
    --bg: #0b0d10;
    --card: #161a20;
    --ink: #eef1f5;
    --muted: #8b95a3;
    --line: #2a313b;
    --accent: #7dd3fc;
    --font: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
    --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: var(--font);
    line-height: 1.5;
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
  header h1 {{ margin: 0 0 0.4rem; font-size: 1.8rem; }}
  header p {{ color: var(--muted); margin: 0 0 1.5rem; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 1rem 1.1rem 1.2rem;
  }}
  .card h2 {{ margin: 0 0 0.5rem; font-size: 1.15rem; }}
  .card h3 {{
    margin: 1rem 0 0.4rem;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
  }}
  .meta {{ font-size: 0.88rem; color: var(--muted); }}
  a {{ color: var(--accent); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .muted {{ color: var(--muted); font-size: 0.85rem; }}
  ul.commits {{ margin: 0; padding-left: 1.1rem; font-size: 0.88rem; }}
  ul.commits li {{ margin-bottom: 0.35rem; }}
  code {{ font-family: var(--mono); font-size: 0.85em; }}
  footer {{
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 0.8rem;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>SIGAI Pilot — Team Hub</h1>
      <p>
        Shared view of every member’s project repo and SIGAI docs.
        Rebuilds on docs merges to <code>main</code> and daily at 08:00 CT.
        Source: <a href="{REPO_URL}">{REPO_URL}</a>
      </p>
    </header>
    <div class="grid">
      {"".join(cards)}
    </div>
    <footer>
      Generated {escape(generated_at)} ·
      <a href="{HUB_URL}">{HUB_URL}</a>
    </footer>
  </div>
</body>
</html>
"""


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
                "commits": m.get("commits") or [],
            }
            for m in enriched
        ],
    }
    (SITE_DIR / "activity.json").write_text(json.dumps(activity, indent=2) + "\n")
    (SITE_DIR / "index.html").write_text(render_html(enriched, generated_at))
    print(f"Wrote {SITE_DIR / 'index.html'}")
    print(f"Wrote {SITE_DIR / 'activity.json'}")


if __name__ == "__main__":
    main()
