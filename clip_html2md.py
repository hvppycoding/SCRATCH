#!/usr/bin/env python3
import sys
import pyperclip
from markdownify import markdownify as md

def html_clipboard_to_markdown_clipboard():
    html = pyperclip.paste()

    if not html or "<" not in html:
        print("클립보드에 HTML 소스(태그 포함)가 없는 것 같아요.", file=sys.stderr)
        return 1

    markdown = md(
        html,
        heading_style="ATX",  # # 헤딩 스타일
        bullets="-"           # 리스트 불릿을 - 로
    ).strip()

    pyperclip.copy(markdown)
    print("변환 완료: Markdown이 클립보드에 복사됐습니다.")
    return 0

if __name__ == "__main__":
    raise SystemExit(html_clipboard_to_markdown_clipboard())
