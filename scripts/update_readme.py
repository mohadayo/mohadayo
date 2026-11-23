"""GitHub Profile READMEのQiita記事セクションのみを自動更新するスクリプト"""

import re
from pathlib import Path

import requests

README_PATH = Path(__file__).parent.parent / "README.md"
QIITA_USER = "moha0918_"


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
    # 欄が空（目印が2行続くだけ）でも置き換えられるよう、閉じる目印の前の改行は content の側に付ける。
    # 記事の題に「\」があっても置き換えの記号として読まれないよう、関数で差し込む
    pattern = rf"(<!-- {tag} -->\n).*?(<!-- /{tag} -->)"
    return re.sub(pattern, lambda m: m.group(1) + content + "\n" + m.group(2), readme, flags=re.DOTALL)


def main():
    readme = README_PATH.read_text(encoding="utf-8")

    qiita_posts = fetch_qiita_posts(limit=3)

    if qiita_posts:
        qiita_md = "\n".join(
            f"- [{p['title']}]({p['url']}) ({p['date']})" for p in qiita_posts
        )
        readme = replace_section(readme, "qiita", qiita_md)

    README_PATH.write_text(readme, encoding="utf-8")
    print(f"README.md updated ({len(readme)} chars)")


if __name__ == "__main__":
    main()
