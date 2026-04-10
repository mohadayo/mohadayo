"""GitHub Profile READMEのブログ・Qiita記事セクションのみを自動更新するスクリプト"""

import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

JST = timezone(timedelta(hours=9))
README_PATH = Path(__file__).parent.parent / "README.md"
BLOG_URL = "https://mohablog.com"
QIITA_USER = "moha0918_"


def fetch_blog_posts(limit: int = 3) -> list[dict]:
    """mohablogの直近記事を取得する"""
    try:
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
    except Exception as e:
        print(f"Warning: ブログ記事の取得に失敗しました: {e}")
        return []


def fetch_qiita_posts(limit: int = 3) -> list[dict]:
    """Qiitaの直近記事を取得する"""
    try:
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
            })
        return posts
    except Exception as e:
        print(f"Warning: Qiita記事の取得に失敗しました: {e}")
        return []


def replace_section(readme: str, tag: str, content: str) -> str:
    """<!-- tag --> ... <!-- /tag --> の間を置換する"""
    pattern = rf"(<!-- {tag} -->\n).*?(\n<!-- /{tag} -->)"
    replacement = rf"\g<1>{content}\g<2>"
    return re.sub(pattern, replacement, readme, flags=re.DOTALL)


def update_timestamp(readme: str) -> str:
    """Last updatedのタイムスタンプを更新する"""
    now = datetime.now(JST).strftime("%Y/%m/%d %H:%M")
    return re.sub(
        r"<sub>Last updated: .+? JST</sub>",
        f"<sub>Last updated: {now} JST</sub>",
        readme,
    )


def main():
    readme = README_PATH.read_text(encoding="utf-8")

    blog_posts = fetch_blog_posts(limit=3)
    qiita_posts = fetch_qiita_posts(limit=3)

    if blog_posts:
        blog_md = "\n".join(
            f"- [{p['title']}]({p['url']}) ({p['date']})" for p in blog_posts
        )
        readme = replace_section(readme, "blog", blog_md)

    if qiita_posts:
        qiita_md = "\n".join(
            f"- [{p['title']}]({p['url']}) ({p['date']})" for p in qiita_posts
        )
        readme = replace_section(readme, "qiita", qiita_md)

    readme = update_timestamp(readme)

    README_PATH.write_text(readme, encoding="utf-8")
    print(f"README.md updated ({len(readme)} chars)")


if __name__ == "__main__":
    main()
