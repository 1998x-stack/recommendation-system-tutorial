# Contributing to the recommendation systems tutorial

## Content contract

Every lesson is a self-contained explanation. A reader who opens a single HTML page must be able to understand the problem, terms, assumptions, mechanism, equations, example, limitations and references without first reading another lesson. Do not write dependent phrases such as “the lecture explains” or “as discussed earlier” unless the missing context is restated on the page.

## Canonical files

- Markdown is the editorial source.
- HTML is the independently readable web edition; it must preserve the same H1 and H2 sequence.
- Python examples live under **examples/** and must be deterministic, runnable and labelled as toy examples unless they reproduce a paper faithfully.
- **evidence/** contains a claim ledger with source URL, precise locator and status.
- **assets/diagrams/** contains standalone SVG copies of original diagrams. Each SVG needs a title, description and viewBox.

## Evidence rules

1. Prefer the primary paper, official research page, standard, or vendor documentation.
2. Attach a source to each historical metric, architecture claim or implementation detail.
3. Distinguish verified facts, derived calculations, illustrative examples and unverified claims.
4. Never infer causal lift from a platform-wide GMV or engagement total.
5. Record the paper version and section/table/figure locator when applicable.

## HTML and accessibility

- One H1; ordered H2/H3; semantic main/article/nav/section/figure elements.
- Inline SVG with title, description and caption; color is never the only carrier of meaning.
- Keyboard-visible focus, labelled native controls, reduced-motion and print styles.
- No CDN, external fonts or remote JavaScript for article rendering.
- Test 1440, 768, 390 and 360 pixel widths. The document must not horizontally overflow; wide equations and code may scroll inside their own labelled regions.

## Release checks

Run from the repository root:

~~~bash
python -m unittest discover -s tests -v
python scripts/validate_content.py
pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/browser_smoke.py --output reports/browser-qa
~~~

A skipped browser test is “not verified”, not “passed”. The GitHub Actions quality workflow is the release gate.
