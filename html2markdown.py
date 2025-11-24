#!/usr/bin/env python3
import argparse
import sys
import requests
from markdownify import markdownify as md

def fetch_html(url: str, timeout: int = 10) -> str:
    res = requests.get(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0 (html2md script)"
        },
    )
    res.raise_for_status()
    # 인코딩이 애매한 사이트 대비
    res.encoding = res.apparent_encoding
    return res.text

def extract_main_html(html: str) -> tuple[str, str]:
    """
    readability로 본문만 뽑아옴.
    return: (title, main_html)
    """
    from readability import Document  # 옵션 기능이라 내부 import
    doc = Document(html)
    title = doc.short_title() or ""
    main_html = doc.summary()
    return title, main_html

def html_to_markdown(html: str) -> str:
    return md(html, heading_style="ATX", bullets="-")

def main():
    parser = argparse.ArgumentParser(
        description="Convert a web page (HTML) to Markdown."
    )
    parser.add_argument("--url", required=True, help="Target URL to convert.")
    parser.add_argument("--output", "-o", help="Output markdown file path. If not set, print to stdout.")
    parser.add_argument("--main", action="store_true", help="Extract main article content using readability.")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout seconds (default: 10).")

    args = parser.parse_args()

    try:
        html = fetch_html(args.url, timeout=args.timeout)

        if args.main:
            title, main_html = extract_main_html(html)
            body_md = html_to_markdown(main_html)
            markdown = f"# {title}\n\n{body_md}" if title else body_md
        else:
            markdown = html_to_markdown(html)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(markdown)
        else:
            sys.stdout.write(markdown)

    except requests.HTTPError as e:
        print(f"[HTTP error] {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"[Request error] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[Error] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
