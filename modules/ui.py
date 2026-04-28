"""
modules/ui.py — Design system do Chess Scout (Dossiê)

Expõe:
  DOSSIE       — dict com todos os tokens de cor
  build_css(C) — retorna o bloco <style>…</style> completo
  Helpers HTML — _donut_svg, _radar_svg, _color_bar, _section_lbl
  Helpers render (dependem de streamlit) — render_header, render_footer,
                render_stepper, _prog_html
"""

import math
import streamlit as st

# ── Paleta dossiê ─────────────────────────────────────────────────────────────
DOSSIE: dict = {
    "bg":        "#f3ede0",
    "paper":     "#faf6ec",
    "paperEdge": "#e7dfcc",
    "ink":       "#1c1a14",
    "inkMid":    "#3a3528",
    "inkMuted":  "#7a6f55",
    "inkFaint":  "#a89d80",
    "border":    "#d5cab0",
    "borderMid": "#c0b390",
    "red":       "#a8281e",
    "redBg":     "#f3dcd6",
    "redBdr":    "#d4a09a",
    "green":     "#3a6b2a",
    "greenBg":   "#dff0d8",
    "greenBdr":  "#a8d5a0",
    "amber":     "#a8702a",
    "amberBg":   "#f5e8d0",
}


# ── CSS ───────────────────────────────────────────────────────────────────────

def build_css(C: dict) -> str:
    """Retorna o bloco <style>…</style> completo parametrizado por C (DOSSIE)."""
    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset Streamlit chrome ───────────────────────────────────────────────── */
#MainMenu, footer, header {{ display:none !important; }}
[data-testid="stSidebar"]       {{ display:none !important; }}
[data-testid="stDecoration"]    {{ display:none !important; }}
[data-testid="stStatusWidget"]  {{ display:none !important; }}
.stDeployButton                 {{ display:none !important; }}
[data-testid="stToolbar"]       {{ display:none !important; }}

/* ── Global ──────────────────────────────────────────────────────────────── */
body, .stApp {{
    background: {C["bg"]} !important;
    font-family: 'Inter', system-ui, sans-serif;
    color: {C["ink"]};
    margin: 0; padding: 0;
    min-height: 100dvh;
}}
.block-container {{
    padding: clamp(72px,9vw,88px) clamp(12px,4vw,32px) 56px !important;
    max-width: 100% !important;
}}
section[data-testid="stMain"] > div {{ padding: 0 !important; }}

/* ── Fixed header ────────────────────────────────────────────────────────── */
.ds-header {{
    position: fixed; top:0; left:0; right:0;
    height: 52px;
    background: {C["bg"]};
    border-bottom: 1px solid {C["border"]};
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 clamp(16px,4vw,28px);
    z-index: 9999;
}}
.ds-header-left {{ display: flex; align-items: center; gap: 10px; }}
.ds-logo {{ font-size: 20px; color: {C["ink"]}; }}
.ds-title {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(13px,2.5vw,16px); font-weight: 700;
    letter-spacing: 0.25em; color: {C["ink"]}; text-transform: uppercase;
}}
.ds-lang-btn {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: {C["inkMuted"]};
    background: transparent;
    border: 1px solid {C["border"]};
    border-radius: 4px; padding: 5px 10px;
    text-decoration: none; transition: border-color 0.2s;
}}
.ds-lang-btn:hover {{ border-color:{C["borderMid"]}; color:{C["inkMid"]}; }}

/* ── Page scaffold ───────────────────────────────────────────────────────── */
.ds-wizard-wrap  {{ width:100%; max-width:520px; margin:0 auto; padding: 0 4px; }}
.ds-results-wrap {{ width:100%; max-width:880px; margin:0 auto; }}

/* ── Footer ──────────────────────────────────────────────────────────────── */
.ds-footer {{
    border-top: 1px solid {C["border"]};
    padding: 14px 22px; text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: {C["inkFaint"]}; letter-spacing: 0.18em;
    background: {C["bg"]};
}}

/* ── Stepper ─────────────────────────────────────────────────────────────── */
.ds-step-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: {C["inkFaint"]};
    letter-spacing: 0.22em; text-transform: uppercase;
    text-align: center; margin-bottom: 16px;
}}
.ds-stepper {{
    display: flex; align-items: center;
    justify-content: center; margin-bottom: 28px; gap: 0;
}}
.ds-step-node {{
    display: flex; flex-direction: column;
    align-items: center; gap: 5px;
}}
.ds-step-circle {{
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px; font-weight: 500;
    border: 1.5px solid;
}}
.ds-circle-done   {{ background:{C["ink"]};    color:{C["paper"]};    border-color:{C["ink"]}; }}
.ds-circle-active {{ background:transparent;   color:{C["red"]};      border-color:{C["red"]}; }}
.ds-circle-future {{ background:transparent;   color:{C["inkFaint"]}; border-color:{C["border"]}; }}
.ds-step-name {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px; letter-spacing: 0.08em; color: {C["inkFaint"]};
}}
.ds-name-active  {{ color:{C["red"]}; }}
.ds-connector {{
    width: 28px; height: 1px; margin-bottom: 20px; flex-shrink: 0;
}}
.ds-conn-done    {{ background:{C["ink"]}; }}
.ds-conn-pending {{ background:{C["border"]}; }}

/* ── Paper card ──────────────────────────────────────────────────────────── */
.ds-paper {{
    background: {C["paper"]};
    border: 1px solid {C["paperEdge"]};
    border-radius: 4px;
    padding: clamp(24px,5vw,44px) clamp(20px,5vw,44px);
    text-align: center;
    margin-bottom: 16px;
}}
.ds-paper-left {{ text-align: left; }}
.ds-wiz-icon  {{ font-size: 34px; margin-bottom: 10px; }}
.ds-wiz-title {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(20px,5vw,28px); font-weight: 700;
    color: {C["ink"]}; margin-bottom: 6px; line-height: 1.2;
}}
.ds-wiz-sub {{
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 13px; color: {C["inkMuted"]}; margin-bottom: 26px;
}}

/* ── Tile zone ───────────────────────────────────────────────────────────── */
.cs-tile-zone {{ display:none; }}
.element-container:has(.cs-tile-zone) + .element-container [data-testid="stButton"] > button {{
    height: 108px !important;
    border-radius: 4px !important;
    border: 1.5px solid {C["border"]} !important;
    background: {C["paper"]} !important;
    color: {C["ink"]} !important;
    font-family: 'Inter', system-ui !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    padding: 16px 12px !important;
    transition: border-color 0.15s, background 0.15s !important;
    white-space: pre-wrap !important;
    line-height: 1.4 !important;
}}
.element-container:has(.cs-tile-zone) + .element-container [data-testid="stButton"] > button:hover {{
    border-color: {C["borderMid"]} !important;
    background: {C["bg"]} !important;
}}
.element-container:has(.cs-tile-zone) + .element-container [data-testid="stButton"] > button[kind="primary"] {{
    background: {C["redBg"]} !important;
    color: {C["red"]} !important;
    border-color: {C["red"]} !important;
    border-width: 1.5px !important;
}}
.cs-tile-row-gap {{ height: 12px; }}
.cs-tile-icon    {{ font-size: 30px; }}
.cs-tile-iconsm  {{ font-size: 24px; }}
.cs-tile-lbl {{
    font-family: 'Inter', system-ui; font-size: 13px; font-weight: 600;
    color: {C["ink"]};
}}
.cs-tile-sub {{
    font-family: 'Inter', system-ui; font-size: 11px;
    color: {C["inkMuted"]}; white-space: pre-line; line-height: 1.4;
}}

/* ── Streamlit buttons ───────────────────────────────────────────────────── */
[data-testid="stButton"] > button {{
    border-radius: 4px !important;
    font-family: 'Inter', system-ui !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.15s !important;
    min-height: 44px !important;
}}
[data-testid="stButton"] > button[kind="primary"] {{
    height: 44px !important; padding: 0 24px !important; font-size: 14px !important;
    background: {C["ink"]} !important; color: {C["paper"]} !important;
    border: none !important;
}}
[data-testid="stButton"] > button[kind="primary"]:hover {{ opacity: 0.88 !important; }}
[data-testid="stButton"] > button[kind="secondary"] {{
    height: 44px !important; padding: 0 22px !important; font-size: 13px !important;
    background: transparent !important; color: {C["inkMuted"]} !important;
    border: 1px solid {C["border"]} !important;
}}
[data-testid="stDownloadButton"] > button {{
    height: 36px !important; padding: 0 16px !important; font-size: 12px !important;
    background: {C["ink"]} !important; color: {C["paper"]} !important;
    border: none !important; border-radius: 4px !important;
    font-family: 'Inter', system-ui !important;
    font-weight: 500 !important;
}}
.cs-tile-backer {{ height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }}

/* ── Text input ──────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] > div > div {{ border: none !important; background: transparent !important; }}
[data-testid="stTextInput"] input {{
    background: {C["paper"]} !important;
    border: 1.5px solid {C["border"]} !important;
    border-radius: 4px !important;
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: clamp(18px,4vw,22px) !important;
    color: {C["ink"]} !important;
    -webkit-text-fill-color: {C["ink"]} !important;
    caret-color: {C["red"]} !important;
    text-align: center !important;
    padding: 14px 16px !important;
    box-shadow: none !important; outline: none !important;
}}
[data-testid="stTextInput"] input::placeholder {{ color: {C["inkFaint"]} !important; opacity:1; }}
[data-testid="stTextInput"] input:focus {{
    border-color: {C["red"]} !important;
    box-shadow: 0 0 0 3px {C["redBg"]} !important;
}}

/* ── Progress (loading) ──────────────────────────────────────────────────── */
.ds-prog-wrap {{
    background: {C["paper"]};
    border: 1px solid {C["paperEdge"]};
    border-radius: 4px;
    padding: clamp(24px,5vw,40px) clamp(20px,5vw,40px);
}}
.ds-prog-title {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(20px,5vw,26px); color: {C["ink"]}; margin-bottom: 6px;
}}
.ds-prog-sub {{
    font-family: 'Inter', system-ui; font-size: 12px;
    color: {C["inkMuted"]}; margin-bottom: 24px;
}}
.ds-prog-bar-bg {{
    height: 3px; background: {C["paperEdge"]}; border-radius: 2px; overflow: hidden;
    margin-bottom: 6px;
}}
.ds-prog-bar-fill {{
    height: 100%; background: {C["red"]}; transition: width 0.6s ease;
    border-radius: 2px;
}}
.ds-prog-status {{
    display: flex; justify-content: space-between; align-items: baseline;
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    margin-bottom: 20px;
}}
.ds-prog-msg {{ color: {C["inkMuted"]}; }}
.ds-prog-pct {{ color: {C["red"]}; font-weight: 500; }}
.ds-prog-log {{
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    color: {C["inkMuted"]}; line-height: 1.8;
    max-height: 120px; overflow-y: auto;
    border-top: 1px solid {C["paperEdge"]}; padding-top: 14px;
}}
.ds-prog-pieces {{
    display: flex; justify-content: center; gap: 14px;
    margin-top: 24px; font-size: 24px; opacity: 0.35;
}}
.ds-prog-grid {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px; margin-top: 20px;
}}
.ds-prog-board {{ display: none; }}

/* ── Plano de estudo (4 semanas) ─────────────────────────────────────────── */
.ds-week-grid {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px; margin-bottom: 20px;
}}
.ds-week-card {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-radius: 4px; padding: 14px 16px;
    border-top: 2px solid {C["borderMid"]};
}}
.ds-week-card-active {{ border-top-color: {C["red"]}; }}
.ds-week-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase;
    color: {C["inkFaint"]}; margin-bottom: 5px;
}}
.ds-week-title {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 15px; font-weight: 700; color: {C["ink"]}; margin-bottom: 6px;
}}
.ds-week-body {{
    font-family: 'Inter', system-ui;
    font-size: 12px; color: {C["inkMuted"]}; line-height: 1.6;
}}

/* ── Player card ─────────────────────────────────────────────────────────── */
.ds-player-card {{
    background: {C["paper"]};
    border: 1px solid {C["paperEdge"]};
    border-radius: 4px; padding: 18px 20px;
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
    margin-bottom: 12px; position: relative;
}}
.ds-player-avatar {{
    width: 44px; height: 44px; border-radius: 50%;
    background: {C["ink"]};
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: {C["paper"]}; flex-shrink: 0;
}}
.ds-player-info {{ flex: 1; min-width: 0; }}
.ds-player-name {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(16px,4vw,20px); font-weight: 700; color: {C["ink"]};
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.ds-player-meta {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: {C["inkMuted"]}; margin-top: 3px; letter-spacing: 0.06em;
}}
.ds-player-actions {{ display: flex; align-items: center; gap: 10px; flex-shrink: 0; }}
.ds-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 4px 10px; border-radius: 2px; border: 1px solid;
}}
.ds-badge-self {{ background:{C["paper"]};  border-color:{C["ink"]};  color:{C["ink"]};  }}
.ds-badge-opp  {{ background:{C["redBg"]};  border-color:{C["red"]};  color:{C["red"]};  }}

/* ── Section label ───────────────────────────────────────────────────────── */
.ds-section-lbl {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase;
    color: {C["inkFaint"]}; margin-bottom: 14px; margin-top: 4px;
    border-bottom: 1px solid {C["paperEdge"]}; padding-bottom: 8px;
}}

/* ── Metric grid ─────────────────────────────────────────────────────────── */
.ds-metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px; margin-bottom: 14px;
}}
.ds-metric-card {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-radius: 4px; padding: 16px 18px; border-top: 3px solid {C["inkFaint"]};
}}
.ds-metric-lbl {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: {C["inkFaint"]}; letter-spacing: 0.18em;
    text-transform: uppercase; margin-bottom: 8px;
}}
.ds-metric-val {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(20px,4vw,26px); font-weight: 700; color: {C["ink"]};
}}
.ds-metric-sub {{
    font-family: 'Inter', system-ui;
    font-size: 11px; color: {C["inkMuted"]}; margin-top: 4px;
}}

/* ── Generic paper section ───────────────────────────────────────────────── */
.ds-card {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-radius: 4px; padding: 20px 22px; margin-bottom: 12px;
}}

/* ── Color bars ──────────────────────────────────────────────────────────── */
.cs-bar-bg {{ background: {C["paperEdge"]}; border-radius: 3px; overflow: hidden; position: relative; }}
.cs-bar-fill {{
    height: 100%; border-radius: 3px;
    display: flex; align-items: center; justify-content: flex-end;
    padding-right: 6px; box-sizing: border-box;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 500; color: #fff;
}}

/* ── Opening rows ────────────────────────────────────────────────────────── */
.cs-opening-row {{ padding:10px 0; border-bottom:1px solid {C["paperEdge"]}; }}
.cs-opening-row:last-child {{ border-bottom:none; }}
.cs-opening-top {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }}
.cs-opening-name {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 13px; color: {C["ink"]};
    display: flex; align-items: center; gap: 6px;
}}
.cs-opening-right {{ display:flex; align-items:center; gap:6px; }}
.cs-opening-games {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkFaint"]}; }}
.cs-opening-pct  {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:16px; font-weight:600; }}
.cs-tag {{ font-family:'JetBrains Mono',monospace; font-size:9px; padding:2px 8px; border-radius:2px; border:1px solid; }}
.cs-tag-best {{ background:{C["greenBg"]}; border-color:{C["greenBdr"]}; color:{C["green"]}; }}
.cs-tag-weak {{ background:{C["redBg"]};   border-color:{C["redBdr"]};   color:{C["red"]};   }}

/* ── Error quality bars ──────────────────────────────────────────────────── */
.cs-qbar-row  {{ margin-bottom:12px; }}
.cs-qbar-head {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px; }}
.cs-qbar-lbl  {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:13px; color:{C["inkMid"]}; }}
.cs-qbar-val-wrap {{ font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:500; }}
.cs-qbar-muted    {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; }}

/* ── Phase bars ──────────────────────────────────────────────────────────── */
.cs-phase-row  {{ margin-bottom:16px; }}
.cs-phase-head {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:5px; }}
.cs-phase-lbl  {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:14px; color:{C["ink"]}; }}
.cs-phase-sub  {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; margin-top:2px; }}
.cs-phase-val  {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:22px; font-weight:600; }}

/* ── Insight box ─────────────────────────────────────────────────────────── */
.cs-insight {{
    background:{C["amberBg"]}; border:1px solid {C["amber"]}40;
    border-radius:4px; padding:14px 16px; margin-top:16px;
    border-left: 3px solid {C["amber"]};
}}
.cs-insight-lbl {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["amber"]}; letter-spacing:0.1em; margin-bottom:4px; }}
.cs-insight-txt {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:14px; color:{C["inkMid"]}; line-height:1.7; }}

/* ── Tactics grid ────────────────────────────────────────────────────────── */
.cs-tactics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; }}
.cs-tactic-card {{ background:{C["paper"]}; border:1px solid {C["paperEdge"]}; border-radius:4px; padding:14px; display:flex; align-items:center; gap:10px; }}
.cs-tac-icon    {{ font-size:24px; flex-shrink:0; }}
.cs-tac-name    {{ font-family:'Inter',system-ui; font-size:12px; color:{C["inkMid"]}; margin-bottom:3px; }}
.cs-tac-bar-row {{ display:flex; align-items:center; gap:8px; }}
.cs-tac-bar-bg  {{ flex:1; height:5px; background:{C["paperEdge"]}; border-radius:3px; overflow:hidden; }}
.cs-tac-bar-fill {{ height:100%; border-radius:3px; }}
.cs-tac-count   {{ font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:500; }}

/* ── Radar legend ────────────────────────────────────────────────────────── */
.cs-radar-legend      {{ display:flex; flex-wrap:wrap; gap:12px; justify-content:center; margin-top:12px; }}
.cs-radar-legend-item {{ display:flex; align-items:center; gap:6px; font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; }}
.cs-radar-dot         {{ width:8px; height:8px; border-radius:2px; background:{C["inkMid"]}; opacity:0.4; }}

/* ── Win-rate by color ───────────────────────────────────────────────────── */
.cs-color-block {{ margin-bottom:16px; }}
.cs-color-head  {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:8px; }}
.cs-color-lbl   {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:14px; color:{C["ink"]}; }}
.cs-color-sub   {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; }}
.cs-color-pct   {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:28px; font-weight:700; }}

/* ── Result detail screens (Step IV) ────────────────────────────────────── */
.ds-detail-header {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-radius: 4px 4px 0 0;
    padding: 16px 20px;
    display: flex; justify-content: space-between; align-items: center;
    position: relative; overflow: hidden;
}}
.ds-detail-hdr-self {{ border-top: 3px solid {C["ink"]}; }}
.ds-detail-hdr-opp  {{ border-top: 3px solid {C["red"]}; }}
.ds-detail-title      {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; }}
.ds-detail-title-self {{ color: {C["ink"]}; }}
.ds-detail-title-opp  {{ color: {C["red"]}; }}
.ds-detail-sub  {{ font-family: 'Inter', system-ui; font-size: 11px; color: {C["inkMuted"]}; margin-top: 2px; }}
.ds-detail-body {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-top: none; border-radius: 0 0 4px 4px;
    padding: clamp(18px,4vw,28px) clamp(16px,4vw,28px);
    margin-bottom: 14px;
}}
.ds-detail-body h1,.ds-detail-body h2,.ds-detail-body h3 {{
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    color: {C["ink"]} !important; font-weight: 700 !important;
}}
.ds-detail-body h1 {{ font-size: clamp(20px,4vw,26px) !important; border-bottom: 1px solid {C["paperEdge"]}; padding-bottom: 6px; margin-bottom: 12px; }}
.ds-detail-body h2 {{ font-size: clamp(16px,3vw,20px) !important; margin-top: 22px; }}
.ds-detail-body h3 {{ font-size: 14px !important; color: {C["inkMid"]} !important; margin-top: 14px; }}
.ds-detail-body p  {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:15px; line-height:1.7; color:{C["inkMid"]}; }}
.ds-detail-body li {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:14px; line-height:1.6; color:{C["inkMid"]}; }}
.ds-detail-body table {{ width:100%; border-collapse:collapse; margin:12px 0; font-size:13px; overflow-x:auto; display:block; }}
.ds-detail-body th {{ font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.1em; background:{C["bg"]}; padding:7px 10px; text-align:left; border:1px solid {C["paperEdge"]}; color:{C["inkMuted"]}; text-transform:uppercase; }}
.ds-detail-body td {{ font-family:'Inter',system-ui; font-size:12px; padding:6px 10px; border:1px solid {C["paperEdge"]}; color:{C["inkMid"]}; }}

/* ── Stamp CONFIDENCIAL ──────────────────────────────────────────────────── */
.ds-stamp {{
    position: absolute; right: 14px; top: 50%; transform: translateY(-50%) rotate(-12deg);
    border: 2.5px double {C["red"]};
    color: {C["red"]}; border-radius: 2px;
    padding: 3px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.18em; font-weight: 500;
    opacity: 0.85; pointer-events: none; text-transform: uppercase;
    white-space: nowrap;
}}

/* ── ACPL hero ───────────────────────────────────────────────────────────── */
.ds-acpl-hero   {{ text-align: center; padding: 20px 0 14px; border-bottom: 1px solid {C["paperEdge"]}; margin-bottom: 20px; }}
.ds-acpl-val    {{ font-family: 'Cormorant Garamond', Georgia, serif; font-size: clamp(44px,10vw,64px); font-weight: 700; line-height: 1; color: {C["ink"]}; }}
.ds-acpl-lbl    {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; color: {C["inkFaint"]}; letter-spacing: 0.2em; text-transform: uppercase; margin-top: 4px; }}
.ds-acpl-interp {{ font-family: 'Cormorant Garamond', Georgia, serif; font-size: 15px; color: {C["inkMuted"]}; margin-top: 6px; font-style: italic; }}

/* ── CTA / Reset wraps ───────────────────────────────────────────────────── */
.ds-cta-wrap   {{ text-align: center; padding: 24px 0 8px; }}
.cs-reset-wrap {{ display:flex; justify-content:center; margin-top:24px; }}

/* ── Tabs ────────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] {{ gap:0; }}
button[data-baseweb="tab"] {{
    font-family:'JetBrains Mono',monospace !important;
    font-size:10px !important; letter-spacing:0.1em !important;
    text-transform:uppercase !important;
    color:{C["inkMuted"]} !important;
    background:transparent !important;
    border:none !important; border-radius:0 !important;
    border-bottom:2px solid transparent !important;
    height:42px !important; padding:0 16px !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color:{C["ink"]} !important;
    border-bottom:2px solid {C["ink"]} !important;
    font-weight:500 !important;
}}
[data-baseweb="tab-list"] {{
    background:transparent !important;
    border-bottom:1px solid {C["paperEdge"]} !important;
    gap:0 !important;
}}
[data-baseweb="tab-panel"] {{
    background:transparent !important; border:none !important; padding:18px 0 !important;
}}

/* ── Tablet (≥768px) ─────────────────────────────────────────────────────── */
@media (min-width: 768px) {{
    .ds-prog-grid {{ grid-template-columns: 1fr 180px; align-items: start; }}
    .ds-prog-board {{ display: block; }}
    .ds-week-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}

/* ── Desktop (≥1024px) ───────────────────────────────────────────────────── */
@media (min-width: 1024px) {{
    .ds-week-grid {{ grid-template-columns: repeat(4, 1fr); }}
    .ds-results-wrap {{ padding: 0 16px; }}
}}

/* ── Print ───────────────────────────────────────────────────────────────── */
@media print {{
    .ds-header, .ds-footer, [data-testid="stButton"] {{ display:none !important; }}
    body, .stApp {{ background: white !important; }}
    .ds-detail-body {{ max-height:none !important; }}
}}

/* ── Mobile ──────────────────────────────────────────────────────────────── */
@media (max-width:479px) {{
    .ds-stamp {{ display:none; }}
    .ds-step-name {{ display:none; }}
    .ds-connector {{ width:20px !important; }}
    button[data-baseweb="tab"] {{ font-size:9px !important; padding:0 10px !important; }}
    .cs-tactics {{ grid-template-columns:1fr 1fr !important; }}
    .ds-wiz-sub {{ font-size:12px; }}
}}
</style>"""


# ── SVG / HTML helpers ────────────────────────────────────────────────────────

def donut_svg(wins: int, draws: int, losses: int, C: dict | None = None) -> str:
    """Donut chart SVG for wins/draws/losses."""
    if C is None:
        C = DOSSIE
    total = wins + draws + losses or 1
    circ  = 2 * math.pi * 72
    w_f   = wins   / total
    d_f   = draws  / total
    l_f   = losses / total
    win_pct = f"{w_f*100:.0f}%"

    def seg(frac, color, offset_frac):
        da  = f"{frac*circ:.2f} {circ:.2f}"
        off = f"{-offset_frac*circ:.2f}"
        return (
            f'<circle cx="90" cy="90" r="72" fill="none" stroke="{color}" '
            f'stroke-width="20" stroke-dasharray="{da}" '
            f'stroke-dashoffset="{off}" />'
        )

    segs = (
        seg(w_f, C["green"],    0) +
        seg(d_f, C["inkMuted"], w_f) +
        seg(l_f, C["red"],      w_f + d_f)
    )
    return f"""
<svg width="180" height="180" viewBox="0 0 180 180"
     style="display:block;margin:0 auto;overflow:visible">
  <g transform="rotate(-90 90 90)">
    <circle cx="90" cy="90" r="72" fill="none"
            stroke="{C["border"]}" stroke-width="20"/>
    {segs}
  </g>
  <text x="90" y="82" text-anchor="middle"
        font-family="'Cormorant Garamond',Georgia,serif"
        font-size="26" font-weight="bold" fill="{C["ink"]}">{win_pct}</text>
  <text x="90" y="97" text-anchor="middle"
        font-family="'JetBrains Mono',monospace"
        font-size="10" fill="{C["inkMuted"]}" letter-spacing="1">TX. VITÓRIA</text>
  <text x="90" y="111" text-anchor="middle"
        font-family="'JetBrains Mono',monospace"
        font-size="10" fill="{C["inkFaint"]}">{total} partidas</text>
</svg>"""


def radar_svg(scores: list[float], C: dict | None = None) -> str:
    """Hexagonal radar chart SVG for 6 skill scores (0–100)."""
    if C is None:
        C = DOSSIE
    cx, cy, R = 110, 110, 80
    labels = ["ABERTURA", "TÁTICAS", "MEIO-JOGO", "FINAL", "DEFESA", "TEMPO"]
    colors = [C["green"] if s > 64 else (C["amber"] if s > 46 else C["red"])
              for s in scores]
    angles = [-90 + i * 60 for i in range(6)]

    def pt(r_frac, deg):
        rad = math.radians(deg)
        return cx + r_frac * R * math.cos(rad), cy + r_frac * R * math.sin(rad)

    grid_html = ""
    for frac in [0.25, 0.5, 0.75, 1.0]:
        pts = " ".join(f"{pt(frac, a)[0]:.1f},{pt(frac, a)[1]:.1f}" for a in angles)
        grid_html += f'<polygon points="{pts}" fill="none" stroke="{C["border"]}" stroke-width="1"/>'

    axes_html = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{pt(1.0, a)[0]:.1f}" y2="{pt(1.0, a)[1]:.1f}"'
        f' stroke="{C["border"]}" stroke-width="1"/>'
        for a in angles
    )

    data_pts = " ".join(f"{pt(s/100, a)[0]:.1f},{pt(s/100, a)[1]:.1f}"
                        for s, a in zip(scores, angles))
    poly = (f'<polygon points="{data_pts}" fill="{C["inkMid"]}" fill-opacity="0.18" '
            f'stroke="{C["inkMid"]}" stroke-width="2"/>')

    dots_html = ""
    lbl_html  = ""
    for s, a, lbl, clr in zip(scores, angles, labels, colors):
        x, y = pt(s/100, a)
        dots_html += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                      f'fill="{C["inkMid"]}" stroke="{C["paper"]}" stroke-width="2"/>')
        lx, ly = pt(1.32, a)
        anchor = "middle"
        if   lx < cx - 5: anchor = "end"
        elif lx > cx + 5: anchor = "start"
        lbl_html += (
            f'<text x="{lx:.1f}" y="{ly - 7:.1f}" text-anchor="{anchor}" '
            f'font-family="\'JetBrains Mono\',monospace" '
            f'font-size="9" fill="{C["inkMuted"]}" letter-spacing="0.5">{lbl}</text>'
            f'<text x="{lx:.1f}" y="{ly + 6:.1f}" text-anchor="{anchor}" '
            f'font-family="\'Cormorant Garamond\',Georgia,serif" '
            f'font-size="12" font-weight="bold" fill="{clr}">{int(s)}</text>'
        )

    return (
        f'<svg width="220" height="220" viewBox="0 0 220 220" '
        f'style="display:block;margin:0 auto;overflow:visible">'
        f'{grid_html}{axes_html}{poly}{dots_html}{lbl_html}</svg>'
    )


def color_bar(pct: float, color: str, height: int = 16, show_label: bool = True) -> str:
    """Horizontal fill bar with optional percentage label."""
    pct = max(0, min(100, pct))
    label = (
        f'<span style="font-family:\'Courier New\',Courier,monospace;font-size:10px;'
        f'font-weight:bold;color:#fff;padding-right:6px;">{pct:.0f}%</span>'
        if show_label and pct > 18 else ""
    )
    return (
        f'<div class="cs-bar-bg" style="height:{height}px">'
        f'<div class="cs-bar-fill" style="width:{pct:.1f}%;background:{color};height:{height}px">'
        f'{label}</div></div>'
    )


def section_lbl(text: str) -> str:
    return f'<div class="ds-section-lbl">{text}</div>'


def chessboard_svg(C: dict | None = None) -> str:
    """Static decorative 8×8 board SVG in dossie palette."""
    if C is None:
        C = DOSSIE
    sq = 22  # square size px
    board_size = sq * 8
    squares = ""
    for row in range(8):
        for col in range(8):
            light = (row + col) % 2 == 0
            fill = C["paper"] if light else C["border"]
            x, y = col * sq, row * sq
            squares += f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="{fill}"/>'
    return (
        f'<svg width="{board_size}" height="{board_size}" viewBox="0 0 {board_size} {board_size}" '
        f'style="display:block;border:1px solid {C["paperEdge"]};border-radius:2px;opacity:0.6">'
        f'{squares}</svg>'
    )


# ── Render helpers (require streamlit) ────────────────────────────────────────

def render_header() -> None:
    lang       = st.session_state.get("lang", "pt")
    other_lang = "en" if lang == "pt" else "pt"
    btn_label  = "EN" if lang == "pt" else "PT"
    st.markdown(f"""
    <div class="ds-header">
      <div class="ds-header-left">
        <span class="ds-logo">♞</span>
        <span class="ds-title">CHESS SCOUT</span>
      </div>
      <a href="?lang={other_lang}" class="ds-lang-btn" target="_self">{btn_label}</a>
    </div>
    """, unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        '<div class="ds-footer">CHESS SCOUT · STOCKFISH + PYTHON-CHESS</div>',
        unsafe_allow_html=True,
    )


_STEP_NAMES = ["Plataforma", "Usuário", "Perspectiva", "Tipo"]


def render_stepper(current: int) -> None:
    label = f"PASSO {current + 1} DE 4"
    st.markdown(f'<div class="ds-step-label">{label}</div>', unsafe_allow_html=True)

    nodes_html = ""
    for i, name in enumerate(_STEP_NAMES):
        if i < current:
            circ_cls = "ds-circle-done"
            sym      = "✓"
            name_cls = ""
        elif i == current:
            circ_cls = "ds-circle-active"
            sym      = str(i + 1)
            name_cls = "ds-name-active"
        else:
            circ_cls = "ds-circle-future"
            sym      = str(i + 1)
            name_cls = ""

        conn = ""
        if i < 3:
            conn_cls = "ds-conn-done" if i < current else "ds-conn-pending"
            conn = f'<div class="ds-connector {conn_cls}"></div>'

        nodes_html += (
            f'<div class="ds-step-node">'
            f'<div class="ds-step-circle {circ_cls}">{sym}</div>'
            f'<div class="ds-step-name {name_cls}">{name}</div>'
            f'</div>'
            f'{conn}'
        )

    st.markdown(
        f'<div class="ds-stepper">{nodes_html}</div>',
        unsafe_allow_html=True,
    )


def prog_html(msg: str, pct: int, log_lines: list[str],
              C: dict | None = None) -> str:
    """Loading-screen progress bar + log HTML snippet."""
    if C is None:
        C = DOSSIE
    pieces     = ["♔", "♕", "♖", "♗", "♘", "♙"]
    thresholds = [10, 25, 45, 65, 80, 95]
    piece_html = "".join(
        f'<span style="color:{C["red"] if pct >= t else C["border"]};'
        f'transition:color 0.4s">{p}</span>'
        for p, t in zip(pieces, thresholds)
    )
    log_html = "".join(f"<div>→ {line}</div>" for line in log_lines[-8:])
    board = chessboard_svg(C)
    return f"""
<div class="ds-prog-bar-bg"><div class="ds-prog-bar-fill" style="width:{pct}%"></div></div>
<div class="ds-prog-status">
  <span class="ds-prog-msg">{msg}</span>
  <span class="ds-prog-pct">{pct}%</span>
</div>
<div class="ds-prog-grid">
  <div>
    <div class="ds-prog-log">{log_html}</div>
    <div class="ds-prog-pieces">{piece_html}</div>
  </div>
  <div class="ds-prog-board">{board}</div>
</div>
"""
