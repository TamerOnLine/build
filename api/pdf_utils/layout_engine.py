# api/pdf_utils/layout_engine.py
from __future__ import annotations

import argparse
import io
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

from reportlab.lib.pagesizes import A4, LETTER
from reportlab.pdfgen.canvas import Canvas

from .data_utils import build_ready_from_profile
from .layout import render_with_layout


PAGESIZES = {
    "A4": A4,
    "LETTER": LETTER,
}


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[ERR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERR] Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def generate_pdf(
    profile: Dict[str, Any],
    layout: Dict[str, Any],
    *,
    ui_lang: str | None = None,
    pagesize: str = "A4",
    compress: bool = True,
) -> bytes:
    """
    Build a PDF bytes object for the given profile & layout.

    Parameters
    ----------
    profile : dict
        Profile JSON (already parsed).
    layout : dict
        Layout JSON (already parsed).
    ui_lang : str | None
        UI language override; falls back to profile["ui_lang"] or 'en'.
    pagesize : {'A4','LETTER'}
        Output page size.
    compress : bool
        Enable ReportLab page compression.

    Returns
    -------
    bytes
        The generated PDF.
    """
    lang = ui_lang or profile.get("ui_lang") or "en"
    ps = PAGESIZES.get(pagesize.upper())
    if ps is None:
        valid = ", ".join(PAGESIZES.keys())
        print(f"[ERR] Unknown pagesize '{pagesize}'. Valid: {valid}", file=sys.stderr)
        sys.exit(2)

    data_map = build_ready_from_profile(profile)

    buf = io.BytesIO()
    canvas = Canvas(buf, pagesize=ps, pageCompression=int(bool(compress)))
    # If you want metadata, set it here:
    # canvas.setAuthor(profile.get("header", {}).get("name", ""))
    # canvas.setTitle("Resume")
    render_with_layout(canvas, layout, data_map, ui_lang=lang)
    canvas.showPage()
    canvas.save()

    return buf.getvalue()


def _atomic_write_bytes(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=str(target.parent), suffix=".pdf") as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(data)
    tmp_path.replace(target)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m api.pdf_utils.layout_engine",
        description="Generate a resume PDF from a profile and layout JSON.",
    )
    parser.add_argument("profile", type=Path, help="Path to profile.json")
    parser.add_argument("layout", type=Path, help="Path to layout.json")
    parser.add_argument("output", type=Path, help="Path to output.pdf")

    parser.add_argument(
        "--ui-lang",
        dest="ui_lang",
        default=None,
        help="Override UI language (defaults to profile.ui_lang or 'en').",
    )
    parser.add_argument(
        "--pagesize",
        dest="pagesize",
        default="A4",
        choices=sorted(PAGESIZES.keys(), key=str.lower),
        help="Page size (default: A4).",
    )
    parser.add_argument(
        "--no-compress",
        dest="compress",
        action="store_false",
        help="Disable PDF compression.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    print(f"[INFO] Loading profile: {args.profile}")
    profile = _read_json(args.profile)

    print(f"[INFO] Loading layout : {args.layout}")
    layout = _read_json(args.layout)

    print(f"[INFO] Generating PDF  (pagesize={args.pagesize}, compress={bool(args.compress)})")
    pdf_bytes = generate_pdf(
        profile=profile,
        layout=layout,
        ui_lang=args.ui_lang,
        pagesize=args.pagesize,
        compress=args.compress,
    )

    print(f"[INFO] Writing PDF     : {args.output}")
    _atomic_write_bytes(args.output, pdf_bytes)

    size = args.output.stat().st_size if args.output.exists() else 0
    print(f"[OK] PDF generated: {args.output} ({size} bytes)")


if __name__ == "__main__":
    main()
