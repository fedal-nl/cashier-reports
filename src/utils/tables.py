from __future__ import annotations

from textwrap import dedent

import pandas as pd
import streamlit as st


def render_rtl_table(table: pd.DataFrame) -> None:
    """Render a scrollable RTL table with reliable column order and alignment."""
    table_html = table.to_html(index=False, border=0, escape=True)
    styles = dedent(
        """
            <style>
                .report-table-wrapper {
                    direction: rtl;
                    max-height: 600px;
                    overflow: auto;
                    border: 1px solid #e6e6e6;
                    border-radius: 0.5rem;
                }
                .report-table-wrapper table {
                    direction: rtl;
                    width: 100%;
                    border-collapse: collapse;
                }
                .report-table-wrapper th,
                .report-table-wrapper td {
                    padding: 0.65rem 0.75rem;
                    border-bottom: 1px solid #e6e6e6;
                    text-align: right !important;
                    white-space: nowrap;
                }
                .report-table-wrapper th {
                    position: sticky;
                    top: 0;
                    background: #f7f7f7;
                    z-index: 1;
                }
                .report-table-wrapper tbody tr:hover { background: #f8fffc; }
            </style>
        """
    ).strip()
    st.markdown(
        f'{styles}\n<div class="report-table-wrapper" dir="rtl">{table_html}</div>',
        unsafe_allow_html=True,
    )
