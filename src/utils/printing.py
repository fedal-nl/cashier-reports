from __future__ import annotations

import json
from html import escape

import pandas as pd
import streamlit.components.v1 as components


def render_print_button(
    table: pd.DataFrame,
    *,
    title: str,
    landscape: bool = False,
) -> None:
    """Render a button that prints only the supplied table on an A4 page."""
    orientation = "landscape" if landscape else "portrait"
    safe_title = escape(title)
    report_html = f"""
        <!doctype html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="utf-8">
            <title>{safe_title}</title>
            <style>
                @page {{ size: A4 {orientation}; margin: 12mm; }}
                body {{ font-family: Arial, sans-serif; direction: rtl; color: #111; }}
                h1 {{ font-size: 20px; margin: 0 0 16px; text-align: right; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
                th, td {{ border: 1px solid #777; padding: 6px; text-align: right; }}
                th {{ background: #f0f0f0; }}
                tr {{ break-inside: avoid; }}
            </style>
        </head>
        <body>
            <h1>{safe_title}</h1>
            {table.to_html(index=False, border=0, escape=True)}
        </body>
        </html>
    """
    encoded_html = json.dumps(report_html, ensure_ascii=True).replace("<", "\\u003c")
    components.html(
        f"""
        <button type="button" onclick="printResult()" style="
            width: 100%; padding: 0.65rem 1rem; border: 1px solid #087f5b;
            border-radius: 0.5rem; background: #0ca678; color: white;
            cursor: pointer; font-size: 1rem; font-weight: 700; direction: rtl;
            box-shadow: 0 2px 6px rgba(12, 166, 120, 0.28);">
            🖨️ طباعة النتائج
        </button>
        <style>
            button:hover {{ background: #087f5b !important; }}
            button:focus {{ outline: 3px solid rgba(12, 166, 120, 0.3); }}
        </style>
        <script>
            function printResult() {{
                const printWindow = window.open('', '_blank');
                printWindow.document.open();
                printWindow.document.write({encoded_html});
                printWindow.document.close();
                printWindow.focus();
                setTimeout(() => printWindow.print(), 250);
            }}
        </script>
        """,
        height=48,
    )
