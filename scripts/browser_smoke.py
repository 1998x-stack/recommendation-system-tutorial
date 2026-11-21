#!/usr/bin/env python3
"""Chromium browser smoke checks for the homepage and five refreshed lessons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SIZES = [
    ("desktop", 1440, 900),
    ("tablet", 768, 1024),
    ("mobile", 390, 844),
    ("narrow-mobile", 360, 800),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "article-index.json").read_text(encoding="utf-8"))
    pages = [{"id": "home", "html": "index.html", "home": True}]
    pages.extend({**article, "home": False} for article in manifest["articles"])
    report = {"pass": True, "pages": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for spec in pages:
            file_path = ROOT / spec["html"]
            key = spec["id"].replace(".", "_")
            entry = {"pass": True, "viewports": {}, "interaction": "not-applicable"}
            for label, width, height in SIZES:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors: list[str] = []
                blocked_requests: list[str] = []
                page.on("pageerror", lambda error, target=errors: target.append(str(error)))
                page.on("console", lambda msg, target=errors: target.append(msg.text) if msg.type == "error" else None)
                page.route("https://**", lambda route, target=blocked_requests: (target.append(route.request.url), route.abort()))
                page.route("http://**", lambda route, target=blocked_requests: (target.append(route.request.url), route.abort()))
                page.goto(file_path.as_uri(), wait_until="load")
                page.screenshot(path=str(args.output / f"{key}-{label}.png"), full_page=True)
                metrics = page.evaluate("""() => {
                  const svgs = [...document.querySelectorAll('svg')];
                  const math = [...document.querySelectorAll('math')];
                  const ns = 'http://www.w3.org/1998/Math/MathML';
                  return {
                    viewport: innerWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                    h1Count: document.querySelectorAll('h1').length,
                    figureCount: document.querySelectorAll('figure').length,
                    svgCount: svgs.length,
                    zeroSizeSvg: svgs.filter(s => {
                      const r = s.getBoundingClientRect();
                      return r.width < 1 || r.height < 1;
                    }).length,
                    mathWrongNamespace: math.filter(m => m.namespaceURI !== ns).length,
                    mathInsideSvg: document.querySelectorAll('svg math').length,
                    buttonCount: document.querySelectorAll('button').length,
                    chapterCardCount: document.querySelectorAll('.chapter-card').length,
                    refreshedCardCount: document.querySelectorAll('.refreshed-card').length,
                    unitCardCount: document.querySelectorAll('.unit-card').length
                  };
                }""")
                common_ok = metrics["scrollWidth"] <= metrics["viewport"] + 1 and metrics["h1Count"] == 1 and not errors and not blocked_requests
                if spec["home"]:
                    okay = common_ok and metrics["chapterCardCount"] == 8 and metrics["refreshedCardCount"] == 5 and metrics["unitCardCount"] == 28
                else:
                    okay = (
                        common_ok and metrics["figureCount"] >= 1 and metrics["svgCount"] >= 1
                        and metrics["zeroSizeSvg"] == 0 and metrics["mathWrongNamespace"] == 0
                        and metrics["mathInsideSvg"] == 0 and metrics["buttonCount"] == 1
                    )
                entry["viewports"][label] = {
                    "pass": okay, **metrics, "errors": errors,
                    "blocked_external_requests": blocked_requests,
                }
                if not okay:
                    entry["pass"] = False
                if label == "desktop" and not spec["home"]:
                    button = page.locator("#demo-toggle")
                    before = page.locator("#demo-output").inner_text()
                    button.click()
                    after = page.locator("#demo-output").inner_text()
                    pressed = button.get_attribute("aria-pressed")
                    interaction_ok = before != after and pressed == "true"
                    entry["interaction"] = {
                        "status": "verified" if interaction_ok else "failed",
                        "before": before, "after": after,
                    }
                    if not interaction_ok:
                        entry["pass"] = False
                if label == "desktop":
                    page.emulate_media(media="print")
                    page.screenshot(path=str(args.output / f"{key}-print.png"), full_page=True)
                page.close()
            report["pages"][spec["id"]] = entry
            if not entry["pass"]:
                report["pass"] = False
        browser.close()

    output = json.dumps(report, ensure_ascii=False, indent=2)
    (args.output / "report.json").write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
