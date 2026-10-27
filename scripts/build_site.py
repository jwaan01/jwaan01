#!/usr/bin/env python3
"""Build the GitHub Pages site: site/index.html (page content) -> docs/.

site/index.html holds the head part (title, meta, fonts, style) above the
<!--/head--> marker and the body below it, so the same file can also be
previewed as an artifact. Run after generate_svgs.py.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
head, body = src.split("<!--/head-->", 1)
page = (
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="theme-color" content="#0b0b0d">\n'
    f"{head.strip()}\n</head>\n<body>\n{body.strip()}\n</body>\n</html>\n"
)
docs = ROOT / "docs"
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(page, encoding="utf-8")
shutil.copy(ROOT / "assets" / "night-run.svg", docs / "night-run.svg")
(docs / ".nojekyll").write_text("")
print("built docs/index.html")
