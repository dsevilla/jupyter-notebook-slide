"""Regenerate ``docs/preview.png``, the image used in the README.

Writes the slides to an HTML file and screenshots it with headless Firefox::

    uv run python docs/make_preview.py
"""

from __future__ import annotations

import pathlib
import subprocess
import tempfile

import notebook_slide as ns

HERE = pathlib.Path(__file__).parent
SLIDES = [
    dict(body="# Part one — Getting your bearings", type="title", min_height="200px"),
    dict(
        body="""# What this session covers

- Work with **text, code and results** inside a notebook.
- Follow the `XML → CSV → Arrow → Parquet` path.
- Understand what a **schema** buys you.

> Key idea: moving less data is usually the first big optimisation.""",
        type="preview",
        min_height="0px",
    ),
    dict(
        body="""# Where does the time actually go?

1. Reading bytes off disk.
2. Parsing them into values.
3. The computation you actually care about.""",
        type="question",
        min_height="0px",
    ),
    dict(
        body="""# From a file to a reusable data source

- Arrow represents columns and types efficiently in memory.
- Parquet keeps the schema and enables **projection** and filters.""",
        type="summary",
        min_height="0px",
        theme=ns.get_theme("midnight"),
    ),
]


def main() -> None:
    html = "<body style='background:#f0f0f0;margin:0;padding:16px'>" + "\n".join(
        ns.slide_html(**slide) for slide in SLIDES
    )
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp) / "preview.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                "firefox",
                "--headless",
                "--profile",
                tmp,
                "--window-size=1010,1560",
                "--screenshot",
                str(HERE / "preview.png"),
                page.as_uri(),
            ],
            check=True,
        )
    print(f"wrote {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
