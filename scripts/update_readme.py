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

    repos = fetch_github_repos()
    blog_posts = fetch_blog_posts()
    qiita_posts = fetch_qiita_posts()

    # GitHub repos セクション
    repos_md = ""
    for r in repos:
        lang = f" `{r['language']}`" if r["language"] else ""
        repos_md += f"- [{r['name']}]({r['url']}){lang} - {r['description']}\n"

    # Blog posts セクション
    blog_md = ""
    for p in blog_posts:
        blog_md += f"- [{p['title']}]({p['url']}) ({p['date']})\n"

    # Qiita posts セクション
    qiita_md = ""
    for p in qiita_posts:
        qiita_md += f"- [{p['title']}]({p['url']}) ({p['date']})\n"

    readme = f"""## moha

バックエンドエンジニア / フリーランス

Python・Go・Claude Codeを軸に開発しています。

---

### Latest Blog Posts
<!-- blog -->
{blog_md.strip()}
<!-- /blog -->

### Latest Qiita Posts
<!-- qiita -->
{qiita_md.strip()}
<!-- /qiita -->

### Latest Repositories
<!-- repos -->
{repos_md.strip()}
<!-- /repos -->

---

<sub>Last updated: {now} JST</sub>
"""
    return readme


def main():
    readme = build_readme()
    README_PATH.write_text(readme, encoding="utf-8")
    print(f"README.md updated ({len(readme)} chars)")


if __name__ == "__main__":
    main()
