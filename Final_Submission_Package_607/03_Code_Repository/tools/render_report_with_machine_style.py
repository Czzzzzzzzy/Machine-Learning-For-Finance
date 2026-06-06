"""Render the final report using the Machine-Learning report visual style."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_HTML = ROOT / "Machine-Learning-For-Finance-main" / "report" / "final_report.html"
REPORT_MD = ROOT / "report" / "final_report.md"
REPORT_HTML = ROOT / "report" / "final_report.html"
REPORT_PDF = ROOT / "report" / "final_report.pdf"
REPORT_TEX = ROOT / "report" / "final_report.tex"


FALLBACK_CSS = """
        :root {
            --imperial-blue: #002147;
            --accent-teal: #006e6d;
            --border-color: #d9dee6;
            --bg-light: #f7f9fb;
            --text-primary: #18212f;
            --text-secondary: #5c6675;
        }
        body {
            margin: 0;
            background: #ffffff;
            color: var(--text-primary);
            font-family: Georgia, "Times New Roman", serif;
            line-height: 1.45;
        }
        .container {
            max-width: 980px;
            margin: 0 auto;
            padding: 28px 34px;
        }
        .cover {
            min-height: 92vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            page-break-after: always;
        }
        .institution, .department, .meta, .subtitle {
            font-family: "Helvetica Neue", Arial, sans-serif;
            color: var(--text-secondary);
        }
        .cover h1 {
            color: var(--imperial-blue);
            font-family: "Helvetica Neue", Arial, sans-serif;
            font-size: 2.4rem;
            line-height: 1.12;
        }
        .rule {
            width: 100%;
            border: 0;
            border-top: 2px solid var(--imperial-blue);
            margin: 22px 0;
        }
        h1, h2, h3 {
            color: var(--imperial-blue);
            font-family: "Helvetica Neue", Arial, sans-serif;
        }
        h2 {
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 6px;
            margin-top: 1.4em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.86rem;
            margin: 1em 0;
        }
        th, td {
            border-bottom: 1px solid var(--border-color);
            padding: 6px 8px;
            vertical-align: top;
        }
        th {
            background: var(--bg-light);
            font-family: "Helvetica Neue", Arial, sans-serif;
        }
        img {
            max-width: 100%;
        }
        figcaption {
            color: var(--text-secondary);
            font-family: "Helvetica Neue", Arial, sans-serif;
            font-size: 0.82rem;
        }
        .callout {
            border-left: 4px solid var(--accent-teal);
            background: var(--bg-light);
            padding: 10px 14px;
            margin: 1em 0;
        }
        .toc {
            page-break-after: always;
        }
"""


def extract_reference_css() -> str:
    if REFERENCE_HTML.exists():
        text = REFERENCE_HTML.read_text(encoding="utf-8")
        match = re.search(r"<style>(.*?)</style>", text, flags=re.S)
        css = match.group(1) if match else FALLBACK_CSS
    else:
        css = FALLBACK_CSS
    css += """

        /* ========== CURRENT REPORT EXTENSIONS ========== */
        @page { size: A4; margin: 13mm 15mm; }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin: 1.2em 0 1.5em 0;
            page-break-inside: avoid;
        }
        .kpi {
            border: 1px solid var(--border-color);
            background: var(--bg-light);
            padding: 12px 14px;
            min-height: 76px;
        }
        .kpi .label {
            font-family: "Helvetica Neue", "Arial", sans-serif;
            font-size: 0.78rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }
        .kpi .value {
            font-family: "Helvetica Neue", "Arial", sans-serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--imperial-blue);
            margin-top: 4px;
        }
        .report-note {
            font-family: "Helvetica Neue", "Arial", sans-serif;
            font-size: 0.86rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            padding-top: 10px;
            margin-top: 1.2em;
        }
        pre {
            background: #f0f2f5;
            border: 1px solid #d9dee6;
            border-left: 4px solid var(--accent-teal);
            padding: 10px 12px;
            overflow-wrap: anywhere;
            white-space: pre-wrap;
            font-size: 0.86rem;
        }
        blockquote {
            background: var(--bg-light);
            border-left: 4px solid var(--accent-teal);
            margin: 1em 0;
            padding: 10px 16px;
        }
        .container > h1:first-of-type { display: none; }
        .toc ul ul { margin-top: 0; }
        .toc .toc-l2 { margin-bottom: 0; }
        table { break-inside: avoid; }
        figure { break-inside: avoid; }
        figure img { max-height: 620px; object-fit: contain; }
        @media print {
            .kpi-grid { grid-template-columns: repeat(4, 1fr); }
            h2 { page-break-before: always; }
            .toc + h2, .container > h2:first-of-type { page-break-before: avoid; }
        }
"""
    return css


def pandoc_html_fragment() -> str:
    cmd = [
        "/opt/anaconda3/bin/pandoc",
        str(REPORT_MD),
        "--from",
        "markdown",
        "--to",
        "html",
        "--resource-path=.:report:outputs/report_ready",
    ]
    return subprocess.check_output(cmd, cwd=ROOT, text=True)


def format_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def build_cover_and_kpis() -> tuple[str, str]:
    perf = pd.read_csv(ROOT / "outputs" / "performance_summary.csv")
    row = perf.loc[perf["AUM"].eq(250_000_000.0)].iloc[0]
    cover = f"""
<div class="cover">
    <div class="institution">Imperial College London</div>
    <div class="department">Machine Learning and Finance</div>
    <hr class="rule">
    <h1>Close-to-Open (C2O) Overnight Equity Strategy</h1>
    <div class="subtitle">Final Submission Report &mdash; Corrected Research Version</div>
    <hr class="rule">
    <div class="meta">
        <strong>Strategy universe:</strong> US Large-Cap Equities, 2010&ndash;2024<br>
        <strong>Final strategy:</strong> volatility-scaled target with expanding-window weight estimation<br>
        <strong>AUM scenarios:</strong> $50M &middot; $250M &middot; $1B<br>
        <strong>Main headline AUM:</strong> $250M
    </div>
</div>
"""
    kpis = f"""
<div class="kpi-grid">
    <div class="kpi"><div class="label">250M Net Return</div><div class="value">{format_pct(float(row['net_annual_return']))}</div></div>
    <div class="kpi"><div class="label">250M Net Vol</div><div class="value">{format_pct(float(row['net_vol']))}</div></div>
    <div class="kpi"><div class="label">250M Net Sharpe</div><div class="value">{float(row['net_sharpe']):.3f}</div></div>
    <div class="kpi"><div class="label">Max Drawdown</div><div class="value">{format_pct(float(row['max_drawdown']))}</div></div>
</div>
<div class="callout">
    <strong>Decision:</strong> final strategy is <code>phase2_g5_05_expanding</code>.
    The old 0.811 Sharpe strategy is retained only as previous-champion evidence.
</div>
"""
    return cover, kpis


def build_toc(soup: BeautifulSoup) -> str:
    headings = soup.find_all(["h2", "h3"])
    items: list[str] = []
    open_nested = False
    for h in headings:
        text = h.get_text(" ", strip=True)
        hid = h.get("id")
        if not hid:
            continue
        if h.name == "h2":
            if open_nested:
                items.append("</ul></li>")
                open_nested = False
            items.append(f'<li><a href="#{hid}">{text}</a>')
            open_nested = True
            items.append("<ul>")
        else:
            if open_nested:
                items.append(f'<li class="toc-l2"><a href="#{hid}">{text}</a></li>')
    if open_nested:
        items.append("</ul></li>")
    return f"""
<div class="toc">
    <h2>Table of Contents</h2>
    <ul>
        {''.join(items)}
    </ul>
</div>
"""


def massage_fragment(fragment: str) -> tuple[str, str]:
    soup = BeautifulSoup(fragment, "html.parser")
    first_h2 = soup.find("h2", id="executive-summary")
    _, kpis = build_cover_and_kpis()
    if first_h2:
        first_h2.insert_after(BeautifulSoup(kpis, "html.parser"))

    caption_map = {
        "return_decomposition_q1.png": "Equal-weight eligible-universe overnight/intraday/close-to-close decomposition, 2010-2024; no AUM, no strategy costs, annual large-cap universe.",
        "short_interest_representative_series.png": "Representative HLT short-interest proxy series, 2015-2024; provided point-in-time proxies plus one-trading-day decision lag; no AUM or portfolio cost assumption.",
        "corrected_report_capacity.png": "Capacity by AUM for the final top/bottom 3% equal-weight strategy; 50M/250M/1B, fixed 5% ADV20 cap, full commission/slippage/borrow schedule.",
        "model_feature_weights_2024.png": "Largest 2024 final linear-score feature weights; transparent expanding-window model, unchanged feature set, no LightGBM portfolio promotion.",
        "model_ic_comparison.png": "Final linear score versus LightGBM diagnostic IC in validation and internal holdout; same data panel and cutoff; LightGBM is not the promoted costed strategy.",
        "rolling_ic.png": "63-day rolling IC for the final linear score; Spearman correlation between alpha score and subsequent overnight return, 2010-2024.",
        "model_yearly_ic.png": "Final linear-score mean IC by calendar year, 2010-2024; negative years highlighted.",
        "corrected_report_ablation.png": "Feature-group ablation at 250M for the final top/bottom 3% equal-weight strategy; fixed 5% ADV20 cap and full cost schedule.",
        "corrected_report_aum_cumulative_returns.png": "Final net cumulative returns by AUM; 50M/250M/1B, final top/bottom 3% equal-weight strategy, fixed 5% ADV20 cap and full commission/slippage/borrow schedule.",
    }

    for img in soup.find_all("img"):
        src = img.get("src", "")
        filename = Path(src).name
        if src.startswith("outputs/"):
            img["src"] = "../" + src
        img["loading"] = "eager"
        if filename in caption_map:
            figure = img.find_parent("figure")
            if figure:
                caption = figure.find("figcaption")
                if caption:
                    caption.string = caption_map[filename]

    for table in soup.find_all("table"):
        table["class"] = table.get("class", []) + ["no-break"]

    toc = build_toc(soup)
    return str(soup), toc


def write_html() -> None:
    css = extract_reference_css()
    fragment, toc = massage_fragment(pandoc_html_fragment())
    cover, _ = build_cover_and_kpis()
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Close-to-Open Overnight Equity Strategy &mdash; Final Report</title>
    <style>{css}</style>
</head>
<body>
<div class="container">
{cover}
{toc}
{fragment}
<div class="report-note">
    Source files: report/final_report.md, outputs/performance_summary.csv, and outputs/report_ready audit evidence.
    Generated with the visual style of Machine-Learning-For-Finance-main/report/final_report.html.
</div>
</div>
</body>
</html>
"""
    REPORT_HTML.write_text(html, encoding="utf-8")


def render_pdf() -> None:
    chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if chrome.exists():
        cmd = [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--no-pdf-header-footer",
            f"--print-to-pdf={REPORT_PDF}",
            REPORT_HTML.resolve().as_uri(),
        ]
        subprocess.run(cmd, cwd=ROOT, check=True)
        return

    cmd = [
        "/opt/anaconda3/bin/pandoc",
        str(REPORT_MD),
        "-o",
        str(REPORT_PDF),
        "--resource-path=.:report:outputs/report_ready",
        "--pdf-engine=xelatex",
        "-V",
        "geometry:margin=0.65in",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


def render_tex_snapshot() -> None:
    cmd = [
        "/opt/anaconda3/bin/pandoc",
        str(REPORT_MD),
        "-o",
        str(REPORT_TEX),
        "--resource-path=.:report:outputs/report_ready",
        "--standalone",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    write_html()
    render_pdf()
    render_tex_snapshot()
    print(f"Wrote {REPORT_HTML}")
    print(f"Wrote {REPORT_PDF}")


if __name__ == "__main__":
    main()
