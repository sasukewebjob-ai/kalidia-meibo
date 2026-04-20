"""
members.txt を読み込んで index.html 内の RAW 定数を更新するスクリプト。
使い方:
    python update_members.py
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
MEMBERS_FILE = BASE_DIR / "members.txt"
HTML_FILE = BASE_DIR / "index.html"


def parse_members(txt_path: Path):
    """members.txt を読み、[男性] と [女性] セクションごとに名前リストを返す。"""
    male, female = [], []
    section = None
    for raw in txt_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[男性]":
            section = "male"
        elif line == "[女性]":
            section = "female"
        elif section == "male":
            male.append(line)
        elif section == "female":
            female.append(line)
    return male, female


def format_names(names, per_line=6, indent="                "):
    """名前リストを 'A', 'B', 'C' 形式で per_line 件ずつ折り返す。
    1行目はキー行の続きに書くので indent を付けない。"""
    chunks = [names[i:i + per_line] for i in range(0, len(names), per_line)]
    lines = []
    for idx, chunk in enumerate(chunks):
        joined = ", ".join(f"'{n}'" for n in chunk)
        lines.append(("" if idx == 0 else indent) + joined)
    return ",\n".join(lines)


def build_raw_js(male, female):
    """JS の RAW 定数文字列を生成する。インデントは index.html に合わせる。"""
    return (
        "const RAW = {\n"
        f"            male: [{format_names(male)}],\n"
        f"            female: [{format_names(female)}]\n"
        "        };"
    )


def update_html(html_path: Path, new_raw_js: str) -> bool:
    html = html_path.read_text(encoding="utf-8")
    new_html, count = re.subn(r"const RAW = \{.*?\};", new_raw_js, html, flags=re.DOTALL)
    if count == 0:
        print("エラー: index.html 内に RAW 定数が見つかりませんでした。")
        return False
    html_path.write_text(new_html, encoding="utf-8")
    return True


def main():
    print("=== KALIDIA名簿 メンバー同期ツール ===\n")

    if not MEMBERS_FILE.exists():
        print(f"エラー: {MEMBERS_FILE} が見つかりません。")
        return

    male, female = parse_members(MEMBERS_FILE)
    print(f"読み込み: {MEMBERS_FILE.name}")
    print(f"  男性 {len(male)}名: {', '.join(male)}")
    print(f"  女性 {len(female)}名: {', '.join(female)}")

    if not male and not female:
        print("\nエラー: メンバーが0人です。")
        return

    new_raw_js = build_raw_js(male, female)

    print(f"\n更新: {HTML_FILE.name}")
    if update_html(HTML_FILE, new_raw_js):
        print("完了: RAW 定数を更新しました。ブラウザで index.html を再読み込みしてください。")
    else:
        print("更新に失敗しました。")


if __name__ == "__main__":
    main()
