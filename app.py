import streamlit as st
import streamlit.components.v1 as components
import math
import time

from modules.fetcher import fetch_games
from modules.analyzer import analyze_games
from modules.stats import compute_stats
from modules.reporter import generate_diagnostic, generate_opponent_guide, save_reports

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chess Scout",
    page_icon="♞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS: dict = {
    "theme":         "dark",
    "step":          0,
    "platform":      "lichess",
    "username":      "",
    "perspective":   "self",
    "time_classes":  ["bullet", "blitz", "rapid"],
    "stats":         None,
    "profile":       None,
    "diagnostic_md": None,
    "guide_md":      None,
    "active_tab":    0,
    "analyzing":     False,
    "analyze_pct":   0,
    "analyze_msg":   "",
    "analyze_error": "",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Color palettes ────────────────────────────────────────────────────────────
DARK: dict = {
    "bg":        "#111827",
    "surface":   "#1a2535",
    "card":      "#1f2d3f",
    "border":    "#2e4058",
    "borderMid": "#3a5070",
    "primary":   "#4e8ecb",
    "green":     "#4aaa6e",
    "greenBg":   "#0e2a1a",
    "greenBdr":  "#1e4a30",
    "red":       "#e05252",
    "redBg":     "#2a0e0e",
    "redBdr":    "#4a1e1e",
    "gold":      "#d4a843",
    "amber":     "#d4843a",
    "slate":     "#7090a8",
    "txt":       "#dce8f5",
    "txtMid":    "#8faabf",
    "txtMuted":  "#4e6880",
    "headerBg":  "#0d1520",
    "footerBg":  "#0d1520",
}
LIGHT: dict = {
    "bg":        "#f4f0e8",
    "surface":   "#faf7f2",
    "card":      "#ffffff",
    "border":    "#ddd5c4",
    "borderMid": "#c8bfae",
    "primary":   "#1e4a7a",
    "green":     "#2a6e42",
    "greenBg":   "#edf7f2",
    "greenBdr":  "#a8d5bc",
    "red":       "#8b2222",
    "redBg":     "#fdf0f0",
    "redBdr":    "#e8b8b8",
    "gold":      "#a07030",
    "amber":     "#9a5a18",
    "slate":     "#607080",
    "txt":       "#1a1a1a",
    "txtMid":    "#4a3c2e",
    "txtMuted":  "#8a7a68",
    "headerBg":  "#1e4a7a",
    "footerBg":  "#f0ece4",
}

C  = DARK  if st.session_state.theme == "dark" else LIGHT
SH = "0 8px 32px #00000050" if st.session_state.theme == "dark" else "0 4px 20px #00000012"

# ── CSS injection ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Reset Streamlit chrome ────────────────────────────────────────────────── */
#MainMenu, footer, header {{ display:none !important; }}
[data-testid="stSidebar"]       {{ display:none !important; }}
[data-testid="stDecoration"]    {{ display:none !important; }}
[data-testid="stStatusWidget"]  {{ display:none !important; }}
.stDeployButton                 {{ display:none !important; }}
[data-testid="stToolbar"]       {{ display:none !important; }}

/* ── Global ─────────────────────────────────────────────────────────────────── */
body, .stApp {{
    background: {C["bg"]} !important;
    font-family: 'Courier New', Courier, monospace;
    color: {C["txt"]};
    margin: 0; padding: 0;
}}
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}
section[data-testid="stMain"] > div {{ padding: 0 !important; }}

/* ── Fixed header ───────────────────────────────────────────────────────────── */
.cs-header {{
    position: fixed; top:0; left:0; right:0;
    height: 56px;
    background: {C["headerBg"]};
    border-bottom: 1px solid {C["border"]};
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 24px;
    z-index: 9999;
}}
.cs-header-left {{
    display: flex; align-items: center; gap: 10px;
}}
.cs-logo {{ font-size: 22px; color: #fff; }}
.cs-title {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 13px; font-weight: bold;
    letter-spacing: 0.3em; color: #fff;
}}
.cs-subtitle {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 9px; color: #ffffff50; margin-left: 4px;
}}

/* ── Page scaffold ──────────────────────────────────────────────────────────── */
.cs-page {{
    padding-top: 56px; min-height: 100vh;
    display: flex; flex-direction: column;
    background: {C["bg"]};
}}
.cs-main {{
    flex: 1; display: flex; flex-direction: column;
    align-items: center; padding: 48px 20px;
}}
.cs-wizard-wrap  {{ width:100%; max-width:520px; }}
.cs-results-wrap {{ width:100%; max-width:800px; }}

/* ── Footer ─────────────────────────────────────────────────────────────────── */
.cs-footer {{
    background: {C["footerBg"]};
    border-top: 1px solid {C["border"]};
    padding: 14px 22px; text-align: center;
    font-family: 'Courier New', Courier, monospace;
    font-size: 10px; color: {C["txtMuted"]}; letter-spacing: 0.22em;
}}

/* ── Stepper ─────────────────────────────────────────────────────────────────── */
.cs-step-label {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 10px; color: {C["txtMuted"]};
    letter-spacing: 0.22em; text-transform: uppercase;
    text-align: center; margin-bottom: 20px;
}}
.cs-stepper {{
    display: flex; align-items: center;
    justify-content: center; margin-bottom: 32px;
}}
.cs-step-node {{
    display: flex; flex-direction: column;
    align-items: center; gap: 6px;
}}
.cs-step-circle {{
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Courier New', Courier, monospace;
    font-size: 13px; font-weight: bold;
    border: 2px solid;
}}
.cs-circle-done   {{ background:{C["primary"]}; color:#fff; border-color:{C["primary"]}; }}
.cs-circle-active {{ background:transparent; color:{C["primary"]}; border-color:{C["primary"]}; }}
.cs-circle-future {{ background:transparent; color:{C["txtMuted"]}; border-color:{C["border"]}; }}
.cs-step-name {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 9px; letter-spacing: 0.1em;
}}
.cs-name-active  {{ color:{C["primary"]}; }}
.cs-name-inactive{{ color:{C["txtMuted"]}; }}
.cs-connector {{
    width:36px; height:2px; margin-bottom:22px; flex-shrink:0;
}}
.cs-conn-done    {{ background:{C["primary"]}; }}
.cs-conn-pending {{ background:{C["border"]}; }}

/* ── Wizard card ─────────────────────────────────────────────────────────────── */
.cs-wizard-card {{
    background: {C["card"]};
    border: 1px solid {C["border"]};
    border-radius: 18px;
    box-shadow: {SH};
    padding: 42px 44px;
    text-align: center;
}}
.cs-wiz-icon  {{ font-size:36px; margin-bottom:12px; }}
.cs-wiz-title {{
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 17px; font-weight: bold;
    color: {C["txt"]}; margin-bottom: 8px;
}}
.cs-wiz-sub {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px; color: {C["txtMuted"]}; margin-bottom: 28px;
}}

/* ── Tile grid ────────────────────────────────────────────────────────────────── */
.cs-tiles-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
.cs-tiles-4 {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.cs-tile {{
    border: 2px solid {C["border"]}; border-radius:12px;
    padding: 20px 14px; text-align:center; cursor:pointer;
    background: {C["card"]}; color:{C["txt"]};
    transition: all 0.18s;
    display:flex; flex-direction:column; align-items:center; gap:8px;
}}
.cs-tile:hover {{ border-color:{C["primary"]}; }}
.cs-tile.sel {{
    background:{C["primary"]}; border-color:{C["primary"]};
    color:#fff; box-shadow: 0 4px 16px {C["primary"]}40;
}}
.cs-tile-icon   {{ font-size:32px; }}
.cs-tile-iconsm {{ font-size:26px; }}
.cs-tile-lbl {{
    font-family:'Courier New',Courier,monospace;
    font-size:13px; font-weight:bold;
}}
.cs-tile-sub {{
    font-family:'Courier New',Courier,monospace;
    font-size:11px; color:{C["txtMuted"]}; white-space:pre-line; line-height:1.4;
}}
.cs-tile.sel .cs-tile-sub {{ color:#ffffff80; }}

/* ── Nav buttons row ─────────────────────────────────────────────────────────── */
.cs-nav {{ display:flex; justify-content:space-between; align-items:center; margin-top:44px; }}
.cs-nav-ph {{ min-width:80px; }}

/* Override Streamlit buttons ─────────────────────────────────────────────────── */
[data-testid="stButton"] > button {{
    border-radius: 8px !important;
    font-family: 'Courier New',Courier,monospace !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    transition: opacity 0.2s !important;
}}
.btn-primary [data-testid="stButton"] > button {{
    height:42px !important; padding:0 22px !important; font-size:13px !important;
    background:{C["primary"]} !important; color:#fff !important; border:none !important;
}}
.btn-ghost [data-testid="stButton"] > button {{
    height:42px !important; padding:0 22px !important; font-size:13px !important;
    background:transparent !important; color:{C["txtMuted"]} !important;
    border:1px solid {C["border"]} !important;
}}
.btn-small [data-testid="stButton"] > button {{
    height:32px !important; padding:0 14px !important; font-size:11px !important;
    background:{C["primary"]} !important; color:#fff !important; border:none !important;
}}
.btn-theme [data-testid="stButton"] > button {{
    background:rgba(255,255,255,0.1) !important; color:#fff !important;
    border:1px solid rgba(255,255,255,0.2) !important;
    border-radius:20px !important;
    height:36px !important; padding:0 12px !important; font-size:12px !important;
}}
.btn-tab [data-testid="stButton"] > button {{
    height:44px !important; width:100% !important;
    border:none !important; border-radius:0 !important;
    font-family:'Courier New',Courier,monospace !important;
    font-size:11px !important; letter-spacing:0.08em !important;
    text-transform:uppercase !important;
    background:{C["card"]} !important; color:{C["txtMuted"]} !important;
    border-bottom:3px solid transparent !important;
}}
.btn-tab-active [data-testid="stButton"] > button {{
    height:44px !important; width:100% !important;
    border:none !important; border-radius:0 !important;
    font-family:'Courier New',Courier,monospace !important;
    font-size:11px !important; letter-spacing:0.08em !important;
    text-transform:uppercase !important; font-weight:700 !important;
    background:{C["surface"]} !important; color:{C["primary"]} !important;
    border-bottom:3px solid {C["primary"]} !important;
}}
.btn-reset [data-testid="stButton"] > button {{
    height:42px !important; padding:0 22px !important; font-size:13px !important;
    background:transparent !important; color:{C["txtMuted"]} !important;
    border:1px solid {C["border"]} !important;
}}

/* ── Text input ───────────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] > div > div {{
    border:none !important; background:transparent !important;
}}
[data-testid="stTextInput"] input {{
    background:transparent !important;
    border:none !important;
    border-bottom:2px solid {C["primary"]} !important;
    border-radius:0 !important;
    font-family:Georgia,'Times New Roman',serif !important;
    font-size:22px !important; color:{C["txt"]} !important;
    text-align:center !important; padding:8px 0 !important;
    box-shadow:none !important; outline:none !important;
}}
[data-testid="stTextInput"] input:focus {{
    box-shadow:none !important; outline:none !important;
    border-bottom:2px solid {C["primary"]} !important;
}}

/* ── Progress ─────────────────────────────────────────────────────────────────── */
.cs-prog-status {{
    display:flex; justify-content:space-between;
    font-family:'Courier New',Courier,monospace; font-size:11px;
    margin-bottom:8px;
}}
.cs-prog-msg {{ color:{C["txtMuted"]}; }}
.cs-prog-pct {{ color:{C["primary"]}; font-weight:bold; }}
.cs-prog-bar {{
    height:5px; background:{C["surface"]};
    border:1px solid {C["border"]}; border-radius:3px; overflow:hidden;
}}
.cs-prog-fill {{
    height:100%; background:{C["primary"]}; transition:width 0.7s ease;
}}
.cs-prog-pieces {{
    display:flex; justify-content:center; gap:12px;
    margin-top:28px; font-size:22px;
}}

/* ── Player card ──────────────────────────────────────────────────────────────── */
.cs-player-card {{
    background:{C["card"]}; border:1px solid {C["border"]};
    border-radius:14px; padding:18px 20px;
    display:flex; align-items:center; gap:14px; flex-wrap:wrap;
    margin-bottom:14px;
}}
.cs-player-avatar {{
    width:46px; height:46px; border-radius:50%;
    background:{C["primary"]};
    display:flex; align-items:center; justify-content:center;
    font-size:20px; color:#fff; flex-shrink:0;
}}
.cs-player-info {{ flex:1; }}
.cs-player-name {{
    font-family:Georgia,'Times New Roman',serif;
    font-size:17px; font-weight:bold; color:{C["txt"]};
}}
.cs-player-meta {{
    font-family:'Courier New',Courier,monospace;
    font-size:10px; color:{C["txtMuted"]}; margin-top:2px;
}}
.cs-player-actions {{ display:flex; align-items:center; gap:10px; flex-shrink:0; }}
.cs-badge {{
    font-family:'Courier New',Courier,monospace;
    font-size:10px; letter-spacing:0.1em;
    padding:4px 12px; border-radius:20px; border:1px solid;
}}
.cs-badge-self {{ background:{C["greenBg"]}; border-color:{C["greenBdr"]}; color:{C["green"]}; }}
.cs-badge-opp  {{ background:{C["redBg"]};   border-color:{C["redBdr"]};   color:{C["red"]};   }}

/* ── Tab bar ──────────────────────────────────────────────────────────────────── */
.cs-tabbar {{
    background:{C["card"]}; border-radius:10px 10px 0 0;
    border:1px solid {C["border"]}; border-bottom:none;
    overflow:hidden;
}}
.cs-tab-content {{
    background:{C["surface"]}; border:1px solid {C["border"]};
    border-top:none; border-radius:0 0 14px 14px;
    padding:24px 22px;
}}

/* ── Generic card ─────────────────────────────────────────────────────────────── */
.cs-card {{
    background:{C["card"]}; border:1px solid {C["border"]};
    border-radius:12px; padding:22px; margin-bottom:14px;
}}
.cs-section-lbl {{
    font-family:'Courier New',Courier,monospace;
    font-size:10px; letter-spacing:0.22em; text-transform:uppercase;
    color:{C["txtMuted"]}; margin-bottom:16px;
}}

/* ── Metric grid ──────────────────────────────────────────────────────────────── */
.cs-metrics-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px; }}
.cs-metric-card {{
    background:{C["card"]}; border:1px solid {C["border"]};
    border-radius:10px; padding:16px 18px; border-top-width:3px;
}}
.cs-metric-lbl {{
    font-family:'Courier New',Courier,monospace;
    font-size:10px; color:{C["txtMuted"]}; letter-spacing:0.18em;
    text-transform:uppercase; margin-bottom:8px;
}}
.cs-metric-val {{
    font-family:Georgia,'Times New Roman',serif;
    font-size:22px; font-weight:bold; color:{C["txt"]};
}}
.cs-metric-sub {{
    font-family:'Courier New',Courier,monospace;
    font-size:11px; color:{C["txtMuted"]}; margin-top:4px;
}}

/* ── Color bar ────────────────────────────────────────────────────────────────── */
.cs-bar-bg {{
    background:{C["surface"]}; border:1px solid {C["border"]};
    border-radius:6px; overflow:hidden; position:relative;
}}
.cs-bar-fill {{
    height:100%; border-radius:6px;
    display:flex; align-items:center; justify-content:flex-end;
    padding-right:6px; box-sizing:border-box;
    font-family:'Courier New',Courier,monospace;
    font-size:10px; font-weight:bold; color:#fff;
}}

/* ── Opening rows ────────────────────────────────────────────────────────────── */
.cs-opening-row {{
    padding:12px 0; border-bottom:1px solid {C["border"]};
}}
.cs-opening-row:last-child {{ border-bottom:none; }}
.cs-opening-top {{
    display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;
}}
.cs-opening-name {{
    font-family:Georgia,'Times New Roman',serif;
    font-size:13px; color:{C["txt"]};
    display:flex; align-items:center; gap:6px;
}}
.cs-opening-right {{ display:flex; align-items:center; gap:6px; }}
.cs-opening-games {{
    font-family:'Courier New',Courier,monospace; font-size:11px; color:{C["txtMuted"]};
}}
.cs-opening-pct {{
    font-family:'Courier New',Courier,monospace; font-size:16px; font-weight:bold;
}}
.cs-tag {{
    font-family:'Courier New',Courier,monospace; font-size:9px;
    padding:2px 8px; border-radius:20px; border:1px solid;
}}
.cs-tag-best {{ background:{C["greenBg"]}; border-color:{C["greenBdr"]}; color:{C["green"]}; }}
.cs-tag-weak {{ background:{C["redBg"]};   border-color:{C["redBdr"]};   color:{C["red"]};   }}

/* ── Quality bars (Erros tab) ────────────────────────────────────────────────── */
.cs-qbar-row {{ margin-bottom:14px; }}
.cs-qbar-head {{
    display:flex; justify-content:space-between; align-items:baseline;
    margin-bottom:5px;
}}
.cs-qbar-lbl {{
    font-family:Georgia,'Times New Roman',serif; font-size:13px; color:{C["txtMid"]};
}}
.cs-qbar-val-wrap {{
    font-family:'Courier New',Courier,monospace; font-size:13px; font-weight:bold;
}}
.cs-qbar-muted {{
    font-family:'Courier New',Courier,monospace; font-size:11px; color:{C["txtMuted"]};
}}

/* ── Phase bar ────────────────────────────────────────────────────────────────── */
.cs-phase-row {{ margin-bottom:18px; }}
.cs-phase-head {{
    display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:5px;
}}
.cs-phase-lbl {{
    font-family:Georgia,'Times New Roman',serif; font-size:13px; color:{C["txt"]};
}}
.cs-phase-sub {{
    font-family:'Courier New',Courier,monospace; font-size:10px; color:{C["txtMuted"]}; margin-top:2px;
}}
.cs-phase-val {{
    font-family:Georgia,'Times New Roman',serif; font-size:22px; font-weight:bold;
}}

/* ── Insight box ─────────────────────────────────────────────────────────────── */
.cs-insight {{
    background:{C["redBg"]}; border:1px solid {C["redBdr"]};
    border-radius:8px; padding:14px 16px; margin-top:18px;
}}
.cs-insight-lbl {{
    font-family:'Courier New',Courier,monospace; font-size:10px;
    color:{C["red"]}; letter-spacing:0.1em; margin-bottom:5px;
}}
.cs-insight-txt {{
    font-family:Georgia,'Times New Roman',serif;
    font-size:13px; color:{C["txtMid"]}; line-height:1.7;
}}

/* ── Tactics grid ────────────────────────────────────────────────────────────── */
.cs-tactics {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }}
.cs-tactic-card {{
    background:{C["surface"]}; border:1px solid {C["border"]};
    border-radius:10px; padding:14px 16px;
    display:flex; align-items:center; gap:12px;
}}
.cs-tac-icon {{ font-size:26px; flex-shrink:0; }}
.cs-tac-name {{
    font-family:Georgia,'Times New Roman',serif;
    font-size:12px; color:{C["txtMid"]}; margin-bottom:3px;
}}
.cs-tac-bar-row {{ display:flex; align-items:center; gap:8px; }}
.cs-tac-bar-bg {{
    flex:1; height:6px; background:{C["card"]};
    border:1px solid {C["border"]}; border-radius:3px; overflow:hidden;
}}
.cs-tac-bar-fill {{ height:100%; border-radius:3px; }}
.cs-tac-count {{
    font-family:'Courier New',Courier,monospace;
    font-size:14px; font-weight:bold;
}}

/* ── Radar legend ─────────────────────────────────────────────────────────────── */
.cs-radar-legend {{
    display:flex; flex-wrap:wrap; gap:14px;
    justify-content:center; margin-top:14px;
}}
.cs-radar-legend-item {{
    display:flex; align-items:center; gap:6px;
    font-family:'Courier New',Courier,monospace;
    font-size:11px; color:{C["txtMid"]};
}}
.cs-radar-dot {{
    width:10px; height:10px; border-radius:2px;
    background:{C["primary"]}; opacity:0.5;
}}

/* ── Report ────────────────────────────────────────────────────────────────────── */
.cs-report-outer {{ border:1px solid {C["border"]}; border-radius:12px; overflow:hidden; }}
.cs-rpt-hdr {{
    padding:14px 20px; border-bottom:1px solid {C["border"]};
    display:flex; justify-content:space-between; align-items:center; gap:12px;
}}
.cs-rpt-hdr-self {{ background:{C["greenBg"]}; }}
.cs-rpt-hdr-opp  {{ background:{C["redBg"]};   }}
.cs-rpt-title-self {{
    font-family:'Courier New',Courier,monospace;
    font-size:11px; letter-spacing:0.14em; color:{C["green"]};
}}
.cs-rpt-title-opp {{
    font-family:'Courier New',Courier,monospace;
    font-size:11px; letter-spacing:0.14em; color:{C["red"]};
}}
.cs-rpt-sub {{
    font-family:'Courier New',Courier,monospace;
    font-size:10px; color:{C["txtMuted"]}; margin-top:2px;
}}
.cs-rpt-body {{
    max-height:500px; overflow-y:auto;
    padding:24px 26px;
    background:{C["card"]};
}}
.cs-rpt-main-title {{
    font-family:Georgia,'Times New Roman',serif;
    font-size:15px; font-weight:bold; color:{C["txt"]}; margin-bottom:4px;
}}
.cs-rpt-meta {{
    font-family:'Courier New',Courier,monospace;
    font-size:10px; color:{C["txtMuted"]}; margin-bottom:24px;
}}
.cs-rpt-sec-title {{
    font-family:'Courier New',Courier,monospace;
    font-size:11px; letter-spacing:0.1em; margin-bottom:10px;
}}
.cs-rpt-item {{
    padding-left:14px;
    font-family:Georgia,'Times New Roman',serif;
    font-size:13px; color:{C["txtMid"]}; line-height:1.7; margin-bottom:7px;
}}
.cs-plan-lbl {{
    font-family:'Courier New',Courier,monospace;
    font-size:11px; letter-spacing:0.12em; color:{C["primary"]};
    margin-bottom:14px; margin-top:20px;
}}
.cs-priority-lbl {{
    font-family:'Courier New',Courier,monospace;
    font-size:11px; margin-bottom:7px; margin-top:16px;
}}
.cs-checklist {{
    background:{C["surface"]}; border:1px solid {C["border"]};
    border-radius:8px; padding:14px 18px; margin-top:20px;
}}
.cs-checklist-lbl {{
    font-family:'Courier New',Courier,monospace;
    font-size:10px; color:{C["txtMuted"]}; letter-spacing:0.18em; margin-bottom:12px;
}}
.cs-checklist-item {{
    display:flex; align-items:flex-start; gap:10px; margin-bottom:9px;
}}
.cs-checkbox {{
    width:14px; height:14px; border-radius:3px;
    border:1px solid {C["borderMid"]}; flex-shrink:0; margin-top:2px;
}}
.cs-checklist-txt {{
    font-family:Georgia,'Times New Roman',serif;
    font-size:13px; color:{C["txtMid"]}; line-height:1.6;
}}

/* ── Win-rate by color ────────────────────────────────────────────────────────── */
.cs-color-block {{ margin-bottom:16px; }}
.cs-color-head {{
    display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:8px;
}}
.cs-color-lbl {{
    font-family:Georgia,'Times New Roman',serif; font-size:14px; color:{C["txt"]};
}}
.cs-color-sub {{
    font-family:'Courier New',Courier,monospace; font-size:10px; color:{C["txtMuted"]};
}}
.cs-color-pct {{
    font-family:Georgia,'Times New Roman',serif; font-size:28px; font-weight:bold;
}}

/* ── Reset wrap ───────────────────────────────────────────────────────────────── */
.cs-reset-wrap {{ display:flex; justify-content:center; margin-top:24px; }}

/* ── Mobile ────────────────────────────────────────────────────────────────────── */
@media (max-width:640px) {{
    .cs-main {{ padding:32px 14px; }}
    .cs-wizard-card {{ padding:28px 20px; }}
    .cs-subtitle {{ display:none; }}
    .cs-step-name {{ display:none; }}
    .cs-connector {{ width:24px !important; }}
    .cs-tab-content {{ padding:18px 16px; }}
    .cs-tactics {{ grid-template-columns:1fr 1fr; }}
    .cs-rpt-body {{ padding:18px; }}
    .btn-tab [data-testid="stButton"] > button {{ font-size:9px !important; }}
    .btn-tab-active [data-testid="stButton"] > button {{ font-size:9px !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ── SVG helpers ───────────────────────────────────────────────────────────────

def _donut_svg(wins: int, draws: int, losses: int) -> str:
    total = wins + draws + losses or 1
    circ  = 2 * math.pi * 72          # circumference for r=72
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
        seg(w_f, C["green"], 0) +
        seg(d_f, C["slate"], w_f) +
        seg(l_f, C["red"],   w_f + d_f)
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
        font-family="Georgia,'Times New Roman',serif"
        font-size="26" font-weight="bold" fill="{C["txt"]}">{win_pct}</text>
  <text x="90" y="97" text-anchor="middle"
        font-family="'Courier New',Courier,monospace"
        font-size="10" fill="{C["txtMuted"]}" letter-spacing="1">TX. VITÓRIA</text>
  <text x="90" y="111" text-anchor="middle"
        font-family="'Courier New',Courier,monospace"
        font-size="10" fill="{C["txtMuted"]}">{total} partidas</text>
</svg>"""


def _radar_svg(scores: list[float]) -> str:
    cx, cy, R = 110, 110, 80
    labels = ["ABERTURA", "TÁTICAS", "MEIO-JOGO", "FINAL", "DEFESA", "TEMPO"]
    colors = [C["green"] if s > 64 else (C["gold"] if s > 46 else C["red"])
              for s in scores]
    angles = [-90 + i * 60 for i in range(6)]

    def pt(r_frac, deg):
        rad = math.radians(deg)
        return cx + r_frac * R * math.cos(rad), cy + r_frac * R * math.sin(rad)

    # grid hexagons
    grid_html = ""
    for frac in [0.25, 0.5, 0.75, 1.0]:
        pts = " ".join(f"{pt(frac, a)[0]:.1f},{pt(frac, a)[1]:.1f}" for a in angles)
        grid_html += f'<polygon points="{pts}" fill="none" stroke="{C["border"]}" stroke-width="1"/>'

    # axis lines
    axes_html = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{pt(1.0, a)[0]:.1f}" y2="{pt(1.0, a)[1]:.1f}"'
        f' stroke="{C["border"]}" stroke-width="1"/>'
        for a in angles
    )

    # data polygon
    data_pts = " ".join(f"{pt(s/100, a)[0]:.1f},{pt(s/100, a)[1]:.1f}"
                        for s, a in zip(scores, angles))
    poly = (f'<polygon points="{data_pts}" fill="{C["primary"]}" fill-opacity="0.25" '
            f'stroke="{C["primary"]}" stroke-width="2"/>')

    # vertex dots & labels
    dots_html = ""
    lbl_html  = ""
    for i, (s, a, lbl, clr) in enumerate(zip(scores, angles, labels, colors)):
        x, y = pt(s/100, a)
        dots_html += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                      f'fill="{C["primary"]}" stroke="{C["card"]}" stroke-width="2"/>')
        lx, ly = pt(1.32, a)
        anchor = "middle"
        if   lx < cx - 5: anchor = "end"
        elif lx > cx + 5: anchor = "start"
        lbl_html += (
            f'<text x="{lx:.1f}" y="{ly - 7:.1f}" text-anchor="{anchor}" '
            f'font-family="\'Courier New\',Courier,monospace" '
            f'font-size="9" fill="{C["txtMuted"]}" letter-spacing="0.5">{lbl}</text>'
            f'<text x="{lx:.1f}" y="{ly + 6:.1f}" text-anchor="{anchor}" '
            f'font-family="\'Courier New\',Courier,monospace" '
            f'font-size="12" font-weight="bold" fill="{clr}">{int(s)}</text>'
        )

    return (
        f'<svg width="220" height="220" viewBox="0 0 220 220" '
        f'style="display:block;margin:0 auto;overflow:visible">'
        f'{grid_html}{axes_html}{poly}{dots_html}{lbl_html}</svg>'
    )


def _color_bar(pct: float, color: str, height: int = 16, show_label: bool = True) -> str:
    pct = max(0, min(100, pct))
    label = f'<span style="font-family:\'Courier New\',Courier,monospace;font-size:10px;font-weight:bold;color:#fff;padding-right:6px;">{pct:.0f}%</span>' if show_label and pct > 18 else ""
    return (
        f'<div class="cs-bar-bg" style="height:{height}px">'
        f'<div class="cs-bar-fill" style="width:{pct:.1f}%;background:{color};height:{height}px">'
        f'{label}</div></div>'
    )


def _section_lbl(text: str) -> str:
    return f'<div class="cs-section-lbl">{text}</div>'


# ── Header ────────────────────────────────────────────────────────────────────

def render_header():
    theme = st.session_state.theme
    icon  = "☀" if theme == "dark" else "☽"
    label = "Claro" if theme == "dark" else "Escuro"
    st.markdown(f"""
    <div class="cs-header">
      <div class="cs-header-left">
        <span class="cs-logo">♞</span>
        <span class="cs-title">CHESS SCOUT</span>
        <span class="cs-subtitle">INTELIGÊNCIA DE JOGO</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    # Theme toggle rendered as floating button via CSS tricks
    st.markdown(
        '<div style="position:fixed;top:10px;right:16px;z-index:10000">',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="btn-theme">', unsafe_allow_html=True)
    if st.button(f"{icon} {label}", key="theme_btn"):
        st.session_state.theme = "light" if theme == "dark" else "dark"
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────

def render_footer():
    st.markdown(
        '<div class="cs-footer">CHESS SCOUT · STOCKFISH + PYTHON-CHESS</div>',
        unsafe_allow_html=True,
    )


# ── Stepper ───────────────────────────────────────────────────────────────────

_STEP_NAMES = ["Plataforma", "Usuário", "Perspectiva", "Tipo"]

def render_stepper(current: int):
    step = current
    label = f"PASSO {step + 1} DE 4"
    st.markdown(f'<div class="cs-step-label">{label}</div>', unsafe_allow_html=True)

    nodes_html = ""
    for i, name in enumerate(_STEP_NAMES):
        if i < step:
            circ_cls = "cs-circle-done"
            sym      = "✓"
            name_cls = "cs-name-inactive"
        elif i == step:
            circ_cls = "cs-circle-active"
            sym      = str(i + 1)
            name_cls = "cs-name-active"
        else:
            circ_cls = "cs-circle-future"
            sym      = str(i + 1)
            name_cls = "cs-name-inactive"

        conn = ""
        if i < 3:
            conn_cls = "cs-conn-done" if i < step else "cs-conn-pending"
            conn = f'<div class="cs-connector {conn_cls}"></div>'

        nodes_html += (
            f'<div class="cs-step-node">'
            f'<div class="cs-step-circle {circ_cls}">{sym}</div>'
            f'<div class="cs-step-name {name_cls}">{name}</div>'
            f'</div>'
            f'{conn}'
        )

    st.markdown(
        f'<div class="cs-stepper">{nodes_html}</div>',
        unsafe_allow_html=True,
    )


# ── Tile helper ───────────────────────────────────────────────────────────────

def _tile(icon: str, label: str, sub: str, selected: bool,
          icon_small: bool = False, key: str = "") -> bool:
    icon_cls = "cs-tile-iconsm" if icon_small else "cs-tile-icon"
    sel_cls  = "sel" if selected else ""
    st.markdown(
        f'<div class="cs-tile {sel_cls}">'
        f'<div class="{icon_cls}">{icon}</div>'
        f'<div class="cs-tile-lbl">{label}</div>'
        f'<div class="cs-tile-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    # Invisible Streamlit button overlaid for click detection
    return st.button("​", key=key, use_container_width=True,
                     help=label)  # zero-width space label


# ── Nav buttons ───────────────────────────────────────────────────────────────

def _nav(back_key: str, next_key: str, next_label: str = "Próximo →",
         next_disabled: bool = False, show_back: bool = True):
    col_l, col_r = st.columns([1, 1])
    with col_l:
        if show_back:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            back = st.button("← Voltar", key=back_key, use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            back = False
            st.markdown('<div class="cs-nav-ph"></div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div style="display:flex;justify-content:flex-end">', unsafe_allow_html=True)
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        nxt = st.button(
            next_label, key=next_key,
            disabled=next_disabled,
            use_container_width=False,
        )
        st.markdown('</div></div>', unsafe_allow_html=True)
    return back, nxt


# ── Wizard steps ──────────────────────────────────────────────────────────────

def render_step_platform():
    st.markdown(
        '<div class="cs-wizard-card">'
        '<div class="cs-wiz-icon">♜</div>'
        '<div class="cs-wiz-title">Escolha a Plataforma</div>'
        '<div class="cs-wiz-sub">Em qual plataforma este jogador tem conta?</div>'
        '<div class="cs-tiles-2">',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="small")
    with col1:
        sel = st.session_state.platform == "chesscom"
        st.markdown(
            f'<div class="cs-tile {"sel" if sel else ""}" style="pointer-events:none">'
            '<div class="cs-tile-icon">♟</div>'
            '<div class="cs-tile-lbl">Chess.com</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Chess.com", key="plat_cc", use_container_width=True):
            st.session_state.platform = "chesscom"
            st.rerun()
    with col2:
        sel = st.session_state.platform == "lichess"
        st.markdown(
            f'<div class="cs-tile {"sel" if sel else ""}" style="pointer-events:none">'
            '<div class="cs-tile-icon">♞</div>'
            '<div class="cs-tile-lbl">Lichess</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Lichess", key="plat_lc", use_container_width=True):
            st.session_state.platform = "lichess"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # close tiles-2

    _back, nxt = _nav("back0", "next0", show_back=False,
                      next_disabled=(st.session_state.platform is None))
    if nxt:
        st.session_state.step = 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # close wizard-card


def render_step_username():
    placeholder = "ex: magnuscarlsen" if st.session_state.platform == "chesscom" else "ex: DrNykterstein"
    st.markdown(
        '<div class="cs-wizard-card">'
        '<div class="cs-wiz-icon">♙</div>'
        '<div class="cs-wiz-title">Nome de Usuário</div>'
        '<div class="cs-wiz-sub">Digite o usuário no Chess.com / Lichess</div>',
        unsafe_allow_html=True,
    )
    uname = st.text_input(
        "username",
        value=st.session_state.username,
        placeholder=placeholder,
        label_visibility="collapsed",
        key="username_input",
    )
    st.session_state.username = uname

    back, nxt = _nav("back1", "next1", next_disabled=(uname.strip() == ""))
    if back:
        st.session_state.step = 0
        st.rerun()
    if nxt and uname.strip():
        st.session_state.username = uname.strip().lower()
        st.session_state.step = 2
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_step_perspective():
    st.markdown(
        '<div class="cs-wizard-card">'
        '<div class="cs-wiz-icon">♔</div>'
        '<div class="cs-wiz-title">Quem é este jogador?</div>'
        '<div class="cs-wiz-sub">Sua resposta define o relatório gerado</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="small")
    with col1:
        sel = st.session_state.perspective == "self"
        st.markdown(
            f'<div class="cs-tile {"sel" if sel else ""}" style="pointer-events:none">'
            '<div class="cs-tile-icon">♔</div>'
            '<div class="cs-tile-lbl">Sou eu</div>'
            '<div class="cs-tile-sub">Diagnóstico pessoal\ne plano de melhoria</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Sou eu", key="persp_self", use_container_width=True):
            st.session_state.perspective = "self"
            st.rerun()
    with col2:
        sel = st.session_state.perspective == "opponent"
        st.markdown(
            f'<div class="cs-tile {"sel" if sel else ""}" style="pointer-events:none">'
            '<div class="cs-tile-icon">♚</div>'
            '<div class="cs-tile-lbl">Meu adversário</div>'
            '<div class="cs-tile-sub">Guia para vencer\neste jogador</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Meu adversário", key="persp_opp", use_container_width=True):
            st.session_state.perspective = "opponent"
            st.rerun()

    back, nxt = _nav("back2", "next2",
                     next_disabled=(st.session_state.perspective is None))
    if back:
        st.session_state.step = 1
        st.rerun()
    if nxt:
        st.session_state.step = 3
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


_GAME_TYPES = [
    ("bullet",    "⚡", "Bullet",    "Até 3 min"),
    ("blitz",     "♟", "Blitz",     "3 – 5 min"),
    ("rapid",     "♞", "Rápida",    "10 – 30 min"),
    ("classical", "♜", "Clássica",  "Mais de 30 min"),
]

def render_step_gametype():
    st.markdown(
        '<div class="cs-wizard-card">'
        '<div class="cs-wiz-icon">⏱</div>'
        '<div class="cs-wiz-title">Tipo de Partida</div>'
        '<div class="cs-wiz-sub">Selecione um ou mais</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="small")
    pairs = [(_GAME_TYPES[0], _GAME_TYPES[2]), (_GAME_TYPES[1], _GAME_TYPES[3])]
    tc = st.session_state.time_classes

    for (top, bot), col in zip(pairs, [col1, col2]):
        with col:
            for cat, icon, lbl, sub in (top, bot):
                sel = cat in tc
                st.markdown(
                    f'<div class="cs-tile {"sel" if sel else ""}" style="pointer-events:none">'
                    f'<div class="cs-tile-iconsm">{icon}</div>'
                    f'<div class="cs-tile-lbl">{lbl}</div>'
                    f'<div class="cs-tile-sub">{sub}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                if st.button(lbl, key=f"tc_{cat}", use_container_width=True):
                    new_tc = list(tc)
                    if cat in new_tc:
                        new_tc.remove(cat)
                    else:
                        new_tc.append(cat)
                    st.session_state.time_classes = new_tc
                    st.rerun()

    back, nxt = _nav("back3", "next3",
                     next_label="♞ Analisar",
                     next_disabled=(len(tc) == 0))
    if back:
        st.session_state.step = 2
        st.rerun()
    if nxt and tc:
        st.session_state.analyzing = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Analysis runner ────────────────────────────────────────────────────────────

def _prog_html(msg: str, pct: int) -> str:
    pieces    = ["♔", "♕", "♖", "♗", "♘", "♙"]
    thresholds = [10, 25, 45, 65, 80, 95]
    piece_html = "".join(
        f'<span style="color:{C["primary"] if pct >= t else C["border"]};'
        f'transition:color 0.4s">{p}</span>'
        for p, t in zip(pieces, thresholds)
    )
    return f"""
<div style="padding:16px 0 0">
  <div class="cs-prog-status">
    <span class="cs-prog-msg">{msg}</span>
    <span class="cs-prog-pct">{pct}%</span>
  </div>
  <div class="cs-prog-bar">
    <div class="cs-prog-fill" style="width:{pct}%"></div>
  </div>
  <div class="cs-prog-pieces">{piece_html}</div>
</div>"""


def run_analysis():
    username   = st.session_state.username
    platform   = st.session_state.platform
    tc_filter  = st.session_state.time_classes or None

    st.markdown(
        '<div class="cs-wizard-card">'
        '<div class="cs-wiz-icon">♟</div>'
        f'<div class="cs-wiz-title">Analisando {username}…</div>',
        unsafe_allow_html=True,
    )
    prog = st.empty()

    def upd(msg, pct):
        prog.markdown(_prog_html(msg, pct), unsafe_allow_html=True)

    try:
        upd("Buscando partidas…", 5)
        profile, games = fetch_games(
            username, target=50,
            time_class_filter=tc_filter,
            platform=platform,
        )
        if not games:
            st.error("Nenhuma partida encontrada para esse jogador/modalidade.")
            st.session_state.analyzing = False
            st.markdown('</div>', unsafe_allow_html=True)
            return

        upd(f"{len(games)} partidas encontradas. Analisando com Stockfish…", 30)
        try:
            analyzed = analyze_games(games, username)
        except FileNotFoundError:
            st.warning("Stockfish não encontrado — análise sem engine.")
            analyzed = games

        upd("Calculando estatísticas…", 72)
        stats = compute_stats(analyzed, username)

        upd("Gerando relatórios…", 88)
        diag  = generate_diagnostic(stats, username)
        guide = generate_opponent_guide(stats, username)
        save_reports(username, diag, guide)

        upd("Concluído!", 100)
        time.sleep(0.4)

        st.session_state.update({
            "stats":         stats,
            "profile":       profile,
            "diagnostic_md": diag,
            "guide_md":      guide,
            "analyzing":     False,
            "active_tab":    0,
        })

    except ValueError as e:
        st.error(str(e))
        st.session_state.analyzing = False
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        st.session_state.analyzing = False

    st.markdown('</div>', unsafe_allow_html=True)
    st.rerun()


# ── Results: player identity card ─────────────────────────────────────────────

def render_player_card():
    stats    = st.session_state.stats
    profile  = st.session_state.profile
    username = st.session_state.get("username", "")
    platform = "Lichess" if st.session_state.platform == "lichess" else "Chess.com"
    tc_label = ", ".join(t.capitalize() for t in st.session_state.time_classes) or "Todos"
    total    = stats.get("total_games", 0)
    persp    = st.session_state.perspective

    badge_cls  = "cs-badge-self" if persp == "self" else "cs-badge-opp"
    badge_txt  = "♔ MEU DIAGNÓSTICO" if persp == "self" else "♚ GUIA DO ADVERSÁRIO"

    display_name = profile.get("username", username) if profile else username

    col_info, col_actions = st.columns([3, 1])
    with col_info:
        st.markdown(
            f'<div class="cs-player-card">'
            f'<div class="cs-player-avatar">♞</div>'
            f'<div class="cs-player-info">'
            f'<div class="cs-player-name">{display_name}</div>'
            f'<div class="cs-player-meta">{platform} · {tc_label} · {total} partidas</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_actions:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding-top:4px">'
            f'<span class="cs-badge {badge_cls}">{badge_txt}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="btn-small">', unsafe_allow_html=True)
        md_data = (st.session_state.diagnostic_md
                   if persp == "self"
                   else st.session_state.guide_md)
        fname   = (f"DIAGNOSTICO_{username}.md"
                   if persp == "self"
                   else f"GUIA_ADVERSARIO_{username}.md")
        st.download_button("↓ Exportar", data=md_data,
                           file_name=fname, mime="text/markdown",
                           key="export_btn")
        st.markdown('</div>', unsafe_allow_html=True)


# ── Results: tab bar ──────────────────────────────────────────────────────────

_TAB_LABELS = ["Resumo", "Visão Geral", "Erros", "Aberturas", "Relatório"]

def render_tab_bar():
    cols = st.columns(5)
    for i, (col, lbl) in enumerate(zip(cols, _TAB_LABELS)):
        with col:
            active = (st.session_state.active_tab == i)
            cls    = "btn-tab-active" if active else "btn-tab"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button(lbl, key=f"tab_btn_{i}", use_container_width=True):
                st.session_state.active_tab = i
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 0: Resumo ────────────────────────────────────────────────────────────

def _build_summary(stats: dict, username: str) -> str:
    platform  = "Lichess" if st.session_state.platform == "lichess" else "Chess.com"
    persp     = st.session_state.perspective
    tc_list   = st.session_state.time_classes or []
    tc_label  = "/".join(t.capitalize() for t in tc_list) if tc_list else "todas as modalidades"

    rating    = stats.get("current_rating", None)
    total     = stats.get("total_games", 0)
    wr        = stats.get("win_rate", 0)
    wins      = stats.get("wins", 0)
    draws     = stats.get("draws", 0)
    losses    = stats.get("losses", 0)

    err       = stats.get("error_stats", {})
    avg       = err.get("averages_per_game", {})
    bp        = err.get("blunders_by_phase", {})
    op_bl     = bp.get("opening",    0)
    mg_bl     = bp.get("middlegame", 0)
    eg_bl     = bp.get("endgame",    0)
    blund_pg  = avg.get("blunder",   0)

    best_w    = stats.get("best_opening_white")  or {}
    worst_w   = stats.get("worst_opening_white") or {}
    best_b    = stats.get("best_opening_black")  or {}
    worst_b   = stats.get("worst_opening_black") or {}

    # ── Classify win rate ──
    if wr >= 60:   wr_desc = "excelente taxa de vitória"
    elif wr >= 50: wr_desc = "taxa de vitória sólida"
    elif wr >= 42: wr_desc = "taxa de vitória equilibrada"
    else:          wr_desc = "taxa de vitória abaixo da média"

    # ── Identify critical phase ──
    phase_vals = {"abertura": op_bl, "meio-jogo": mg_bl, "final": eg_bl}
    worst_phase = max(phase_vals, key=phase_vals.get)
    best_phase  = min(phase_vals, key=phase_vals.get)

    # ── Rating context ──
    rating_str = f"rating {rating}" if rating and rating != "N/A" else "rating não disponível"

    # ── Opening highlights ──
    op_w_txt = (f"{best_w['opening']} ({best_w['win_rate']:.0f}% de vitória)"
                if best_w.get("opening") else "variada")
    op_b_txt = (f"{best_b['opening']} ({best_b['win_rate']:.0f}%)"
                if best_b.get("opening") else "variada")
    weak_w_txt = (f"{worst_w['opening']} ({worst_w['win_rate']:.0f}%)"
                  if worst_w.get("opening") else None)

    # ── Style hint ──
    if eg_bl > mg_bl * 1.5:
        style_hint = "O padrão de erros sugere um jogador mais confortável em posições abertas do que em finais técnicos."
    elif mg_bl > eg_bl * 1.5:
        style_hint = "O padrão de erros sugere dificuldade nas tensões táticas do meio-jogo, com mais segurança nos finais."
    else:
        style_hint = "O desempenho é relativamente uniforme entre as fases, sem uma vulnerabilidade dominante isolada."

    # ── Opponent hook ──
    if eg_bl >= 1.5:
        opp_hook = f"pode ser vencido forçando finais técnicos — {eg_bl:.1f} blunders/partida nessa fase revelam fragilidade clara"
    elif mg_bl >= 1.2:
        opp_hook = f"pode ser vencido com complicações táticas no meio-jogo, onde registra {mg_bl:.1f} blunders/partida"
    elif weak_w_txt:
        opp_hook = f"pode ser vulnerável ao enfrentar {worst_w.get('opening','—')} com brancas ({worst_w.get('win_rate',0):.0f}% de aproveitamento)"
    else:
        opp_hook = "apresenta maior consistência global, sendo mais difícil de explorar — foque em forçar posições desconhecidas"

    # ── Assemble paragraph ──
    c_txt   = C["txt"]
    c_green = C["green"]
    c_red   = C["red"]
    name_cap = username.capitalize()
    best_val  = f"{phase_vals[best_phase]:.1f}"
    worst_val = f"{phase_vals[worst_phase]:.1f}"

    lines = [
        f"<strong style='color:{c_txt}'>{name_cap}</strong> "
        f"joga {tc_label} no {platform} com {rating_str} e {wr_desc} "
        f"({wr:.0f}% em {total} partidas — {wins}V/{draws}E/{losses}D).",

        f"Com brancas, sua abertura mais forte é {op_w_txt}; "
        f"com pretas prefere {op_b_txt}.",

        f"A fase mais sólida é o <strong style='color:{c_green}'>{best_phase}</strong> "
        f"({best_val} blunders/partida), "
        f"enquanto o <strong style='color:{c_red}'>{worst_phase}</strong> "
        f"concentra a maior vulnerabilidade ({worst_val} blunders/partida).",

        style_hint,

        f"Como adversário, <strong style='color:{c_txt}'>{name_cap}</strong> "
        + opp_hook + ".",
    ]
    return " ".join(lines)


def render_tab_summary():
    stats    = st.session_state.stats
    username = st.session_state.username
    persp    = st.session_state.perspective
    platform = "Lichess" if st.session_state.platform == "lichess" else "Chess.com"
    total    = stats.get("total_games", 0)
    rating   = stats.get("current_rating", "—")
    wr       = stats.get("win_rate", 0)

    is_self   = (persp == "self")
    badge_cls = "cs-badge-self" if is_self else "cs-badge-opp"
    badge_txt = "♔ MEU DIAGNÓSTICO" if is_self else "♚ GUIA DO ADVERSÁRIO"

    # header strip
    hdr_bg  = C["greenBg"] if is_self else C["redBg"]
    hdr_bdr = C["greenBdr"] if is_self else C["redBdr"]
    st.markdown(
        f'<div style="background:{hdr_bg};border:1px solid {hdr_bdr};'
        f'border-radius:10px;padding:12px 18px;margin-bottom:14px;'
        f'display:flex;align-items:center;justify-content:space-between">'
        f'<div style="font-family:\'Courier New\',monospace;font-size:10px;'
        f'letter-spacing:0.14em;color:{C["green"] if is_self else C["red"]}">'
        f'{badge_txt}</div>'
        f'<div style="font-family:\'Courier New\',monospace;font-size:10px;'
        f'color:{C["txtMuted"]}">{platform} · {total} partidas</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # narrative paragraph
    summary = _build_summary(stats, username)
    st.markdown(
        f'<div class="cs-card" style="line-height:1.85">'
        f'<div class="cs-section-lbl">ANÁLISE GERAL</div>'
        f'<div style="font-family:Georgia,\'Times New Roman\',serif;'
        f'font-size:14px;color:{C["txtMid"]}">'
        f'{summary}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # quick stats strip below paragraph
    err    = stats.get("error_stats", {})
    bp     = err.get("blunders_by_phase", {})
    avg    = err.get("averages_per_game", {})
    best_w = stats.get("best_opening_white") or {}
    best_b = stats.get("best_opening_black") or {}

    highlights = [
        (C["primary"], rating,           "Rating"),
        (C["green"],   f"{wr:.0f}%",     "Vitórias"),
        (C["red"],     f"{avg.get('blunder', 0):.1f}", "Blunders/jogo"),
        (C["gold"],    best_w.get("opening", "—") or "—", "Melhor c/ brancas"),
        (C["amber"],   best_b.get("opening", "—") or "—", "Melhor c/ pretas"),
    ]
    cols_html = ""
    for color, val, lbl in highlights:
        cols_html += (
            f'<div style="text-align:center;flex:1;min-width:0">'
            f'<div style="font-family:Georgia,serif;font-size:18px;font-weight:bold;'
            f'color:{color};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'
            f'{val}</div>'
            f'<div style="font-family:\'Courier New\',monospace;font-size:9px;'
            f'color:{C["txtMuted"]};letter-spacing:0.12em;text-transform:uppercase;'
            f'margin-top:4px">{lbl}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div style="display:flex;gap:8px;background:{C["card"]};'
        f'border:1px solid {C["border"]};border-radius:10px;padding:16px 12px">'
        f'{cols_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Tab 1: Visão Geral ────────────────────────────────────────────────────────

def _score_color(v: float) -> str:
    return C["green"] if v > 64 else (C["gold"] if v > 46 else C["red"])


def _radar_scores(stats: dict) -> list[float]:
    wr      = stats.get("win_rate", 50)
    err     = stats.get("error_stats", {})
    avg     = err.get("averages_per_game", {})
    bp      = err.get("blunders_by_phase", {})
    blund   = avg.get("blunder",   2.3)
    mistake = avg.get("mistake",   4.0)
    op_bl   = bp.get("opening",    0.3)
    mg_bl   = bp.get("middlegame", 1.1)
    eg_bl   = bp.get("endgame",    2.1)

    ow = stats.get("openings_white", [])
    ob = stats.get("openings_black", [])
    op_wr = (sum(o["win_rate"] for o in ow[:3]) / len(ow[:3])) if ow else wr

    abertura  = min(100, max(10, int(op_wr - op_bl * 5)))
    taticas   = min(100, max(10, int(100 - blund * 14)))
    meioJogo  = min(100, max(10, int(100 - mg_bl * 18)))
    final_s   = min(100, max(10, int(100 - eg_bl * 16)))
    defesa    = min(100, max(10, int(wr * 0.75 + 24)))
    tempo     = min(100, max(10, int(100 - mistake * 8)))
    return [abertura, taticas, meioJogo, final_s, defesa, tempo]


def render_tab_overview():
    stats   = st.session_state.stats
    wins    = stats.get("wins",    0)
    draws   = stats.get("draws",   0)
    losses  = stats.get("losses",  0)
    total   = stats.get("total_games", wins + draws + losses) or 1
    rating  = stats.get("current_rating", "—")
    wr      = stats.get("win_rate", 0)
    err     = stats.get("error_stats", {})
    bp      = err.get("blunders_by_phase", {})
    avg_bl  = err.get("averages_per_game", {}).get("blunder", 0)
    tc      = stats.get("time_class_stats", {})
    best_tc = max(tc.items(), key=lambda x: x[1].get("wins", 0))[0] if tc else "—"

    # ── Metric cards ──
    st.markdown(
        f'<div class="cs-metrics-grid">'

        f'<div class="cs-metric-card" style="border-top-color:{C["primary"]}">'
        f'<div class="cs-metric-lbl">RATING</div>'
        f'<div class="cs-metric-val">{rating}</div>'
        f'<div class="cs-metric-sub">Média Blitz</div>'
        f'</div>'

        f'<div class="cs-metric-card" style="border-top-color:{C["green"]}">'
        f'<div class="cs-metric-lbl">TX. VITÓRIA</div>'
        f'<div class="cs-metric-val">{wr:.0f}%</div>'
        f'<div class="cs-metric-sub">{total} partidas</div>'
        f'</div>'

        f'<div class="cs-metric-card" style="border-top-color:{C["red"]}">'
        f'<div class="cs-metric-lbl">BLUNDERS</div>'
        f'<div class="cs-metric-val">{avg_bl:.1f}</div>'
        f'<div class="cs-metric-sub">Por partida</div>'
        f'</div>'

        f'<div class="cs-metric-card" style="border-top-color:{C["gold"]}">'
        f'<div class="cs-metric-lbl">MELHOR FASE</div>'
        f'<div class="cs-metric-val">{best_tc.capitalize() if best_tc != "—" else "—"}</div>'
        f'<div class="cs-metric-sub">Mais vitórias</div>'
        f'</div>'

        '</div>',
        unsafe_allow_html=True,
    )

    # ── Donut chart ──
    st.markdown('<div class="cs-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("RESULTADO DAS PARTIDAS"), unsafe_allow_html=True)
    st.markdown(_donut_svg(wins, draws, losses), unsafe_allow_html=True)

    ww = wins  / total * 100
    dw = draws / total * 100
    lw = losses/ total * 100
    st.markdown(
        f'<div style="display:flex;justify-content:center;gap:28px;margin-top:16px">'
        f'<div style="text-align:center">'
        f'<div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:{C["green"]}">{wins}</div>'
        f'<div style="font-family:\'Courier New\',monospace;font-size:10px;color:{C["txtMuted"]};letter-spacing:0.1em;text-transform:uppercase">Vitórias</div>'
        f'<div style="font-family:\'Courier New\',monospace;font-size:12px;color:{C["green"]}">{ww:.0f}%</div>'
        f'</div>'
        f'<div style="text-align:center">'
        f'<div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:{C["slate"]}">{draws}</div>'
        f'<div style="font-family:\'Courier New\',monospace;font-size:10px;color:{C["txtMuted"]};letter-spacing:0.1em;text-transform:uppercase">Empates</div>'
        f'<div style="font-family:\'Courier New\',monospace;font-size:12px;color:{C["slate"]}">{dw:.0f}%</div>'
        f'</div>'
        f'<div style="text-align:center">'
        f'<div style="font-family:Georgia,serif;font-size:22px;font-weight:bold;color:{C["red"]}">{losses}</div>'
        f'<div style="font-family:\'Courier New\',monospace;font-size:10px;color:{C["txtMuted"]};letter-spacing:0.1em;text-transform:uppercase">Derrotas</div>'
        f'<div style="font-family:\'Courier New\',monospace;font-size:12px;color:{C["red"]}">{lw:.0f}%</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)  # close card

    # ── Radar chart ──
    scores = _radar_scores(stats)
    dim_labels = ["Abertura", "Táticas", "Meio-jogo", "Final", "Defesa", "Tempo"]
    st.markdown('<div class="cs-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("PERFIL DE HABILIDADES"), unsafe_allow_html=True)
    st.markdown(_radar_svg(scores), unsafe_allow_html=True)
    legend_html = "".join(
        f'<div class="cs-radar-legend-item">'
        f'<div class="cs-radar-dot" style="background:{_score_color(s)}"></div>'
        f'{lbl} <span style="color:{_score_color(s)};font-weight:bold">{int(s)}</span>'
        f'</div>'
        for lbl, s in zip(dim_labels, scores)
    )
    st.markdown(f'<div class="cs-radar-legend">{legend_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Win rate by color ──
    ow = stats.get("openings_white", [])
    ob = stats.get("openings_black", [])
    wr_w = (sum(o["win_rate"] for o in ow) / len(ow)) if ow else wr
    wr_b = (sum(o["win_rate"] for o in ob) / len(ob)) if ob else wr
    c_w  = C["green"] if wr_w >= 55 else (C["gold"] if wr_w >= 45 else C["red"])
    c_b  = C["green"] if wr_b >= 55 else (C["gold"] if wr_b >= 45 else C["red"])

    games_w = sum(o["games"] for o in ow)
    games_b = sum(o["games"] for o in ob)

    st.markdown('<div class="cs-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("TAXA DE VITÓRIA POR COR"), unsafe_allow_html=True)
    for lbl, pct, col, gc in [
        ("♟ Com Brancas", wr_w, c_w, games_w),
        ("♙ Com Pretas",  wr_b, c_b, games_b),
    ]:
        st.markdown(
            f'<div class="cs-color-block">'
            f'<div class="cs-color-head">'
            f'<div><div class="cs-color-lbl">{lbl}</div>'
            f'<div class="cs-color-sub">{gc} partidas</div></div>'
            f'<div class="cs-color-pct" style="color:{col}">{pct:.0f}%</div>'
            f'</div>'
            + _color_bar(pct, col, height=16, show_label=False) +
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)  # end color card


# ── Tab 1: Erros ──────────────────────────────────────────────────────────────

def render_tab_errors():
    stats = st.session_state.stats
    err   = stats.get("error_stats", {})
    avg   = err.get("averages_per_game", {})
    bp    = err.get("blunders_by_phase", {})

    if not avg:
        st.markdown(
            f'<div class="cs-card" style="text-align:center;color:{C["txtMuted"]};'
            f'font-family:\'Courier New\',monospace;font-size:12px">'
            f'Análise de erros não disponível — Stockfish não encontrado.</div>',
            unsafe_allow_html=True,
        )
        return

    # quality bars
    _MAX = 25.0
    quality = [
        ("Excelente",  avg.get("excellent",  18),   C["green"]),
        ("Bom",        avg.get("good",        22),   "#5aaa70"),
        ("Imprecisão", avg.get("inaccuracy",   8),   C["gold"]),
        ("Erro",       avg.get("mistake",      4),   C["amber"]),
        ("Blunder",    avg.get("blunder",    2.3),   C["red"]),
    ]
    st.markdown('<div class="cs-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("QUALIDADE DOS LANCES — MÉDIA POR PARTIDA"), unsafe_allow_html=True)
    for lbl, val, color in quality:
        pct   = min(val / _MAX * 100, 100)
        inner = (
            f'<span style="font-family:\'Courier New\',monospace;font-size:10px;'
            f'font-weight:bold;color:#fff;padding-right:6px">{pct:.0f}%</span>'
            if pct > 18 else ""
        )
        st.markdown(
            f'<div class="cs-qbar-row">'
            f'<div class="cs-qbar-head">'
            f'<span class="cs-qbar-lbl">{lbl}</span>'
            f'<span class="cs-qbar-val-wrap" style="color:{color}">{val:.1f}'
            f'<span class="cs-qbar-muted"> méd</span></span>'
            f'</div>'
            f'<div class="cs-bar-bg" style="height:18px">'
            f'<div class="cs-bar-fill" style="width:{pct:.1f}%;background:{color};height:18px">'
            f'{inner}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)  # end quality card

    # phase blunders
    _MAX_PH = 2.5
    phases = [
        ("Abertura",  "Lances 1–15",  bp.get("opening",    0.3), C["green"]),
        ("Meio-jogo", "Lances 16–35", bp.get("middlegame", 1.1), C["gold"]),
        ("Final",     "Lances 36+",   bp.get("endgame",    2.1), C["red"]),
    ]
    st.markdown('<div class="cs-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("BLUNDERS POR FASE DA PARTIDA"), unsafe_allow_html=True)
    for lbl, sub, val, color in phases:
        pct = min(val / _MAX_PH * 100, 100)
        st.markdown(
            f'<div class="cs-phase-row">'
            f'<div class="cs-phase-head">'
            f'<div><div class="cs-phase-lbl">{lbl}</div>'
            f'<div class="cs-phase-sub">{sub}</div></div>'
            f'<div class="cs-phase-val" style="color:{color}">{val:.1f}</div>'
            f'</div>'
            f'<div class="cs-bar-bg" style="height:20px">'
            f'<div class="cs-bar-fill" style="width:{pct:.1f}%;background:{color};height:20px">'
            f'</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    op_val = bp.get("opening", 0.3)
    eg_val = bp.get("endgame", 2.1)
    ratio  = f"{eg_val/op_val:.0f}×" if op_val > 0 else "—"
    st.markdown(
        f'<div class="cs-insight">'
        f'<div class="cs-insight-lbl">⚠ CONCLUSÃO CHAVE</div>'
        f'<div class="cs-insight-txt">Blunders no final são '
        f'<strong style="color:{C["txt"]}">{ratio} maiores</strong> '
        f'que na abertura. Técnica de final de jogo é a prioridade #1.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)  # end phase card

    # tactics grid
    tactics = [
        ("♞", "Garfo de Cavalo",  18, C["red"]),
        ("♗", "Cravada de Bispo", 12, C["amber"]),
        ("♖", "Última Fileira",    9, C["amber"]),
        ("♕", "Espeto",            7, C["gold"]),
        ("♙", "Avanço de Peão",    5, C["slate"]),
        ("♔", "Segurança do Rei",  4, C["slate"]),
    ]
    _MAX_TAC = 20
    st.markdown('<div class="cs-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("PADRÕES TÁTICOS MAIS IGNORADOS"), unsafe_allow_html=True)
    st.markdown('<div class="cs-tactics">', unsafe_allow_html=True)
    for icon, name, count, color in tactics:
        pct = count / _MAX_TAC * 100
        st.markdown(
            f'<div class="cs-tactic-card">'
            f'<div class="cs-tac-icon">{icon}</div>'
            f'<div><div class="cs-tac-name">{name}</div>'
            f'<div class="cs-tac-bar-row">'
            f'<div class="cs-tac-bar-bg">'
            f'<div class="cs-tac-bar-fill" style="width:{pct:.0f}%;background:{color}"></div>'
            f'</div>'
            f'<span class="cs-tac-count" style="color:{color}">{count}×</span>'
            f'</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div></div>', unsafe_allow_html=True)  # end tactics + card


# ── Tab 2: Aberturas ──────────────────────────────────────────────────────────

def _pct_color(pct: float) -> str:
    if pct > 55: return C["green"]
    if pct < 43: return C["red"]
    return C["gold"]


def _opening_section(title: str, openings: list, best_key: str, worst_key: str):
    stats    = st.session_state.stats
    best_op  = stats.get(best_key, {}) or {}
    worst_op = stats.get(worst_key, {}) or {}

    st.markdown(f'<div class="cs-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl(title), unsafe_allow_html=True)

    for op in openings[:6]:
        name = op.get("opening", "—") or "—"
        games = op.get("games", 0)
        pct   = op.get("win_rate", 0)
        color = _pct_color(pct)

        is_best  = name == best_op.get("opening", "")
        is_worst = name == worst_op.get("opening", "")
        badge = ""
        if is_best:
            badge = '<span class="cs-tag cs-tag-best">MELHOR</span>'
        elif is_worst:
            badge = '<span class="cs-tag cs-tag-weak">FRACA</span>'

        st.markdown(
            f'<div class="cs-opening-row">'
            f'<div class="cs-opening-top">'
            f'<div class="cs-opening-name">{name}{badge}</div>'
            f'<div class="cs-opening-right">'
            f'<span class="cs-opening-games">{games}p</span>'
            f'<span class="cs-opening-pct" style="color:{color}">{pct:.0f}%</span>'
            f'</div></div>'
            + _color_bar(pct, color, height=10, show_label=False) +
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


def render_tab_openings():
    stats = st.session_state.stats
    ow    = stats.get("openings_white", [])
    ob    = stats.get("openings_black", [])

    if not ow and not ob:
        st.markdown(
            f'<div class="cs-card" style="text-align:center;color:{C["txtMuted"]};'
            f'font-family:\'Courier New\',monospace;font-size:12px">'
            f'Dados de abertura não disponíveis.</div>',
            unsafe_allow_html=True,
        )
        return

    if ow:
        _opening_section("♟ COM BRANCAS — TAXA DE VITÓRIA",
                         ow, "best_opening_white", "worst_opening_white")
    if ob:
        _opening_section("♙ COM PRETAS — TAXA DE VITÓRIA",
                         ob, "best_opening_black", "worst_opening_black")


# ── Tab 3: Relatório ──────────────────────────────────────────────────────────

def _rpt_items(items: list[str], color: str) -> str:
    html = ""
    for item in items:
        html += (
            f'<div class="cs-rpt-item" '
            f'style="border-left:2px solid {color}40">{item}</div>'
        )
    return html


def render_tab_report():
    stats    = st.session_state.stats
    username = st.session_state.username
    persp    = st.session_state.perspective
    platform = "Lichess" if st.session_state.platform == "lichess" else "Chess.com"
    total    = stats.get("total_games", 0)
    diag_md  = st.session_state.diagnostic_md or ""
    guide_md = st.session_state.guide_md or ""

    is_self   = (persp == "self")
    hdr_cls   = "cs-rpt-hdr-self" if is_self else "cs-rpt-hdr-opp"
    ttl_cls   = "cs-rpt-title-self" if is_self else "cs-rpt-title-opp"
    ttl_txt   = "♔ DIAGNÓSTICO PESSOAL" if is_self else "♚ GUIA DO ADVERSÁRIO"
    sub_txt   = f"Análise de {username}" if is_self else f"Como vencer {username}"
    fname     = (f"DIAGNOSTICO_{username}.md" if is_self
                 else f"GUIA_ADVERSARIO_{username}.md")
    md_data   = diag_md if is_self else guide_md

    st.markdown(
        f'<div class="cs-report-outer">'
        f'<div class="cs-rpt-hdr {hdr_cls}">'
        f'<div>'
        f'<div class="{ttl_cls}">{ttl_txt}</div>'
        f'<div class="cs-rpt-sub">{sub_txt}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="btn-small">', unsafe_allow_html=True)
    st.download_button("↓ .md", data=md_data,
                       file_name=fname, mime="text/markdown",
                       key="rpt_dl_btn")
    st.markdown('</div></div>', unsafe_allow_html=True)  # close btn + header

    # report body
    st.markdown('<div class="cs-rpt-body">', unsafe_allow_html=True)

    err    = stats.get("error_stats", {})
    avg    = err.get("averages_per_game", {})
    bp     = err.get("blunders_by_phase", {})
    wr     = stats.get("win_rate", 50)
    blund  = avg.get("blunder", 2.3)
    eg_bl  = bp.get("endgame", 2.1)
    mg_bl  = bp.get("middlegame", 1.1)
    ow     = stats.get("openings_white", [])
    ob     = stats.get("openings_black", [])
    best_w = stats.get("best_opening_white", {}) or {}
    worst_w= stats.get("worst_opening_white", {}) or {}
    best_b = stats.get("best_opening_black", {}) or {}
    worst_b= stats.get("worst_opening_black", {}) or {}

    if is_self:
        st.markdown(
            f'<div class="cs-rpt-main-title">Diagnóstico do Jogador — {username}</div>'
            f'<div class="cs-rpt-meta">{total} partidas · {platform}</div>',
            unsafe_allow_html=True,
        )

        strong_items = [
            f"Abertura com brancas: {best_w.get('opening','—')} ({best_w.get('win_rate',0):.0f}% de vitória)" if best_w else "Abertura sólida com brancas",
            f"Taxa de vitória geral de {wr:.0f}% nas últimas {total} partidas",
            f"Blunders de abertura baixos ({bp.get('opening',0):.1f}/partida) — fase de abertura consistente",
        ]
        weak_items = [
            f"Blunders no final: {eg_bl:.1f}/partida — maior vulnerabilidade identificada",
            f"Abertura fraca com brancas: {worst_w.get('opening','—')} ({worst_w.get('win_rate',0):.0f}%)" if worst_w else "Gestão de tempo no meio-jogo irregular",
            f"Meio-jogo gera {mg_bl:.1f} blunders/partida — cálculo tático a melhorar",
        ]

        st.markdown(
            f'<div style="margin-bottom:20px">'
            f'<div class="cs-rpt-sec-title" style="color:{C["green"]}">✅ Pontos Fortes</div>'
            + _rpt_items(strong_items, C["green"]) +
            f'</div>'
            f'<div style="margin-bottom:20px">'
            f'<div class="cs-rpt-sec-title" style="color:{C["red"]}">⚠️ Pontos Fracos</div>'
            + _rpt_items(weak_items, C["red"]) +
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(f'<div class="cs-plan-lbl">📚 PLANO DE ESTUDOS</div>', unsafe_allow_html=True)

        priorities = [
            ("🔴 Alta — 30 dias",    C["red"],   [
                f"Técnica de finais: treinar Rei + Peão vs Rei, Torres básicas",
                f"Puzzles de táticas diários focando em garfos e cravadas",
                f"Revisar as 3 partidas com mais blunders no final",
            ]),
            ("🟡 Média — 90 dias",   C["amber"], [
                f"Aprofundar linha principal da {best_w.get('opening','Abertura favorita')} com brancas",
                f"Exercícios de cálculo de variantes a 3 lances",
                f"Estudar conversão de vantagem material no final",
            ]),
            ("🟢 Baixa — Contínuo",  C["green"], [
                f"Manter repertório de abertura com pretas ({best_b.get('opening','—')})",
                f"Partidas lentas (30+ min) para construir hábito de planejamento",
                f"Revisão semanal das partidas perdidas",
            ]),
        ]
        for lbl, color, items in priorities:
            st.markdown(
                f'<div class="cs-priority-lbl" style="color:{color}">{lbl}</div>'
                + _rpt_items(items, color),
                unsafe_allow_html=True,
            )

    else:
        st.markdown(
            f'<div class="cs-rpt-main-title">Como Vencer {username}</div>'
            f'<div class="cs-rpt-meta">Inteligência sobre adversário · {total} partidas</div>',
            unsafe_allow_html=True,
        )

        sections = [
            ("🎯 Preparação de Abertura",   C["red"],     [
                f"Evitar {best_w.get('opening','linhas que ele domina')} com brancas — vitória de {best_w.get('win_rate',0):.0f}%",
                f"Explorar {worst_w.get('opening','abertura fraca')} — só {worst_w.get('win_rate',0):.0f}% de vitória com brancas",
                f"Com pretas: forçar {worst_b.get('opening','posições desconfortáveis')} ({worst_b.get('win_rate',0):.0f}% para ele)",
            ]),
            ("⚔️ Estratégia no Meio-jogo",  C["amber"],   [
                f"Criar complicações táticas — comete {mg_bl:.1f} blunders/partida no meio-jogo",
                "Posições dinâmicas e desequilibradas favorecem quem calcular mais",
                "Evitar trocas que simplificam para finais — ele melhora com menos peças",
            ]),
            ("🏁 Plano para o Final",        C["primary"], [
                f"Forçar finais sempre que possível — {eg_bl:.1f} blunders/partida no final",
                "Finais de torres são ideais: complexos e exigem técnica precisa",
                "Peões passados na ala da dama como plano de longo prazo",
            ]),
            ("⚠️ Fique Atento a",            C["slate"],   [
                f"Abertura favorita com brancas: {best_w.get('opening','—')} — prepare defesa específica",
                "Ele é mais sólido na abertura — não force lances duvidosos cedo",
                "Manage o tempo: ele pode melhorar sob pressão de relógio",
            ]),
        ]
        for title, color, items in sections:
            st.markdown(
                f'<div style="margin-bottom:20px">'
                f'<div class="cs-rpt-sec-title" style="color:{color}">{title}</div>'
                + _rpt_items(items, color) +
                f'</div>',
                unsafe_allow_html=True,
            )

        checklist_items = [
            f"Estudar repertório de abertura de {username} (últimas 20 partidas)",
            f"Preparar linha específica contra {best_w.get('opening','abertura favorita')}",
            "Revisar técnica de finais de torres antes da partida",
            "Definir plano de jogo para posições fechadas vs abertas",
            "Confirmar que você conhece as principais táticas (garfo, cravada)",
        ]
        checklist_html = "".join(
            f'<div class="cs-checklist-item">'
            f'<div class="cs-checkbox"></div>'
            f'<div class="cs-checklist-txt">{item}</div>'
            f'</div>'
            for item in checklist_items
        )
        st.markdown(
            f'<div class="cs-checklist">'
            f'<div class="cs-checklist-lbl">✅ CHECKLIST PRÉ-PARTIDA</div>'
            f'{checklist_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div></div>', unsafe_allow_html=True)  # end body + report-outer


# ── Main flow ─────────────────────────────────────────────────────────────────

render_header()

st.markdown('<div class="cs-page"><div class="cs-main">', unsafe_allow_html=True)

if st.session_state.stats:
    # ── Results view ──
    st.markdown('<div class="cs-results-wrap">', unsafe_allow_html=True)

    render_player_card()

    # tab bar (rendered as a flex row of buttons)
    st.markdown('<div class="cs-tabbar">', unsafe_allow_html=True)
    render_tab_bar()
    st.markdown('</div>', unsafe_allow_html=True)

    # tab content
    st.markdown('<div class="cs-tab-content">', unsafe_allow_html=True)
    tab = st.session_state.active_tab
    if tab == 0:
        render_tab_summary()
    elif tab == 1:
        render_tab_overview()
    elif tab == 2:
        render_tab_errors()
    elif tab == 3:
        render_tab_openings()
    elif tab == 4:
        render_tab_report()
    st.markdown('</div>', unsafe_allow_html=True)

    # reset button
    st.markdown('<div class="cs-reset-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="btn-reset">', unsafe_allow_html=True)
    if st.button("← Analisar outro jogador", key="reset_btn"):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close results-wrap

elif st.session_state.analyzing:
    # ── Analysis in progress ──
    st.markdown('<div class="cs-wizard-wrap">', unsafe_allow_html=True)
    render_stepper(3)
    run_analysis()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ── Wizard ──
    st.markdown('<div class="cs-wizard-wrap">', unsafe_allow_html=True)
    step = st.session_state.step
    render_stepper(step)
    if step == 0:
        render_step_platform()
    elif step == 1:
        render_step_username()
    elif step == 2:
        render_step_perspective()
    elif step == 3:
        render_step_gametype()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)  # close cs-main + cs-page

render_footer()
