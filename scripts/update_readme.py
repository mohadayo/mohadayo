"""GitHub Profile READMEを自動更新するスクリプト"""

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

JST = timezone(timedelta(hours=9))
README_PATH = Path(__file__).parent.parent / "README.md"
GITHUB_USER = "mohadayo"
BLOG_URL = "https://mohablog.com"
QIITA_USER = "moha0918_"


def fetch_github_repos(limit: int = 5) -> list[dict]:
    """直近の公開リポジトリを取得する"""
    resp = requests.get(
        f"https://api.github.com/users/{GITHUB_USER}/repos",
        params={"sort": "created", "direction": "desc", "per_page": limit, "type": "owner"},
        headers={"Accept": "application/vnd.github.v3+json"},
        timeout=15,
    )
    resp.raise_for_status()
    repos = []
    for r in resp.json():
        if r["fork"]:
            continue
        repos.append({
            "name": r["name"],
            "url": r["html_url"],
            "description": r["description"] or "",
            "language": r["language"] or "",
            "stars": r["stargazers_count"],
        })
    return repos[:limit]


def fetch_blog_posts(limit: int = 5) -> list[dict]:
    """mohablogの直近記事を取得する"""
    resp = requests.get(
        f"{BLOG_URL}/wp-json/wp/v2/posts",
        params={"per_page": limit, "_fields": "title,link,date"},
        timeout=15,
    )
    resp.raise_for_status()
    posts = []
    for p in resp.json():
        posts.append({
            "title": p["title"]["rendered"],
            "url": p["link"],
            "date": p["date"][:10],
        })
    return posts


def fetch_qiita_posts(limit: int = 5) -> list[dict]:
    """Qiitaの直近記事を取得する"""
    resp = requests.get(
        f"https://qiita.com/api/v2/users/{QIITA_USER}/items",
        params={"per_page": limit},
        headers={"Accept": "application/json"},
        timeout=15,
    )
    resp.raise_for_status()
    posts = []
    for p in resp.json():
        posts.append({
            "title": p["title"],
            "url": p["url"],
            "date": p["created_at"][:10],
            "likes": p["likes_count"],
        })
    return posts


def build_readme() -> str:
    """READMEのMarkdownを生成する"""
    now = datetime.now(JST).strftime("%Y/%m/%d %H:%M")

    blog_posts = fetch_blog_posts()
    qiita_posts = fetch_qiita_posts()

    # Blog posts セクション
    blog_md = ""
    for p in blog_posts:
        blog_md += f"- [{p['title']}]({p['url']}) ({p['date']})\n"

    # Qiita posts セクション
    qiita_md = ""
    for p in qiita_posts:
        qiita_md += f"- [{p['title']}]({p['url']}) ({p['date']})\n"

    readme = f"""<h1 align="center">Hi! Welcome to my GitHub!</h1>
<p align="center">
  <em>Backend Engineer / Freelance / Tokyo</em>
</p>

<p align="center">
  <a href="https://mohablog.com"><img src="https://img.shields.io/badge/Blog-mohablog-333?style=flat-square" alt="Blog" /></a>
  <a href="https://qiita.com/moha0918_"><img src="https://img.shields.io/badge/Qiita-moha0918__-55C500?style=flat-square&logo=qiita&logoColor=white" alt="Qiita" /></a>
  <a href="https://github.com/mohadayo"><img src="https://img.shields.io/badge/GitHub-mohadayo-181717?style=flat-square&logo=github" alt="GitHub" /></a>
</p>

---

### Tech Stack & Languages

<table>
  <tr>
    <td align="center" valign="middle">
      <img src="https://skillicons.dev/icons?i=python,go,fastapi,django&theme=light" alt="Tech Stack 1" /><br/>
      <img src="https://skillicons.dev/icons?i=docker,aws,postgres,githubactions&theme=light" alt="Tech Stack 2" />
    </td>
    <td align="center" valign="middle">
      <img src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username={GITHUB_USER}&theme=default" alt="Top Languages by Repo" />
    </td>
  </tr>
</table>

---

### Live Service

- [SES面談対策クイズ](https://github.com/mohadayo/rootage-ses-quiz) - SES企業向け面談対策アプリ (Go)

---

### Blog Posts
<!-- blog -->
{blog_md.strip()}
<!-- /blog -->

### Qiita Posts
<!-- qiita -->
{qiita_md.strip()}
<!-- /qiita -->

---

<p align="center">
  <sub>Last updated: {now} JST</sub>
</p>
"""
    return readme


def main():
    readme = build_readme()
    README_PATH.write_text(readme, encoding="utf-8")
    print(f"README.md updated ({len(readme)} chars)")


if __name__ == "__main__":
    main()
