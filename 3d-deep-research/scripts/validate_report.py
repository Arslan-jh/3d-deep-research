#!/usr/bin/env python3
"""Validate a 3d-deep-research Markdown report and optionally its PDF."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CHINESE_NUMERALS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6}
PLACEHOLDER_PATTERNS = [
    r"\[研究对象\]",
    r"\[YYYY(?:-MM-DD)?\]",
    r"\[一句话(?:问题|判断)?\]",
    r"\[来源\]",
    r"\[待补\]",
    r"\{\{[^}]+\}\}",
    r"\bTODO\b",
    r"\bTBD\b",
]


def _configure_utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def _read_pdf(pdf_path: Path) -> tuple[int, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except ModuleNotFoundError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install pypdf or PyPDF2 to validate PDF content.") from exc

    reader = PdfReader(str(pdf_path))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    return len(reader.pages), text


def validate_markdown(md_text: str) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []

    h1 = re.findall(r"^#\s+.+$", md_text, flags=re.MULTILINE)
    if len(h1) != 1:
        errors.append(f"Expected exactly one H1 title, found {len(h1)}.")

    main_sections = re.findall(
        r"^##\s+([一二三四五六])、(.+)$",
        md_text,
        flags=re.MULTILINE,
    )
    sequence = [CHINESE_NUMERALS[item[0]] for item in main_sections]
    if sequence != [1, 2, 3, 4, 5, 6]:
        errors.append(
            "Main sections must appear exactly once in order: 一、 through 六、. "
            f"Found: {sequence or 'none'}."
        )

    current_main: int | None = None
    in_appendix = False
    for line_no, line in enumerate(md_text.splitlines(), start=1):
        main_match = re.match(r"^##\s+([一二三四五六])、", line)
        if main_match:
            current_main = CHINESE_NUMERALS[main_match.group(1)]
            in_appendix = False
            continue
        if re.match(r"^##\s+附录", line):
            current_main = None
            in_appendix = True
            continue
        sub_match = re.match(r"^###\s+(\d+)\.(\d+)\b", line)
        if sub_match:
            prefix = int(sub_match.group(1))
            if current_main is None or prefix != current_main:
                errors.append(
                    f"Line {line_no}: subsection {sub_match.group(0)!r} "
                    "does not match its main section."
                )
        appendix_match = re.match(r"^###\s+A\d+\b", line)
        if appendix_match and not in_appendix:
            errors.append(f"Line {line_no}: appendix subsection appears outside appendix.")

    placeholders: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        placeholders.extend(re.findall(pattern, md_text, flags=re.IGNORECASE))
    if placeholders:
        errors.append(
            "Unresolved template placeholders: "
            + ", ".join(sorted(set(placeholders))[:10])
        )

    if re.search(r"```\s*mermaid\b", md_text, flags=re.IGNORECASE):
        errors.append("Unrendered Mermaid source found; render it to SVG first.")

    source_definitions = set(
        re.findall(r"^\|\s*(S\d{2,})\s*\|", md_text, flags=re.MULTILINE)
    )
    source_references = set(re.findall(r"\[(S\d{2,})\]", md_text))
    if not source_references:
        errors.append("No [Sxx] source references found in the report.")
    unresolved_sources = source_references - source_definitions
    if unresolved_sources:
        errors.append(
            "Source references missing from the source ledger: "
            + ", ".join(sorted(unresolved_sources))
        )
    unused_sources = source_definitions - source_references
    if unused_sources:
        warnings.append(
            "Source ledger entries are not cited in the report: "
            + ", ".join(sorted(unused_sources))
        )

    if "Claim ID" not in md_text or not re.search(
        r"^\|\s*C\d{2,}\s*\|",
        md_text,
        flags=re.MULTILINE,
    ):
        errors.append("Claim evidence matrix with Cxx rows was not found.")

    figures = re.findall(
        r"<figure\b.*?</figure>",
        md_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for index, figure in enumerate(figures, start=1):
        if "<figcaption" not in figure.lower():
            errors.append(f"Figure {index} has no figcaption.")
        svg_match = re.search(
            r"<svg\b([^>]*)>",
            figure,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if svg_match:
            attributes = svg_match.group(1)
            for required in ("viewBox", "role=", "aria-label="):
                if required.lower() not in attributes.lower():
                    errors.append(f"Figure {index} SVG is missing {required}.")

    stats = {
        "main_sections": len(main_sections),
        "source_definitions": len(source_definitions),
        "source_references": len(source_references),
        "figures": len(figures),
        "characters": len(md_text),
    }
    return errors, warnings, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a 3d-deep-research report.")
    parser.add_argument("markdown", help="Markdown report path")
    parser.add_argument("--pdf", help="Optional rendered PDF path")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result")
    return parser.parse_args()


def main() -> None:
    _configure_utf8_console()
    args = parse_args()
    markdown_path = Path(args.markdown).expanduser().resolve()
    if not markdown_path.is_file():
        raise SystemExit(f"Markdown report not found: {markdown_path}")

    md_text = markdown_path.read_text(encoding="utf-8")
    errors, warnings, stats = validate_markdown(md_text)

    if args.pdf:
        pdf_path = Path(args.pdf).expanduser().resolve()
        if not pdf_path.is_file() or pdf_path.stat().st_size < 1024:
            errors.append(f"PDF is missing or too small: {pdf_path}")
        else:
            try:
                pages, pdf_text = _read_pdf(pdf_path)
                stats["pdf_pages"] = pages
                stats["pdf_text_characters"] = len(pdf_text)
                if pages < 1:
                    errors.append("PDF has no pages.")
                if len(pdf_text.strip()) < 100:
                    warnings.append("PDF text extraction returned very little text.")
                if "\ufffd" in pdf_text:
                    warnings.append("PDF text contains Unicode replacement characters.")
            except Exception as exc:
                errors.append(f"PDF validation failed: {exc}")

    passed = not errors and not (args.strict and warnings)
    result = {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print(f"[ERROR] {error}")
        for warning in warnings:
            print(f"[WARN] {warning}")
        print("[OK] Report validation passed." if passed else "[FAIL] Report validation failed.")
        print("[INFO] " + json.dumps(stats, ensure_ascii=False))

    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
