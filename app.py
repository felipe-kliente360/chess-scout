import streamlit as st
import streamlit.components.v1 as components
import math
import time

from modules.fetcher import fetch_games
from modules.analyzer import analyze_games
from modules.stats import compute_stats
from modules.reporter import generate_diagnostic, generate_opponent_guide, save_reports, md_to_pdf

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chess Scout",
    page_icon="♞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Lang from query param ─────────────────────────────────────────────────────
_qp_lang = st.query_params.get("lang", None)
if _qp_lang in ("pt", "en"):
    st.session_state["lang"] = _qp_lang


# ── Session state defaults ────────────────────────────────────────────────────
_DEFAULTS: dict = {
    "lang":          "pt",
    "step":          0,
    "platform":      "chesscom",
    "username":      "",
    "perspective":   "self",
    "time_classes":  ["blitz"],
    "stats":         None,
    "profile":       None,
    "diagnostic_md": None,
    "guide_md":      None,
    "analyzing":     False,
    "analyze_pct":   0,
    "analyze_msg":   "",
    "analyze_error": "",
    "result_step":   "overview",
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Design tokens — Dossiê ────────────────────────────────────────────────────
DOSSIE: dict = {
    "bg":          "#f3ede0",
    "paper":       "#faf6ec",
    "paperEdge":   "#e7dfcc",
    "ink":         "#1c1a14",
    "inkMid":      "#3a3528",
    "inkMuted":    "#7a6f55",
    "inkFaint":    "#a89d80",
    "border":      "#d5cab0",
    "borderMid":   "#c0b390",
    "red":         "#a8281e",
    "redBg":       "#f3dcd6",
    "redBdr":      "#d4a09a",
    "green":       "#3a6b2a",
    "greenBg":     "#dff0d8",
    "greenBdr":    "#a8d5a0",
    "amber":       "#a8702a",
    "amberBg":     "#f5e8d0",
}

C = DOSSIE

# ── CSS injection ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset Streamlit chrome ────────────────────────────────────────────────── */
#MainMenu, footer, header {{ display:none !important; }}
[data-testid="stSidebar"]       {{ display:none !important; }}
[data-testid="stDecoration"]    {{ display:none !important; }}
[data-testid="stStatusWidget"]  {{ display:none !important; }}
.stDeployButton                 {{ display:none !important; }}
[data-testid="stToolbar"]       {{ display:none !important; }}

/* ── Global ──────────────────────────────────────────────────────────────────── */
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

/* ── Fixed header ─────────────────────────────────────────────────────────── */
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

/* ── Page scaffold ─────────────────────────────────────────────────────────── */
.ds-wizard-wrap  {{ width:100%; max-width:520px; margin:0 auto; padding: 0 4px; }}
.ds-results-wrap {{ width:100%; max-width:880px; margin:0 auto; }}

/* ── Footer ────────────────────────────────────────────────────────────────── */
.ds-footer {{
    border-top: 1px solid {C["border"]};
    padding: 14px 22px; text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: {C["inkFaint"]}; letter-spacing: 0.18em;
    background: {C["bg"]};
}}

/* ── Stepper ───────────────────────────────────────────────────────────────── */
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

/* ── Paper card (wizard + results) ────────────────────────────────────────── */
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

/* ── Tile zone ─────────────────────────────────────────────────────────────── */
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

/* ── Streamlit buttons global ──────────────────────────────────────────────── */
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
[data-testid="stButton"] > button[kind="primary"]:hover {{
    opacity: 0.88 !important;
}}
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

/* Legacy tile backer */
.cs-tile-backer {{
    height: 0 !important; overflow: hidden !important;
    margin: 0 !important; padding: 0 !important;
}}

/* ── Text input ────────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] > div > div {{
    border: none !important; background: transparent !important;
}}
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

/* ── Progress (loading screen) ─────────────────────────────────────────────── */
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

/* ── Player card (results header) ─────────────────────────────────────────── */
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
.ds-badge-self {{ background:{C["paper"]};  border-color:{C["ink"]};   color:{C["ink"]};  }}
.ds-badge-opp  {{ background:{C["redBg"]};  border-color:{C["red"]};   color:{C["red"]};  }}

/* ── Section label ─────────────────────────────────────────────────────────── */
.ds-section-lbl {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase;
    color: {C["inkFaint"]}; margin-bottom: 14px; margin-top: 4px;
    border-bottom: 1px solid {C["paperEdge"]}; padding-bottom: 8px;
}}

/* ── Metric grid ───────────────────────────────────────────────────────────── */
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

/* ── Generic paper section ─────────────────────────────────────────────────── */
.ds-card {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-radius: 4px; padding: 20px 22px; margin-bottom: 12px;
}}

/* ── Color bars ────────────────────────────────────────────────────────────── */
.cs-bar-bg {{
    background: {C["paperEdge"]}; border-radius: 3px;
    overflow: hidden; position: relative;
}}
.cs-bar-fill {{
    height: 100%; border-radius: 3px;
    display: flex; align-items: center; justify-content: flex-end;
    padding-right: 6px; box-sizing: border-box;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 500; color: #fff;
}}

/* ── Opening rows ──────────────────────────────────────────────────────────── */
.cs-opening-row {{ padding:10px 0; border-bottom:1px solid {C["paperEdge"]}; }}
.cs-opening-row:last-child {{ border-bottom:none; }}
.cs-opening-top {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }}
.cs-opening-name {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 13px; color: {C["ink"]};
    display: flex; align-items: center; gap: 6px;
}}
.cs-opening-right {{ display:flex; align-items:center; gap:6px; }}
.cs-opening-games {{
    font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkFaint"]};
}}
.cs-opening-pct {{
    font-family:'Cormorant Garamond',Georgia,serif; font-size:16px; font-weight:600;
}}
.cs-tag {{
    font-family:'JetBrains Mono',monospace; font-size:9px;
    padding:2px 8px; border-radius:2px; border:1px solid;
}}
.cs-tag-best {{ background:{C["greenBg"]}; border-color:{C["greenBdr"]}; color:{C["green"]}; }}
.cs-tag-weak {{ background:{C["redBg"]};   border-color:{C["redBdr"]};   color:{C["red"]};   }}

/* ── Error quality bars ────────────────────────────────────────────────────── */
.cs-qbar-row {{ margin-bottom:12px; }}
.cs-qbar-head {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px; }}
.cs-qbar-lbl {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:13px; color:{C["inkMid"]}; }}
.cs-qbar-val-wrap {{ font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:500; }}
.cs-qbar-muted {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; }}

/* ── Phase bars ────────────────────────────────────────────────────────────── */
.cs-phase-row {{ margin-bottom:16px; }}
.cs-phase-head {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:5px; }}
.cs-phase-lbl {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:14px; color:{C["ink"]}; }}
.cs-phase-sub {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; margin-top:2px; }}
.cs-phase-val {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:22px; font-weight:600; }}

/* ── Insight box ───────────────────────────────────────────────────────────── */
.cs-insight {{
    background:{C["amberBg"]}; border:1px solid {C["amber"]}40;
    border-radius:4px; padding:14px 16px; margin-top:16px;
    border-left: 3px solid {C["amber"]};
}}
.cs-insight-lbl {{
    font-family:'JetBrains Mono',monospace; font-size:10px;
    color:{C["amber"]}; letter-spacing:0.1em; margin-bottom:4px;
}}
.cs-insight-txt {{
    font-family:'Cormorant Garamond',Georgia,serif;
    font-size:14px; color:{C["inkMid"]}; line-height:1.7;
}}

/* ── Tactics grid ──────────────────────────────────────────────────────────── */
.cs-tactics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; }}
.cs-tactic-card {{
    background:{C["paper"]}; border:1px solid {C["paperEdge"]};
    border-radius:4px; padding:14px;
    display:flex; align-items:center; gap:10px;
}}
.cs-tac-icon {{ font-size:24px; flex-shrink:0; }}
.cs-tac-name {{ font-family:'Inter',system-ui; font-size:12px; color:{C["inkMid"]}; margin-bottom:3px; }}
.cs-tac-bar-row {{ display:flex; align-items:center; gap:8px; }}
.cs-tac-bar-bg {{ flex:1; height:5px; background:{C["paperEdge"]}; border-radius:3px; overflow:hidden; }}
.cs-tac-bar-fill {{ height:100%; border-radius:3px; }}
.cs-tac-count {{ font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:500; }}

/* ── Radar legend ──────────────────────────────────────────────────────────── */
.cs-radar-legend {{ display:flex; flex-wrap:wrap; gap:12px; justify-content:center; margin-top:12px; }}
.cs-radar-legend-item {{ display:flex; align-items:center; gap:6px; font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; }}
.cs-radar-dot {{ width:8px; height:8px; border-radius:2px; background:{C["inkMid"]}; opacity:0.4; }}

/* ── Win-rate by color ─────────────────────────────────────────────────────── */
.cs-color-block {{ margin-bottom:16px; }}
.cs-color-head {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:8px; }}
.cs-color-lbl {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:14px; color:{C["ink"]}; }}
.cs-color-sub {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:{C["inkMuted"]}; }}
.cs-color-pct {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:28px; font-weight:700; }}

/* ── Step IV — result detail screens ──────────────────────────────────────── */
.ds-detail-header {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-radius: 4px 4px 0 0;
    padding: 16px 20px;
    display: flex; justify-content: space-between; align-items: center;
    position: relative; overflow: hidden;
}}
.ds-detail-hdr-self {{ border-top: 3px solid {C["ink"]}; }}
.ds-detail-hdr-opp  {{ border-top: 3px solid {C["red"]}; }}
.ds-detail-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase;
}}
.ds-detail-title-self {{ color: {C["ink"]}; }}
.ds-detail-title-opp  {{ color: {C["red"]}; }}
.ds-detail-sub {{
    font-family: 'Inter', system-ui;
    font-size: 11px; color: {C["inkMuted"]}; margin-top: 2px;
}}
.ds-detail-body {{
    background: {C["paper"]}; border: 1px solid {C["paperEdge"]};
    border-top: none; border-radius: 0 0 4px 4px;
    padding: clamp(18px,4vw,28px) clamp(16px,4vw,28px);
    margin-bottom: 14px;
}}

/* Markdown inside report body */
.ds-detail-body h1,.ds-detail-body h2,.ds-detail-body h3 {{
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    color: {C["ink"]} !important; font-weight: 700 !important;
}}
.ds-detail-body h1 {{ font-size: clamp(20px,4vw,26px) !important; border-bottom: 1px solid {C["paperEdge"]}; padding-bottom: 6px; margin-bottom: 12px; }}
.ds-detail-body h2 {{ font-size: clamp(16px,3vw,20px) !important; margin-top: 22px; }}
.ds-detail-body h3 {{ font-size: 14px !important; color: {C["inkMid"]} !important; margin-top: 14px; }}
.ds-detail-body p {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:15px; line-height:1.7; color:{C["inkMid"]}; }}
.ds-detail-body li {{ font-family:'Cormorant Garamond',Georgia,serif; font-size:14px; line-height:1.6; color:{C["inkMid"]}; }}
.ds-detail-body table {{ width:100%; border-collapse:collapse; margin:12px 0; font-size:13px; overflow-x:auto; display:block; }}
.ds-detail-body th {{ font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.1em; background:{C["bg"]}; padding:7px 10px; text-align:left; border:1px solid {C["paperEdge"]}; color:{C["inkMuted"]}; text-transform:uppercase; }}
.ds-detail-body td {{ font-family:'Inter',system-ui; font-size:12px; padding:6px 10px; border:1px solid {C["paperEdge"]}; color:{C["inkMid"]}; }}

/* Stamp CONFIDENCIAL */
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

/* ── ACPL hero ─────────────────────────────────────────────────────────────── */
.ds-acpl-hero {{
    text-align: center; padding: 20px 0 14px;
    border-bottom: 1px solid {C["paperEdge"]}; margin-bottom: 20px;
}}
.ds-acpl-val {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(44px,10vw,64px); font-weight: 700; line-height: 1;
    color: {C["ink"]};
}}
.ds-acpl-lbl {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: {C["inkFaint"]}; letter-spacing: 0.2em;
    text-transform: uppercase; margin-top: 4px;
}}
.ds-acpl-interp {{
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 15px; color: {C["inkMuted"]}; margin-top: 6px; font-style: italic;
}}

/* ── Overview CTA button (Ver relatório) ───────────────────────────────────── */
.ds-cta-wrap {{ text-align: center; padding: 24px 0 8px; }}

/* ── Reset wrap ────────────────────────────────────────────────────────────── */
.cs-reset-wrap {{ display:flex; justify-content:center; margin-top:24px; }}

/* ── Tabs (overview) ───────────────────────────────────────────────────────── */
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
    background:transparent !important;
    border:none !important;
    padding:18px 0 !important;
}}

/* ── Print ─────────────────────────────────────────────────────────────────── */
@media print {{
    .ds-header, .ds-footer, [data-testid="stButton"] {{ display:none !important; }}
    body, .stApp {{ background: white !important; }}
    .ds-detail-body {{ max-height:none !important; }}
}}

/* ── Mobile adjustments (min-width only) ───────────────────────────────────── */
@media (max-width:479px) {{
    .ds-stamp {{ display:none; }}
    .ds-step-name {{ display:none; }}
    .ds-connector {{ width:20px !important; }}
    button[data-baseweb="tab"] {{ font-size:9px !important; padding:0 10px !important; }}
    .cs-tactics {{ grid-template-columns:1fr 1fr !important; }}
    .ds-wiz-sub {{ font-size:12px; }}
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


def _radar_svg(scores: list[float]) -> str:
    cx, cy, R = 110, 110, 80
    labels = ["ABERTURA", "TÁTICAS", "MEIO-JOGO", "FINAL", "DEFESA", "TEMPO"]
    colors = [C["green"] if s > 64 else (C["amber"] if s > 46 else C["red"])
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
    poly = (f'<polygon points="{data_pts}" fill="{C["inkMid"]}" fill-opacity="0.18" '
            f'stroke="{C["inkMid"]}" stroke-width="2"/>')

    # vertex dots & labels
    dots_html = ""
    lbl_html  = ""
    for i, (s, a, lbl, clr) in enumerate(zip(scores, angles, labels, colors)):
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


def _color_bar(pct: float, color: str, height: int = 16, show_label: bool = True) -> str:
    pct = max(0, min(100, pct))
    label = f'<span style="font-family:\'Courier New\',Courier,monospace;font-size:10px;font-weight:bold;color:#fff;padding-right:6px;">{pct:.0f}%</span>' if show_label and pct > 18 else ""
    return (
        f'<div class="cs-bar-bg" style="height:{height}px">'
        f'<div class="cs-bar-fill" style="width:{pct:.1f}%;background:{color};height:{height}px">'
        f'{label}</div></div>'
    )


def _section_lbl(text: str) -> str:
    return f'<div class="ds-section-lbl">{text}</div>'


# ── JS: wire tile clicks to backing buttons ───────────────────────────────────
def _inject_tile_js():
    """Wire .cs-tile divs to the invisible backing st.button (same column) via JS."""
    components.html("""
    <script>
    (function() {
        var doc = window.parent.document;
        function findBtn(tile) {
            // Try column scope first (st.columns wraps each col in [data-testid="column"])
            var col = tile.closest('[data-testid="column"]');
            if (col) {
                var btn = col.querySelector('[data-testid="stButton"] button');
                if (btn) return btn;
            }
            // Fallback: next sibling element-container with button
            var ec = tile.closest('.element-container');
            if (ec && ec.nextElementSibling) {
                var b = ec.nextElementSibling.querySelector('button');
                if (b) return b;
            }
            return null;
        }
        function wireUp() {
            doc.querySelectorAll('.cs-tile:not([data-wired])').forEach(function(tile) {
                var btn = findBtn(tile);
                if (!btn) return;
                tile.setAttribute('data-wired', '1');
                tile.style.cursor = 'pointer';
                tile.addEventListener('click', function(e) {
                    e.preventDefault();
                    btn.click();
                });
            });
        }
        wireUp();
        new MutationObserver(wireUp).observe(doc.body, {childList: true, subtree: true});
    })();
    </script>
    """, height=0)


# ── Header ────────────────────────────────────────────────────────────────────

def render_header():
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


# ── Footer ────────────────────────────────────────────────────────────────────

def render_footer():
    st.markdown(
        '<div class="ds-footer">CHESS SCOUT · STOCKFISH + PYTHON-CHESS</div>',
        unsafe_allow_html=True,
    )


# ── Stepper ───────────────────────────────────────────────────────────────────

_STEP_NAMES = ["Plataforma", "Usuário", "Perspectiva", "Tipo"]

def render_stepper(current: int):
    step  = current
    label = f"PASSO {step + 1} DE 4"
    st.markdown(f'<div class="ds-step-label">{label}</div>', unsafe_allow_html=True)

    nodes_html = ""
    for i, name in enumerate(_STEP_NAMES):
        if i < step:
            circ_cls = "ds-circle-done"
            sym      = "✓"
            name_cls = ""
        elif i == step:
            circ_cls = "ds-circle-active"
            sym      = str(i + 1)
            name_cls = "ds-name-active"
        else:
            circ_cls = "ds-circle-future"
            sym      = str(i + 1)
            name_cls = ""

        conn = ""
        if i < 3:
            conn_cls = "ds-conn-done" if i < step else "ds-conn-pending"
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
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_l:
        if show_back:
            back = st.button("← Voltar", key=back_key, type="secondary",
                             use_container_width=True)
        else:
            back = False
    with col_r:
        nxt = st.button(next_label, key=next_key, type="primary",
                        disabled=next_disabled, use_container_width=True)
    return back, nxt


# ── Wizard steps ──────────────────────────────────────────────────────────────

def render_step_platform():
    plat = st.session_state.platform
    st.markdown(
        '<div class="ds-paper">'
        '<div class="ds-wiz-icon">♜</div>'
        '<div class="ds-wiz-title">Escolha a Plataforma</div>'
        '<div class="ds-wiz-sub">Em qual plataforma este jogador tem conta?</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cs-tile-zone"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if st.button("♟  Chess.com", key="plat_cc",
                     type=("primary" if plat == "chesscom" else "secondary"),
                     use_container_width=True):
            st.session_state.platform = "chesscom"
            st.rerun()
    with col2:
        if st.button("♞  Lichess", key="plat_lc",
                     type=("primary" if plat == "lichess" else "secondary"),
                     use_container_width=True):
            st.session_state.platform = "lichess"
            st.rerun()

    _back, nxt = _nav("back0", "next0", show_back=False,
                      next_disabled=(plat is None))
    if nxt:
        st.session_state.step = 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # close ds-paper


def render_step_username():
    plat_name = "Chess.com" if st.session_state.platform == "chesscom" else "Lichess"
    placeholder = "ex: magnuscarlsen" if st.session_state.platform == "chesscom" else "ex: DrNykterstein"
    st.markdown(
        '<div class="ds-paper">'
        '<div class="ds-wiz-icon">♙</div>'
        '<div class="ds-wiz-title">Nome de Usuário</div>'
        f'<div class="ds-wiz-sub">Digite o usuário no {plat_name}</div>',
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
    st.markdown('</div>', unsafe_allow_html=True)  # close ds-paper


def render_step_perspective():
    persp = st.session_state.perspective
    st.markdown(
        '<div class="ds-paper">'
        '<div class="ds-wiz-icon">♔</div>'
        '<div class="ds-wiz-title">Quem é este jogador?</div>'
        '<div class="ds-wiz-sub">Sua resposta define o relatório gerado</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="cs-tile-zone"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if st.button("♔  Sou eu", key="persp_self",
                     type=("primary" if persp == "self" else "secondary"),
                     use_container_width=True):
            st.session_state.perspective = "self"
            st.rerun()
    with col2:
        if st.button("♚  Adversário", key="persp_opp",
                     type=("primary" if persp == "opponent" else "secondary"),
                     use_container_width=True):
            st.session_state.perspective = "opponent"
            st.rerun()

    back, nxt = _nav("back2", "next2",
                     next_disabled=(persp is None))
    if back:
        st.session_state.step = 1
        st.rerun()
    if nxt:
        st.session_state.step = 3
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # close ds-paper


_GAME_TYPES = [
    ("bullet",    "⚡", "Bullet",    "Até 3 min"),
    ("blitz",     "♟", "Blitz",     "3 – 5 min"),
    ("rapid",     "♞", "Rápida",    "10 – 30 min"),
    ("classical", "♜", "Clássica",  "Mais de 30 min"),
]

def render_step_gametype():
    tc = st.session_state.time_classes
    st.markdown(
        '<div class="ds-paper">'
        '<div class="ds-wiz-icon">⏱</div>'
        '<div class="ds-wiz-title">Tipo de Partida</div>'
        '<div class="ds-wiz-sub">Selecione um ou mais</div>',
        unsafe_allow_html=True,
    )

    rows = [(_GAME_TYPES[0], _GAME_TYPES[1]), (_GAME_TYPES[2], _GAME_TYPES[3])]
    for row_idx, (left, right) in enumerate(rows):
        st.markdown('<div class="cs-tile-zone"></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="medium")
        for (cat, icon, lbl, sub), col in zip((left, right), (c1, c2)):
            with col:
                btn_type = "primary" if cat in tc else "secondary"
                if st.button(f"{icon}  {lbl}", key=f"tc_{cat}",
                             type=btn_type, use_container_width=True):
                    new_tc = list(tc)
                    if cat in new_tc:
                        new_tc.remove(cat)
                    else:
                        new_tc.append(cat)
                    st.session_state.time_classes = new_tc
                    st.rerun()
        if row_idx == 0:
            st.markdown('<div class="cs-tile-row-gap"></div>', unsafe_allow_html=True)

    back, nxt = _nav("back3", "next3",
                     next_label="♞ Analisar",
                     next_disabled=(len(tc) == 0))
    if back:
        st.session_state.step = 2
        st.rerun()
    if nxt and tc:
        st.session_state.analyzing = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)  # close ds-paper


# ── Analysis runner ────────────────────────────────────────────────────────────

_log_lines: list[str] = []

def _prog_html(msg: str, pct: int) -> str:
    pieces    = ["♔", "♕", "♖", "♗", "♘", "♙"]
    thresholds = [10, 25, 45, 65, 80, 95]
    piece_html = "".join(
        f'<span style="color:{C["red"] if pct >= t else C["border"]};'
        f'transition:color 0.4s">{p}</span>'
        for p, t in zip(pieces, thresholds)
    )
    log_html = "".join(f"<div>→ {l}</div>" for l in _log_lines[-8:])
    return f"""
<div class="ds-prog-bar-bg"><div class="ds-prog-bar-fill" style="width:{pct}%"></div></div>
<div class="ds-prog-status">
  <span class="ds-prog-msg">{msg}</span>
  <span class="ds-prog-pct">{pct}%</span>
</div>
<div class="ds-prog-log">{log_html}</div>
<div class="ds-prog-pieces">{piece_html}</div>
"""


def run_analysis():
    global _log_lines
    _log_lines = []

    username  = st.session_state.username
    platform  = st.session_state.platform
    tc_filter = st.session_state.time_classes or None
    tc_label  = ", ".join(t.capitalize() for t in (tc_filter or []))
    plat_name = "Lichess" if platform == "lichess" else "Chess.com"

    st.markdown(
        f'<div class="ds-prog-wrap">'
        f'<div class="ds-prog-title">Analisando {username}…</div>'
        f'<div class="ds-prog-sub">{tc_label} · {plat_name}</div>',
        unsafe_allow_html=True,
    )
    prog = st.empty()

    def upd(msg, pct):
        _log_lines.append(msg)
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
            "result_step":   "overview",
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

    badge_cls  = "ds-badge-self" if persp == "self" else "ds-badge-opp"
    badge_txt  = "♔ DIAGNÓSTICO" if persp == "self" else "♚ ADVERSÁRIO"

    display_name = profile.get("username", username) if profile else username

    st.markdown(
        f'<div class="ds-player-card">'
        f'<div class="ds-player-avatar">♞</div>'
        f'<div class="ds-player-info">'
        f'<div class="ds-player-name">{display_name}</div>'
        f'<div class="ds-player-meta">{platform} · {tc_label} · {total} partidas</div>'
        f'</div>'
        f'<div class="ds-player-actions">'
        f'<span class="ds-badge {badge_cls}">{badge_txt}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Tab: Visão Geral ──────────────────────────────────────────────────────────

def _score_color(v: float) -> str:
    return C["green"] if v > 64 else (C["amber"] if v > 46 else C["red"])


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
    wr      = stats.get("win_rate", 0)

    # ── Donut chart ──
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("RESULTADO DAS PARTIDAS"), unsafe_allow_html=True)
    st.markdown(_donut_svg(wins, draws, losses), unsafe_allow_html=True)

    ww = wins  / total * 100
    dw = draws / total * 100
    lw = losses/ total * 100
    st.markdown(
        f'<div style="display:flex;justify-content:center;gap:28px;margin-top:16px">'
        f'<div style="text-align:center">'
        f'<div style="font-family:\'Cormorant Garamond\',Georgia,serif;font-size:22px;font-weight:bold;color:{C["green"]}">{wins}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{C["inkMuted"]};letter-spacing:0.1em;text-transform:uppercase">Vitórias</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:{C["green"]}">{ww:.0f}%</div>'
        f'</div>'
        f'<div style="text-align:center">'
        f'<div style="font-family:\'Cormorant Garamond\',Georgia,serif;font-size:22px;font-weight:bold;color:{C["inkMuted"]}">{draws}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{C["inkMuted"]};letter-spacing:0.1em;text-transform:uppercase">Empates</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:{C["inkMuted"]}">{dw:.0f}%</div>'
        f'</div>'
        f'<div style="text-align:center">'
        f'<div style="font-family:\'Cormorant Garamond\',Georgia,serif;font-size:22px;font-weight:bold;color:{C["red"]}">{losses}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{C["inkMuted"]};letter-spacing:0.1em;text-transform:uppercase">Derrotas</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:{C["red"]}">{lw:.0f}%</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)  # close card

    # ── Radar chart ──
    scores = _radar_scores(stats)
    dim_labels = ["Abertura", "Táticas", "Meio-jogo", "Final", "Defesa", "Tempo"]
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
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
    c_w  = C["green"] if wr_w >= 55 else (C["amber"] if wr_w >= 45 else C["red"])
    c_b  = C["green"] if wr_b >= 55 else (C["amber"] if wr_b >= 45 else C["red"])

    games_w = sum(o["games"] for o in ow)
    games_b = sum(o["games"] for o in ob)

    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
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


# ── Tab: Erros ────────────────────────────────────────────────────────────────

def render_tab_errors():
    stats = st.session_state.stats
    err   = stats.get("error_stats", {})
    avg   = err.get("averages_per_game", {})
    bp    = err.get("blunders_by_phase", {})

    if not avg:
        st.markdown(
            f'<div class="ds-card" style="text-align:center;color:{C["inkMuted"]};'
            f'font-family:\'JetBrains Mono\',monospace;font-size:12px">'
            f'Análise de erros não disponível — Stockfish não encontrado.</div>',
            unsafe_allow_html=True,
        )
        return

    # quality bars
    _MAX = 25.0
    quality = [
        ("Excelente",  avg.get("excellent",  18),   C["green"]),
        ("Bom",        avg.get("good",        22),   "#5aaa70"),
        ("Imprecisão", avg.get("inaccuracy",   8),   C["amber"]),
        ("Erro",       avg.get("mistake",      4),   C["amber"]),
        ("Blunder",    avg.get("blunder",    2.3),   C["red"]),
    ]
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.markdown(_section_lbl("QUALIDADE DOS LANCES — MÉDIA POR PARTIDA"), unsafe_allow_html=True)
    for lbl, val, color in quality:
        pct   = min(val / _MAX * 100, 100)
        inner = (
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
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
        ("Meio-jogo", "Lances 16–35", bp.get("middlegame", 1.1), C["amber"]),
        ("Final",     "Lances 36+",   bp.get("endgame",    2.1), C["red"]),
    ]
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
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
        f'<strong style="color:{C["ink"]}">{ratio} maiores</strong> '
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
        ("♕", "Espeto",            7, C["amber"]),
        ("♙", "Avanço de Peão",    5, C["inkMuted"]),
        ("♔", "Segurança do Rei",  4, C["inkMuted"]),
    ]
    _MAX_TAC = 20
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
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
    return C["amber"]


def _opening_section(title: str, openings: list, best_key: str, worst_key: str):
    stats    = st.session_state.stats
    best_op  = stats.get(best_key, {}) or {}
    worst_op = stats.get(worst_key, {}) or {}

    st.markdown(f'<div class="ds-card">', unsafe_allow_html=True)
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
            f'<div class="ds-card" style="text-align:center;color:{C["inkMuted"]};'
            f'font-family:\'JetBrains Mono\',monospace;font-size:12px">'
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


# ── Screen III: Overview ─────────────────────────────────────────────────────

def render_screen_overview():
    stats    = st.session_state.stats
    profile  = st.session_state.profile
    username = st.session_state.username
    platform = "Lichess" if st.session_state.platform == "lichess" else "Chess.com"
    tc_label = ", ".join(t.capitalize() for t in st.session_state.time_classes) or "Todos"
    persp    = st.session_state.perspective
    is_self  = (persp == "self")

    wins   = stats.get("wins",   0)
    draws  = stats.get("draws",  0)
    losses = stats.get("losses", 0)
    total  = stats.get("total_games", wins + draws + losses) or 1
    rating = stats.get("current_rating", "—")
    wr     = stats.get("win_rate", 0)
    err    = stats.get("error_stats", {})
    avg    = err.get("averages_per_game", {})
    acpl   = err.get("acpl", 0)
    avg_bl = avg.get("blunder", 0)

    display_name = profile.get("username", username) if profile else username

    # Player card
    badge_cls = "ds-badge-self" if is_self else "ds-badge-opp"
    badge_txt = "♔ DIAGNÓSTICO" if is_self else "♚ ADVERSÁRIO"
    st.markdown(
        f'<div class="ds-player-card">'
        f'<div class="ds-player-avatar">♞</div>'
        f'<div class="ds-player-info">'
        f'<div class="ds-player-name">{display_name}</div>'
        f'<div class="ds-player-meta">{platform} · {tc_label} · {total} partidas</div>'
        f'</div>'
        f'<div class="ds-player-actions">'
        f'<span class="ds-badge {badge_cls}">{badge_txt}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Metrics grid
    st.markdown(
        f'<div class="ds-metrics-grid">'
        f'<div class="ds-metric-card" style="border-top-color:{C["inkFaint"]}">'
        f'<div class="ds-metric-lbl">RATING</div>'
        f'<div class="ds-metric-val">{rating}</div>'
        f'<div class="ds-metric-sub">{tc_label}</div>'
        f'</div>'
        f'<div class="ds-metric-card" style="border-top-color:{C["green"]}">'
        f'<div class="ds-metric-lbl">TX. VITÓRIA</div>'
        f'<div class="ds-metric-val">{wr:.0f}%</div>'
        f'<div class="ds-metric-sub">{total} partidas</div>'
        f'</div>'
        f'<div class="ds-metric-card" style="border-top-color:{C["red"]}">'
        f'<div class="ds-metric-lbl">ACPL</div>'
        f'<div class="ds-metric-val">{acpl:.0f}</div>'
        f'<div class="ds-metric-sub">perda/lance</div>'
        f'</div>'
        f'<div class="ds-metric-card" style="border-top-color:{C["amber"]}">'
        f'<div class="ds-metric-lbl">BLUNDERS</div>'
        f'<div class="ds-metric-val">{avg_bl:.1f}</div>'
        f'<div class="ds-metric-sub">por partida</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Sub-tabs
    _tabs = st.tabs(["Visão Geral", "Erros", "Aberturas"])
    with _tabs[0]:
        render_tab_overview()
    with _tabs[1]:
        render_tab_errors()
    with _tabs[2]:
        render_tab_openings()

    # CTA
    cta_label = "♔ Ver Diagnóstico Pessoal" if is_self else "♚ Ver Plano de Ataque"
    st.markdown('<div class="ds-cta-wrap">', unsafe_allow_html=True)
    if st.button(cta_label, key="cta_detail_btn", type="primary"):
        st.session_state.result_step = "detail"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Screen IV-A: Personal ─────────────────────────────────────────────────────

def render_screen_personal():
    stats    = st.session_state.stats
    username = st.session_state.username
    diag_md  = st.session_state.diagnostic_md or ""
    err      = stats.get("error_stats", {})
    acpl     = err.get("acpl", 0)
    bp       = err.get("blunders_by_phase", {})

    if acpl < 20:   acpl_interp = "Nível master — precisão excepcional"
    elif acpl < 40: acpl_interp = "Jogador avançado — erros controlados"
    elif acpl < 60: acpl_interp = "Nível intermediário — espaço para evolução"
    else:           acpl_interp = "Fase difícil — foco em reduzir erros"

    pdf_bytes = md_to_pdf(diag_md)
    if pdf_bytes:
        dl_data = pdf_bytes; dl_mime = "application/pdf"; fname = f"DIAGNOSTICO_{username}.pdf"
        dl_label = "↓ .pdf"
    else:
        dl_data = (diag_md or "").encode(); dl_mime = "text/markdown"; fname = f"DIAGNOSTICO_{username}.md"
        dl_label = "↓ .md"

    # Header + download
    col_hdr, col_dl = st.columns([5, 1])
    with col_hdr:
        st.markdown(
            '<div class="ds-detail-header ds-detail-hdr-self">'
            '<div>'
            '<div class="ds-detail-title ds-detail-title-self">♔ RELATÓRIO PESSOAL</div>'
            f'<div class="ds-detail-sub">Análise de {username}</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_dl:
        st.download_button(dl_label, data=dl_data, file_name=fname, mime=dl_mime,
                           key="personal_dl_btn")

    # ACPL hero
    st.markdown(
        f'<div class="ds-acpl-hero">'
        f'<div class="ds-acpl-val">{acpl:.0f}</div>'
        f'<div class="ds-acpl-lbl">ACPL — PERDA MÉDIA POR LANCE</div>'
        f'<div class="ds-acpl-interp">{acpl_interp}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Errors by phase
    _MAX_PH = 2.5
    phases = [
        ("Abertura",  "Lances 1–15",  bp.get("opening",    0), C["green"]),
        ("Meio-jogo", "Lances 16–35", bp.get("middlegame", 0), C["amber"]),
        ("Final",     "Lances 36+",   bp.get("endgame",    0), C["red"]),
    ]
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.markdown('<div class="ds-section-lbl">BLUNDERS POR FASE</div>', unsafe_allow_html=True)
    for lbl, sub, val, color in phases:
        pct = min(val / _MAX_PH * 100, 100)
        st.markdown(
            f'<div class="cs-phase-row">'
            f'<div class="cs-phase-head">'
            f'<div><div class="cs-phase-lbl">{lbl}</div>'
            f'<div class="cs-phase-sub">{sub}</div></div>'
            f'<div class="cs-phase-val" style="color:{color}">{val:.1f}</div>'
            f'</div>'
            f'<div class="cs-bar-bg" style="height:16px">'
            f'<div class="cs-bar-fill" style="width:{pct:.1f}%;background:{color};height:16px">'
            f'</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Narrative report
    st.markdown('<div class="ds-detail-body">', unsafe_allow_html=True)
    if diag_md:
        st.markdown(diag_md)
    else:
        st.markdown(
            f'<p style="color:{C["inkMuted"]};font-style:italic">Relatório não gerado.</p>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Back button
    st.markdown('<div class="cs-reset-wrap">', unsafe_allow_html=True)
    if st.button("← Voltar para Visão Geral", key="back_personal", type="secondary"):
        st.session_state.result_step = "overview"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Screen IV-B: Adversary ────────────────────────────────────────────────────

def render_screen_adversary():
    stats    = st.session_state.stats
    username = st.session_state.username
    guide_md = st.session_state.guide_md or ""
    err      = stats.get("error_stats", {})
    bp       = err.get("blunders_by_phase", {})
    ow       = stats.get("openings_white", [])

    pdf_bytes = md_to_pdf(guide_md)
    if pdf_bytes:
        dl_data = pdf_bytes; dl_mime = "application/pdf"; fname = f"GUIA_ADVERSARIO_{username}.pdf"
        dl_label = "↓ .pdf"
    else:
        dl_data = (guide_md or "").encode(); dl_mime = "text/markdown"; fname = f"GUIA_ADVERSARIO_{username}.md"
        dl_label = "↓ .md"

    # Header + stamp + download
    col_hdr, col_dl = st.columns([5, 1])
    with col_hdr:
        st.markdown(
            '<div class="ds-detail-header ds-detail-hdr-opp">'
            '<div>'
            '<div class="ds-detail-title ds-detail-title-opp">♚ PLANO DE ATAQUE</div>'
            f'<div class="ds-detail-sub">Como vencer {username}</div>'
            '</div>'
            '<div class="ds-stamp">CONFIDENCIAL</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_dl:
        st.download_button(dl_label, data=dl_data, file_name=fname, mime=dl_mime,
                           key="adversary_dl_btn")

    # Key intel
    worst_w  = stats.get("worst_opening_white", {}) or {}
    phase_vals = {
        "final":     bp.get("endgame",    0),
        "meio-jogo": bp.get("middlegame", 0),
        "abertura":  bp.get("opening",    0),
    }
    worst_phase     = max(phase_vals, key=phase_vals.get)
    worst_phase_val = phase_vals[worst_phase]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<div class="ds-card">'
            f'<div class="ds-section-lbl">🎯 LINHA DECISIVA</div>'
            f'<div style="font-family:\'Cormorant Garamond\',Georgia,serif;'
            f'font-size:16px;color:{C["red"]};font-weight:700;margin-bottom:5px">'
            f'{worst_w.get("opening", "Posições abertas")}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{C["inkMuted"]}">'
            f'Apenas {worst_w.get("win_rate", 0):.0f}% de vitória com brancas'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="ds-card">'
            f'<div class="ds-section-lbl">⚡ FASE CRÍTICA</div>'
            f'<div style="font-family:\'Cormorant Garamond\',Georgia,serif;'
            f'font-size:16px;color:{C["red"]};font-weight:700;margin-bottom:5px">'
            f'{worst_phase.capitalize()}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{C["inkMuted"]}">'
            f'{worst_phase_val:.1f} blunders/partida — janela de pressão'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Weapons to avoid
    strong_white = [o for o in ow if o.get("win_rate", 0) >= 55][:3]
    if strong_white:
        st.markdown('<div class="ds-card">', unsafe_allow_html=True)
        st.markdown('<div class="ds-section-lbl">🛡 ARMAS A EVITAR — ele domina</div>',
                    unsafe_allow_html=True)
        for op in strong_white:
            wr_op = op.get("win_rate", 0)
            st.markdown(
                f'<div class="cs-opening-row">'
                f'<div class="cs-opening-top">'
                f'<div class="cs-opening-name">{op.get("opening", "—")}</div>'
                f'<div class="cs-opening-right">'
                f'<span class="cs-opening-games">{op.get("games", 0)}p</span>'
                f'<span class="cs-opening-pct" style="color:{C["red"]}">{wr_op:.0f}%</span>'
                f'</div></div>'
                + _color_bar(wr_op, C["red"], height=8, show_label=False) +
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Narrative guide
    st.markdown('<div class="ds-detail-body">', unsafe_allow_html=True)
    if guide_md:
        st.markdown(guide_md)
    else:
        st.markdown(
            f'<p style="color:{C["inkMuted"]};font-style:italic">Guia não gerado.</p>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Back button
    st.markdown('<div class="cs-reset-wrap">', unsafe_allow_html=True)
    if st.button("← Voltar para Visão Geral", key="back_adversary", type="secondary"):
        st.session_state.result_step = "overview"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Main flow ─────────────────────────────────────────────────────────────────

render_header()

if st.session_state.stats:
    # ── Results view ──
    st.markdown('<div class="ds-results-wrap">', unsafe_allow_html=True)

    result_step = st.session_state.get("result_step", "overview")
    if result_step == "detail":
        if st.session_state.perspective == "self":
            render_screen_personal()
        else:
            render_screen_adversary()
    else:
        render_screen_overview()

    # Reset button
    st.markdown('<div class="cs-reset-wrap">', unsafe_allow_html=True)
    if st.button("← Analisar Outro Jogador", key="reset_btn", type="secondary"):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close results-wrap

elif st.session_state.analyzing:
    # ── Analysis in progress ──
    st.markdown('<div class="ds-wizard-wrap">', unsafe_allow_html=True)
    render_stepper(3)
    run_analysis()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ── Wizard ──
    st.markdown('<div class="ds-wizard-wrap">', unsafe_allow_html=True)
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

render_footer()
