#!/usr/bin/env python3
"""Static quality gate for the first five independently authored articles."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_EVIDENCE_STATUS = {"verified", "derived", "illustrative", "unverified"}


class ArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.local_anchors: list[str] = []
        self.external_assets: list[str] = []
        self.figure_count = 0
        self.svg_count = 0
        self.caption_count = 0
        self.button_count = 0
        self._active_heading: str | None = None
        self._heading_text = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag in {"h1", "h2"}:
            self._active_heading = tag
            self._heading_text = ""
        if tag == "figure":
            self.figure_count += 1
        if tag == "svg":
            self.svg_count += 1
        if tag == "figcaption":
            self.caption_count += 1
        if tag == "button":
            self.button_count += 1
        if tag == "a" and values.get("href", "").startswith("#"):
            self.local_anchors.append(str(values["href"])[1:])
        if tag == "script" and values.get("src", "").startswith(("http://", "https://")):
            self.external_assets.append(str(values["src"]))
        if tag == "link" and "stylesheet" in values.get("rel", "").split():
            href = str(values.get("href", ""))
            if href.startswith(("http://", "https://")):
                self.external_assets.append(href)

    def handle_data(self, data: str) -> None:
        if self._active_heading:
            self._heading_text += data

    def handle_endtag(self, tag: str) -> None:
        if tag == self._active_heading:
            self.headings.append((tag, self._heading_text.strip()))
            self._active_heading = None
            self._heading_text = ""


def check_article(article: dict[str, str]) -> list[str]:
    errors: list[str] = []
    md_path = ROOT / article["markdown"]
    html_path = ROOT / article["html"]
    example_path = ROOT / article["example"]
    evidence_path = ROOT / article["evidence"]
    diagram_path = ROOT / article["diagram"]

    for path in (md_path, html_path, example_path, evidence_path, diagram_path):
        if not path.is_file():
            errors.append(f"missing file: {path.relative_to(ROOT)}")
    if errors:
        return errors

    markdown = md_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    markdown_title = re.search(r"^#\s+(.+)$", markdown, re.M)
    markdown_h2 = re.findall(r"^##\s+(.+)$", markdown, re.M)
    if not markdown_title:
        errors.append(f"{article['id']}: Markdown has no H1")
    elif markdown_title.group(1).strip() != article["title"]:
        errors.append(f"{article['id']}: article-index title differs from Markdown H1")

    parsed = ArticleParser()
    parsed.feed(html)
    h1 = [text for tag, text in parsed.headings if tag == "h1"]
    h2 = [text for tag, text in parsed.headings if tag == "h2"]
    if len(h1) != 1:
        errors.append(f"{article['id']}: expected one H1, found {len(h1)}")
    elif markdown_title and h1[0] != markdown_title.group(1).strip():
        errors.append(f"{article['id']}: HTML H1 differs from Markdown H1")
    if h2 != markdown_h2:
        errors.append(f"{article['id']}: Markdown/HTML H2 mismatch\n  MD: {markdown_h2}\n  HTML: {h2}")
    if parsed.figure_count < 1 or parsed.svg_count < 1 or parsed.caption_count < 1:
        errors.append(f"{article['id']}: expected an accessible figure, SVG and caption")
    if parsed.button_count != 1:
        errors.append(f"{article['id']}: expected exactly one working demo button")
    missing_anchors = sorted(set(parsed.local_anchors) - parsed.ids)
    if missing_anchors:
        errors.append(f"{article['id']}: broken local anchors {missing_anchors}")
    if parsed.external_assets:
        errors.append(f"{article['id']}: external CSS/JS dependencies are not allowed: {parsed.external_assets}")
    if "讲义介绍了" in markdown or "讲义介绍了" in html:
        errors.append(f"{article['id']}: article must stand alone without lecture-dependent wording")

    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        claims = evidence.get("claims", [])
        if not claims:
            errors.append(f"{article['id']}: evidence ledger has no claims")
        for claim in claims:
            if claim.get("status") not in ALLOWED_EVIDENCE_STATUS:
                errors.append(f"{article['id']}: invalid evidence status for {claim.get('id')}")
            if not claim.get("source_url", "").startswith("https://"):
                errors.append(f"{article['id']}: evidence claim {claim.get('id')} has no HTTPS source")
            if not claim.get("locator"):
                errors.append(f"{article['id']}: evidence claim {claim.get('id')} has no locator")
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"{article['id']}: invalid evidence ledger: {exc}")

    try:
        svg_root = ET.fromstring(diagram_path.read_text(encoding="utf-8"))
        local_names = {node.tag.split("}")[-1] for node in svg_root.iter()}
        if "title" not in local_names or "desc" not in local_names:
            errors.append(f"{article['id']}: standalone SVG needs title and desc")
        if not svg_root.attrib.get("viewBox"):
            errors.append(f"{article['id']}: standalone SVG needs viewBox")
    except ET.ParseError as exc:
        errors.append(f"{article['id']}: invalid SVG XML: {exc}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "article-index.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    articles = manifest.get("articles", [])
    if len(articles) != 5:
        errors.append(f"article-index.json must describe exactly five refreshed articles, found {len(articles)}")
    for article in articles:
        errors.extend(check_article(article))

    courses = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))
    if len(courses.get("chapters", [])) != 28:
        errors.append("courses.json must retain all 28 practical course units")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for css_class, expected in (("chapter-card", 8), ("refreshed-card", 5), ("unit-card", 28)):
        actual = home.count('class="' + css_class + '"')
        if actual != expected:
            errors.append(f"index.html must contain {expected} {css_class} elements, found {actual}")
    if "master" in (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8"):
        errors.append("Pages deployment must target main, not master")
    if "convert.js" in (ROOT / ".github/workflows/deploy.yml").read_text(encoding="utf-8"):
        errors.append("Pages deployment must not depend on the missing convert.js")
    if not (ROOT / ".nojekyll").is_file():
        errors.append("missing .nojekyll for static GitHub Pages publishing")

    report = {
        "pass": not errors,
        "articles_checked": len(articles),
        "homepage": {"chapters": 8, "refreshed_articles": 5, "practical_units": 28},
        "errors": errors,
        "checks": [
            "Markdown/HTML title and H2 parity",
            "semantic article structure and local anchors",
            "inline SVG, caption and offline CSS/JS",
            "evidence ledger schema and source locators",
            "standalone SVG XML metadata",
            "homepage navigation counts",
            "28 practical course units retained",
            "static Pages workflow targets main",
        ],
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
