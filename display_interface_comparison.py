"""
Display Interface Comparison Tool: OLDI (LVDS) vs eDP  — Light-mode UI
Run with:  streamlit run display_interface_comparison.py

Tested on Windows (Anaconda, fpdf 1.7.2) and macOS.
PDF generation uses fpdf 1.7.2; install via: pip install fpdf
"""

import sys
import math
import io
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
from fpdf import FPDF
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Display Interface eDP and OLDI design tool",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Light-mode CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
.stApp { background-color: #f0f4f8; }

/* ── Sidebar background ── */
[data-testid="stSidebar"] { background-color: #dde2e8; }

/* ── ALL text inside sidebar → dark ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div  { color: #1e3a5f !important; }

/* ── Selectbox dropdown text & selected value ── */
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-baseweb="select"] span,
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] .stSelectbox div { color: #1e293b !important; }

/* ── Number input text ── */
[data-testid="stSidebar"] input[type="number"],
[data-testid="stSidebar"] input { color: #1e293b !important; }

/* ── Radio + toggle labels stay readable ── */
[data-testid="stSidebar"] .stRadio label span { color: #1e3a5f !important; }
[data-testid="stSidebar"] .stToggle label span { color: #1e3a5f !important; }

/* ── Toggle track: OFF state ── */
[data-testid="stSidebar"] .stToggle > label > div:first-child,
[data-testid="stSidebar"] [data-testid="stToggle"] > label > div:first-child,
[data-testid="stSidebar"] [role="checkbox"][aria-checked="false"],
[data-testid="stSidebar"] [data-baseweb="checkbox"] [data-checked="false"] > div,
[data-testid="stSidebar"] label[data-baseweb="checkbox"] > span:first-child {
    background-color: #94a3b8 !important;
    border-color: #94a3b8 !important;
    outline: 2px solid #cbd5e1 !important;
}
/* ── Toggle track: ON state ── */
[data-testid="stSidebar"] [role="checkbox"][aria-checked="true"],
[data-testid="stSidebar"] [data-baseweb="checkbox"] [data-checked="true"] > div {
    background-color: #38bdf8 !important;
    border-color: #38bdf8 !important;
}
/* ── Broad fallback: any small square/circle inside stToggle ── */
[data-testid="stSidebar"] .stToggle span[data-testid="stWidgetLabel"] ~ div,
[data-testid="stSidebar"] .stToggle > label > span:first-of-type {
    background-color: #94a3b8 !important;
    border: 2px solid #cbd5e1 !important;
}

/* ── Metric cards ── */
.metric-card {
    background: #ffffff; border-radius: 10px;
    padding: 14px 18px; margin: 4px 0;
    border-left: 5px solid #2563eb;
    box-shadow: 0 1px 4px rgba(0,0,0,0.10);
}
.metric-card.custom {
    background: #fffbeb;
    border-left-color: #d97706;
    box-shadow: 0 1px 4px rgba(217,119,6,0.18);
}
.metric-label { color: #64748b; font-size: 1.1rem; font-weight: 700;
                text-transform: uppercase; letter-spacing: 0.05em; }
.metric-value { color: #1e3a5f; font-size: 2.6rem; font-weight: 800; margin-top: 4px; }
.metric-sub   { color: #2563eb; font-size: 1.1rem; margin-top: 4px; }
.metric-card.custom .metric-value { color: #92400e; }
.metric-card.custom .metric-sub   { color: #d97706; }
.custom-row-label {
    font-size: 0.78rem; font-weight: 700; color: #d97706;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin: 6px 0 2px 2px;
}

/* ── Badges ── */
.pass-badge { background:#dcfce7; color:#166534; padding:2px 10px;
              border-radius:20px; font-size:0.82rem; font-weight:700;
              border:1px solid #86efac; }
.fail-badge { background:#fee2e2; color:#991b1b; padding:2px 10px;
              border-radius:20px; font-size:0.82rem; font-weight:700;
              border:1px solid #fca5a5; }
.warn-badge { background:#fef3c7; color:#92400e; padding:2px 10px;
              border-radius:20px; font-size:0.82rem; font-weight:700;
              border:1px solid #fde68a; }
.dsc-badge  { background:#ede9fe; color:#5b21b6 !important; padding:2px 10px;
              border-radius:20px; font-size:0.82rem; font-weight:700;
              border:1px solid #c4b5fd; }
.mso-badge  { background:#fef9c3; color:#854d0e !important; padding:2px 10px;
              border-radius:20px; font-size:0.82rem; font-weight:700;
              border:1px solid #fde68a; }
/* badges inside sidebar must override the blanket sidebar colour rule */
[data-testid="stSidebar"] .dsc-badge,
[data-testid="stSidebar"] .dsc-badge * { color:#5b21b6 !important; }
[data-testid="stSidebar"] .mso-badge,
[data-testid="stSidebar"] .mso-badge * { color:#854d0e !important; }

/* ── Section headers ── */
.section-header { border-bottom: 3px solid #2563eb; padding-bottom: 6px;
                  margin-bottom: 16px; color: #1e3a5f; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { font-weight: 600; color: #1e3a5f;
    background-color: #f1f5f9; border: 1px solid #dbe3ec;
    border-radius: 6px; padding: 6px 14px; }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #2563eb; background-color: #e0ebff; border: 1px solid #2563eb;
    font-weight: 800; }
.stTabs [data-baseweb="tab"][aria-selected="true"] p {
    font-weight: 800 !important; }

/* ── Caption ── */
.diagram-caption { color: #64748b; font-size:0.82rem;
                   text-align:center; margin-top:-8px; }

/* ── Headings / body ── */
h1,h2,h3,h4,h5,h6 { color: #1e3a5f; }
p, li { color: #1e293b; }

/* ── Bigger table fonts ── */
[data-testid="stDataFrame"] table   { font-size: 1.3rem !important; }
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th      { font-size: 1.3rem !important;
                                      padding: 10px 16px !important; }
[data-testid="stDataFrame"] thead th { font-size: 1.3rem !important;
                                       font-weight: 700 !important; }

/* ── Left-align st.latex() formulas (KaTeX centers by default) ── */
[data-testid="stMarkdownContainer"] .katex-display,
[data-testid="stMarkdownContainer"] .katex-display > .katex,
[data-testid="stMarkdownContainer"] .katex-display > .katex > .katex-html {
    text-align: left !important;
    justify-content: flex-start !important;
    display: block !important;
}

/* ── Input fields: white background + border so they read as editable controls ── */
.stNumberInput div[data-baseweb="input"],
.stTextInput div[data-baseweb="input"],
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #94a3b8 !important;
    border-radius: 6px !important;
}
.stNumberInput input, .stTextInput input { background-color: #ffffff !important; }
.stNumberInput button { background-color: #f1f5f9 !important; border-color: #94a3b8 !important; }

/* ── "Display Driver IC" tab Calculate button ONLY — no background, bigger font.
       Scoped via the key= "st-key-" class Streamlit attaches to the widget's
       wrapper, so this does NOT affect any other button in the app. ── */
.st-key-tddi_calculate_btn button {
    font-size: 1.3rem !important;
    padding: 0.55rem 1.4rem !important;
    background-color: transparent !important;
    background: transparent !important;
    border-color: #94a3b8 !important;
    color: #1e3a5f !important;
}
.st-key-tddi_calculate_btn button:hover {
    background-color: #f1f5f9 !important;
    border-color: #2563eb !important;
    color: #1e3a5f !important;
}

/* ── Bigger input widget fonts (labels, values, radio, tabs) ── */
[data-testid="stWidgetLabel"] p           { font-size: 1.2rem !important; }
.stNumberInput input, .stTextInput input  { font-size: 1.3rem !important; }
.stRadio label span                       { font-size: 1.2rem !important; }
.stSelectbox div[data-baseweb="select"] * { font-size: 1.2rem !important; }
.stTabs [data-baseweb="tab"] p             { font-size: 1.15rem !important; }

/* ── Bigger, darker caption text (st.caption) ── */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *      { font-size: 1.2rem !important;
                                            color: #0f172a !important;
                                            opacity: 1 !important; }

/* ── Subsection group labels (#### inside columns) ── */
h4 { font-size: 1.25rem !important; }
</style>
""", unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Constants
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
BASE_RESOLUTIONS = {
    "1920×1080  (12.8\")": (1920, 1080, 12.8),
    "2560×1440  (15.6\")": (2560, 1440, 15.6),
    "2880×1620  (17.3\")": (2880, 1620, 17.3),
    "3840×2160  (21.4\")": (3840, 2160, 21.4),
    "6200×1680  (29.1\")": (6200, 1680, 29.1),
}

# 1.62 Gbps (RBR) added
EDP_LINK_RATES = [1.62, 2.7, 3.24, 4.32, 5.4, 8.1]
EDP_RATE_NAMES = {
    1.62: "RBR",  2.7: "HBR1", 3.24: "", 4.32: "", 5.4: "HBR2", 8.1: "HBR3"
}
EDP_RATE_SHORT = [f"{r} Gbps" + (f" ({EDP_RATE_NAMES[r]})" if EDP_RATE_NAMES[r] else "")
                  for r in EDP_LINK_RATES]
LANES_OPTIONS  = [1, 2, 4]
EDP_ENCODING   = 0.8

# DSI 1.2 — up to 2 ports, each up to 4 data lanes
DSI_LANE_RATES   = [0.5, 0.89, 1.0, 1.5, 2.0, 2.5]
DSI_LANES_OPTIONS = [1, 2, 3, 4]
DSI_PORTS_OPTIONS = [1, 2]
DSI_ENCODING     = 1.0   # DSI is byte-oriented, no 8b/10b overhead

MSO_MODES = ["Off", "2×1", "4×1", "2×2"]

DSC_RATIO = {24: 3.0, 30: 3.75}

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Helper functions
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def pixel_clock_hz(h, v, fps, blank_ratio):
    return h * v * fps * (1.0 + blank_ratio)

def oldi_ports_needed(pclk_hz, max_freq_mhz, min_ports):
    return max(min_ports, math.ceil(pclk_hz / (max_freq_mhz * 1e6)))

def oldi_data_pairs(bpp_val):
    return 5 if bpp_val >= 30 else 4

def dsc_eff_bpp(bpp_val, dsc_on):
    if not dsc_on:
        return float(bpp_val)
    return bpp_val / DSC_RATIO.get(bpp_val, 3.0)

def edp_max_active_pixels(lanes, link_gbps, fps_val, eff_bpp_val, blk_ratio=0.0):
    # Link carries full pixel clock (active + blanking).
    # Max active pixels = link_BW / (eff_bpp × fps × (1 + blank_ratio))
    return lanes * link_gbps * 1e9 * EDP_ENCODING / eff_bpp_val / fps_val / (1.0 + blk_ratio)

def dsi_max_active_pixels(lanes, lane_gbps, fps_val, eff_bpp_val, blk_ratio=0.0):
    # DSI link: no 8b/10b overhead (byte-oriented protocol)
    return lanes * lane_gbps * 1e9 * DSI_ENCODING / eff_bpp_val / fps_val / (1.0 + blk_ratio)

def ppi(w, h, diag_in):
    return math.sqrt(w**2 + h**2) / diag_in if diag_in > 0 else 0

def aspect_ratio(w, h):
    g = math.gcd(w, h)
    return f"{w//g}:{h//g}"

def _common_ar_name(aw, ah):
    tbl = {(16,9):"16:9 Widescreen",(4,3):"4:3 Standard",
           (16,10):"16:10 Wide",(21,9):"21:9 Ultrawide",(32,9):"32:9 Super-UW"}
    if (aw, ah) in tbl: return tbl[(aw, ah)]
    r = aw / ah
    if abs(r-16/9)<0.05:  return "≈ 16:9"
    if abs(r-16/10)<0.05: return "≈ 16:10"
    if r > 3.5:            return "Ultra-panoramic"
    if r > 2.5:            return "Ultrawide"
    return f"{aw}:{ah}"

def _ppi_class(p):
    if p >= 220: return "4K / Retina"
    if p >= 160: return "QHD / Hi-DPI"
    if p >= 100: return "FHD / Standard"
    return "HD / Low"

def mso_params(mso_mode):
    """Returns (num_streams, lanes_per_stream, horiz_tiles, vert_tiles).
    N×M notation: N = number of independent video streams,
                  M = physical lanes dedicated to each stream.
    Total lanes required = N × M.
    BW check: lanes_per_stream × link_rate × 0.8 must cover pixels_per_stream.
      2×1 → 2 streams × 1 lane  = 2 total lanes  (L0→stream0, L1→stream1)
      4×1 → 4 streams × 1 lane  = 4 total lanes  (L0…L3 each own stream)
      2×2 → 2 streams × 2 lanes = 4 total lanes  (L0+L1→stream0, L2+L3→stream1)
    """
    return {
        "Off": (1, None, 1, 1),
        "2×1": (2, 1,    2, 1),
        "4×1": (4, 1,    4, 1),
        "2×2": (2, 2,    2, 1),
    }[mso_mode]

def badge(ok):
    return ('<span class="pass-badge">✓ PASS</span>' if ok
            else '<span class="fail-badge">✗ FAIL</span>')

# ── Colour helpers ─────────────────────────────────────────────────────────────
def cs(val):   # status
    s = str(val)
    if "PASS" in s: return "background-color:#dcfce7;color:#166534;font-weight:700"
    if "FAIL" in s: return "background-color:#fee2e2;color:#991b1b;font-weight:700"
    return ""

def ch(val):   # headroom
    try:
        v = float(val)
        if v>20: return "background-color:#dcfce7;color:#166534"
        if v>5:  return "background-color:#fef9c3;color:#854d0e"
        return "background-color:#fee2e2;color:#991b1b"
    except: return ""

def cm(val, total_px):   # max-pixels cell
    try:
        v = float(val)*1e6 / total_px
        if v>=1.10: return "background-color:#dcfce7;color:#166534"
        if v>=1.0:  return "background-color:#f0fdf4;color:#166534"
        if v>=0.9:  return "background-color:#fef9c3;color:#854d0e"
        return "background-color:#fee2e2;color:#991b1b"
    except: return ""

def cmg(val):   # margin
    try:
        v = float(val)
        if v>=10:  return "background-color:#dcfce7;color:#166534"
        if v>=0:   return "background-color:#f0fdf4;color:#166534"
        if v>=-10: return "background-color:#fef9c3;color:#854d0e"
        return "background-color:#fee2e2;color:#991b1b"
    except: return ""

# ── Plotly light-mode palette ──────────────────────────────────────────────────
BG    = "#f8fafc"
PLT   = dict(plot_bgcolor=BG, paper_bgcolor=BG, template="plotly_white",
             font=dict(color="#1e293b", size=14))    # â† global font size up
BOX_SOC   = dict(fillcolor="#dbeafe", line=dict(color="#2563eb", width=2))
BOX_CABLE = dict(fillcolor="#dcfce7", line=dict(color="#16a34a", width=2))
BOX_DISP  = dict(fillcolor="#ede9fe", line=dict(color="#7c3aed", width=2))
BOX_INNER = dict(fillcolor="#f1f5f9", line=dict(color="#94a3b8", width=1))
BOX_LCD   = dict(fillcolor="#d1fae5", line=dict(color="#059669", width=2))
TH = dict(color="#1e3a5f", size=16, family="Arial Black")   # was 13
TM = dict(color="#1e293b", size=14, family="Arial")          # was 12
TS = dict(color="#475569", size=13, family="Arial")          # was 10
TG = dict(color="#b45309", size=12, family="Arial")          # was 9

# Stream colours (used in eDP stream diagram)
STREAM_COLORS = ["#2563eb","#16a34a","#d97706","#7c3aed"]
STREAM_FILLS  = ["#dbeafe","#dcfce7","#fef9c3","#ede9fe"]

def _rect(fig, x0,y0,x1,y1, style):
    fig.add_shape(type="rect",x0=x0,y0=y0,x1=x1,y1=y1,xref="x",yref="y",**style)

def _lbl(fig, x, y, text, font=None, anchor="center"):
    fig.add_annotation(x=x,y=y,text=text,showarrow=False,
                       xref="x",yref="y",font=font or TM,
                       xanchor=anchor,yanchor="middle",align="center")

def _arr(fig, x0,y0,x1,y1, color="#2563eb", label="", dashed=False):
    fig.add_shape(type="line",x0=x0,y0=y0,x1=x1,y1=y1,xref="x",yref="y",
                  line=dict(color=color,width=2,dash="dot" if dashed else "solid"))
    fig.add_annotation(x=x1,y=y1,ax=x0,ay=y0,xref="x",yref="y",axref="x",ayref="y",
                       showarrow=True,arrowhead=3,arrowsize=1.2,
                       arrowwidth=2,arrowcolor=color,text="")
    if label:
        fig.add_annotation(x=(x0+x1)/2,y=(y0+y1)/2+0.17,text=label,
                            showarrow=False,xref="x",yref="y",font=TG,xanchor="center")

def _base_fig(title):
    fig = go.Figure()
    fig.update_layout(height=520,
        title=dict(text=title,font=dict(size=13,color="#1e3a5f")),
        xaxis=dict(visible=False,range=[0,14]),
        yaxis=dict(visible=False,range=[0,8]),
        margin=dict(l=10,r=10,t=52,b=10), **PLT)
    return fig

# ── Block diagram: OLDI ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def draw_oldi(n_ports, cpp_mhz, max_mhz, bpp_val, fps_val=60):
    # Signal path: SOC → Serializer → GMSL3 Channel → OLDI Deserializer
    #              → FPC/Cable → LVDS Bridge IC → LCD Panel
    dp = oldi_data_pairs(bpp_val); tp = dp + 1
    total_pairs = n_ports * tp; total_pins = total_pairs * 2

    fig = go.Figure()
    fig.update_layout(
        height=620,
        title=dict(
            text=(f"OLDI/LVDS Block Diagram  —  {n_ports} port{'s' if n_ports>1 else ''}"
                  f"  ·  {dp}D+1Clk/port  ·  {bpp_val} bpp"),
            font=dict(size=14, color="#1e293b", family="Arial"), x=0.5, xanchor="center"),
        xaxis=dict(visible=False, range=[0, 14]),
        yaxis=dict(visible=False, range=[1.5, 9.5]),
        margin=dict(l=10, r=10, t=52, b=10),
        plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
        template="plotly_white", font=dict(color="#1e293b", size=13))

    # ── Layout constants (mirrors draw_edp) ───────────────────────────────────
    FY0, FY1  = 2.8, 8.3
    GMS_Y0    = 3.8          # GMSL3 channel block bottom (shorter)
    FPC_Y0    = 3.8          # FPC cable block bottom
    FPC_Y1    = 7.0          # FPC cable block top
    CY1       = 7.6          # GMSL3 top
    HDR_H     = 0.62
    AY        = 5.55         # forward arrow y-level
    AUX_Y, AUX_LBL = 4.58, 4.41   # ctrl back-channel arrow
    HPD_Y, HPD_LBL = 4.22, 4.05   # PWM/BL back-channel arrow

    # x-ranges — same 7-column layout as eDP
    soc_x0, soc_x1 = 0.10, 1.85
    ser_x0, ser_x1 = 2.05, 3.65
    gms_x0, gms_x1 = 3.85, 5.05
    des_x0, des_x1 = 5.25, 7.15
    fpc_x0, fpc_x1 = 7.35, 8.30
    brg_x0, brg_x1 = 8.50, 11.05
    lcd_x0, lcd_x1 = 11.25, 13.90

    # ── Local helpers ─────────────────────────────────────────────────────────
    def _cx(x0, x1): return (x0 + x1) / 2

    def _block(x0, y0, x1, y1, body_fill, border_col, hdr_col, title, lines,
               line_step=0.44):
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      xref="x", yref="y",
                      fillcolor=body_fill, line=dict(color=border_col, width=2))
        fig.add_shape(type="rect", x0=x0, y0=y1-HDR_H, x1=x1, y1=y1,
                      xref="x", yref="y",
                      fillcolor=hdr_col, line=dict(color=hdr_col, width=0))
        fig.add_shape(type="line", x0=x0, y0=y1-HDR_H, x1=x1, y1=y1-HDR_H,
                      xref="x", yref="y", line=dict(color=border_col, width=1.0))
        fig.add_annotation(
            x=_cx(x0, x1), y=y1 - HDR_H/2, text=f"<b>{title}</b>",
            showarrow=False, xref="x", yref="y",
            font=dict(color="white", size=13, family="Arial"),
            xanchor="center", yanchor="middle")
        body_top = y1 - HDR_H - 0.18
        for i, (txt, fnt) in enumerate(lines):
            fig.add_annotation(
                x=_cx(x0, x1), y=body_top - line_step * i,
                text=txt, showarrow=False, xref="x", yref="y",
                font=fnt, xanchor="center", yanchor="middle")

    def _signal_arr(x0, x1, color, label=""):
        fig.add_shape(type="line", x0=x0, y0=AY, x1=x1, y1=AY,
                      xref="x", yref="y", line=dict(color=color, width=2.5))
        fig.add_annotation(
            x=x1, y=AY, ax=x0, ay=AY,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3,
            arrowwidth=2.5, arrowcolor=color, text="")
        if label:
            fig.add_annotation(
                x=_cx(x0, x1), y=AY + 0.24, text=f"<b>{label}</b>",
                showarrow=False, xref="x", yref="y",
                font=dict(color=color, size=11, family="Arial"),
                xanchor="center", yanchor="bottom")

    def _dashed_arr(x0, x1, color, label, y_arr, y_lbl, bidir=False):
        fig.add_shape(type="line", x0=x0, y0=y_arr, x1=x1, y1=y_arr,
                      xref="x", yref="y",
                      line=dict(color=color, width=1.8, dash="dot"))
        fig.add_annotation(
            x=x1, y=y_arr, ax=x0, ay=y_arr,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.1,
            arrowwidth=1.8, arrowcolor=color, text="")
        if bidir:
            fig.add_annotation(
                x=x0, y=y_arr, ax=x1, ay=y_arr,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.1,
                arrowwidth=1.8, arrowcolor=color, text="")
        fig.add_annotation(
            x=_cx(x0, x1), y=y_lbl, text=f"<b>{label}</b>",
            showarrow=False, xref="x", yref="y",
            font=dict(color=color, size=11, family="Arial"),
            xanchor="center", yanchor="bottom")

    # ── Font styles ────────────────────────────────────────────────────────────
    FN = dict(color="#334155", size=12, family="Arial")
    FB = dict(color="#1e293b", size=12, family="Arial Black")
    FG = dict(color="#15803d", size=12, family="Arial")
    FO = dict(color="#b45309", size=12, family="Arial")
    FA = dict(color="#0369a1", size=12, family="Arial")
    FP = dict(color="#7c3aed", size=12, family="Arial")

    # ── Display Module outer container (FPC + LVDS Bridge IC + LCD Panel) ──────
    DM_X0  = fpc_x0 - 0.15
    DM_X1  = lcd_x1 + 0.10
    DM_Y0  = FY0    - 0.55
    DM_Y1  = FY1    + 0.55
    DM_LBL = 0.50
    fig.add_shape(type="rect",
                  x0=DM_X0, y0=DM_Y0, x1=DM_X1, y1=DM_Y1,
                  xref="x", yref="y",
                  fillcolor="#f8f0ff",
                  line=dict(color="#7c3aed", width=2.5, dash="dash"))
    fig.add_shape(type="rect",
                  x0=DM_X0, y0=DM_Y1-DM_LBL, x1=DM_X1, y1=DM_Y1,
                  xref="x", yref="y",
                  fillcolor="#7c3aed", line=dict(color="#7c3aed", width=0))
    fig.add_annotation(
        x=_cx(DM_X0, DM_X1), y=DM_Y1 - DM_LBL/2,
        text="<b>DISPLAY MODULE</b>",
        showarrow=False, xref="x", yref="y",
        font=dict(color="white", size=13, family="Arial"),
        xanchor="center", yanchor="middle")

    # ── 1. HOST SoC ────────────────────────────────────────────────────────────
    _block(soc_x0, FY0, soc_x1, FY1,
           "#dbeafe", "#2563eb", "#1e3a5f", "HOST SoC",
           [("Video Source",                    FB),
            (f"{bpp_val} bpp  ·  {fps_val} Hz", FN)])

    # ── 2. Serializer (sky blue, same as deserializer) ─────────────────────────
    _block(ser_x0, FY0, ser_x1, FY1,
           "#e0f2fe", "#0284c7", "#075985", "Serializer",
           [("GMSL3 TX",             FB),
            ("Video → serial",       FN),
            ("PAM4 modulation",      FN),
            ("I²C / GPIO fwd",       FN),
            ("12 Gbps",              FA)])

    # ── 3. GMSL3 Channel (green cable, shorter) ────────────────────────────────
    _block(gms_x0, GMS_Y0, gms_x1, CY1,
           "#dcfce7", "#16a34a", "#166634", "GMSL3<br>Channel",
           [("Coax / STP",  FN),
            ("Up to 15 m",  FG),
            ("12 Gbps",     FG),
            ("Bi-dir ctrl", FG),
            ("Low EMI",     FG)])

    # ── 4. OLDI Deserializer ───────────────────────────────────────────────────
    _block(des_x0, FY0, des_x1, FY1,
           "#e0f2fe", "#0284c7", "#075985", "OLDI Deserializer",
           [("GMSL3 RX",                            FB),
            ("PAM4 demodulation",                   FN),
            (f"OLDI TX · {n_ports} port{'s' if n_ports>1 else ''}", FN),
            (f"{dp}D + 1Clk / port · 7:1 ser.",    FN),
            (f"{cpp_mhz:.1f} MHz / port",           FA),
            (f"Max: {max_mhz} MHz / port",          FA)])

    # ── 5. FPC / Cable (grey, shorter — inside Display Module) ─────────────────
    _block(fpc_x0, FPC_Y0, fpc_x1, FPC_Y1,
           "#f1f5f9", "#94a3b8", "#475569", "FPC<br>Cable",
           [(f"{n_ports}×{tp} pairs",      FN),
            (f"≈ {total_pins}+ sig. pins", FN),
            ("+ Ctrl + Power",             FN),
            ("≤ 0.5 m",                    FG)])

    # ── 6. LVDS Bridge IC ─────────────────────────────────────────────────────
    _block(brg_x0, FY0, brg_x1, FY1,
           "#ede9fe", "#7c3aed", "#4c1d95", "LVDS Bridge IC",
           [("OLDI RX / TCON",              FB),
            (f"Receives {n_ports} port{'s' if n_ports>1 else ''}", FN),
            ("7:1 LVDS deserializer",       FN),
            ("Pixel reassembly",            FN),
            (f"Max: {max_mhz} MHz / port",  FP),
            ("Backlight PWM ctrl",          FN)])

    # ── 7. LCD Panel (dark grey) ───────────────────────────────────────────────
    _block(lcd_x0, FY0, lcd_x1, FY1,
           "#e2e8f0", "#64748b", "#1e293b", "LCD Panel",
           [("TFT Array",             FN),
            ("Source Driver IC",      FN),
            ("Gate Driver IC",        FN),
            ("Backlight (LED strip)", FN),
            ("Pixel data bus",        FG),
            ("PWM backlight ctrl",    FG)])

    # ── Forward signal arrows ──────────────────────────────────────────────────
    _signal_arr(soc_x1, ser_x0, "#d97706", "Video")
    _signal_arr(ser_x1, gms_x0, "#16a34a", "GMSL3")
    _signal_arr(gms_x1, des_x0, "#0284c7", "")
    _signal_arr(des_x1, fpc_x0, "#0284c7", "OLDI")
    _signal_arr(fpc_x1, brg_x0, "#7c3aed", "")
    _signal_arr(brg_x1, lcd_x0, "#059669", "Pixel bus")

    # ── Back-channel arrows (Ctrl/PWM — Bridge IC → Deserializer via FPC) ──────
    _dashed_arr(brg_x0, des_x1, "#b45309", "Ctrl (I²C/GPIO)",
                y_arr=AUX_Y, y_lbl=AUX_LBL, bidir=True)
    _dashed_arr(des_x1, brg_x0, "#dc2626", "PWM (BL)",
                y_arr=HPD_Y, y_lbl=HPD_LBL, bidir=False)

    return fig

# ── Block diagram: eDP ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def draw_edp(n_lanes, link_rate, bpp_val, fps_val, dsc_on, mso_mode):
    eff_bw  = n_lanes * link_rate * EDP_ENCODING
    dsc_lbl = f" + DSC {DSC_RATIO.get(bpp_val,3):.2g}:1" if dsc_on else ""
    mso_lbl = f" · MSO {mso_mode}" if mso_mode != "Off" else ""
    sig_pins = n_lanes * 2 + 3

    fig = go.Figure()
    fig.update_layout(
        height=620,
        title=dict(
            text=(f"eDP Block Diagram  —  {n_lanes}L × {link_rate} Gbps"
                  f"  ·  eff {eff_bw:.2f} Gbps{dsc_lbl}{mso_lbl}"),
            font=dict(size=14, color="#1e293b", family="Arial"), x=0.5, xanchor="center"),
        xaxis=dict(visible=False, range=[0, 14]),
        yaxis=dict(visible=False, range=[1.5, 9.5]),
        margin=dict(l=10, r=10, t=52, b=10),
        plot_bgcolor="#f8fafc", paper_bgcolor="#f8fafc",
        template="plotly_white", font=dict(color="#1e293b", size=13))

    # ── Layout constants ───────────────────────────────────────────────────────
    FY0, FY1   = 2.8, 8.3    # full-height IC blocks
    GMS_Y0     = 3.8          # GMSL channel block bottom (shorter)
    FPC_Y0     = 3.8          # FPC cable block — smaller, same height as GMSL
    FPC_Y1     = 7.0          # FPC cable block top
    CY1        = 7.6          # GMSL top (kept taller than FPC)
    HDR_H      = 0.62         # header band height
    AY         = 5.55         # forward signal arrow y-level
    # Back-channel arrows: inside FPC box (3.80–7.00) & below all text (last=4.88)
    AUX_Y, AUX_LBL = 4.58, 4.41   # arrow line, then label just below
    HPD_Y, HPD_LBL = 4.22, 4.05   # arrow line, then label just below

    # x-ranges (left edge, right edge) for each block
    soc_x0, soc_x1 = 0.10, 1.85
    ser_x0, ser_x1 = 2.05, 3.65
    gms_x0, gms_x1 = 3.85, 5.05
    des_x0, des_x1 = 5.25, 7.15
    fpc_x0, fpc_x1 = 7.35, 8.30
    brg_x0, brg_x1 = 8.50, 11.05
    lcd_x0, lcd_x1 = 11.25, 13.90

    # ── Drawing helpers ────────────────────────────────────────────────────────
    def _cx(x0, x1): return (x0 + x1) / 2

    def _block(x0, y0, x1, y1, body_fill, border_col, hdr_col, title, lines,
               line_step=0.44):
        """Draw a block with a coloured header band and compact fixed-step body lines."""
        # Body rectangle
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      xref="x", yref="y",
                      fillcolor=body_fill,
                      line=dict(color=border_col, width=2))
        # Header band (darker, sits at top)
        fig.add_shape(type="rect", x0=x0, y0=y1-HDR_H, x1=x1, y1=y1,
                      xref="x", yref="y",
                      fillcolor=hdr_col,
                      line=dict(color=hdr_col, width=0))
        # Thin separator below header
        fig.add_shape(type="line", x0=x0, y0=y1-HDR_H, x1=x1, y1=y1-HDR_H,
                      xref="x", yref="y",
                      line=dict(color=border_col, width=1.0))
        # Header title (white text, centred in band)
        fig.add_annotation(
            x=_cx(x0, x1), y=y1 - HDR_H/2,
            text=f"<b>{title}</b>",
            showarrow=False, xref="x", yref="y",
            font=dict(color="white", size=13, family="Arial"),
            xanchor="center", yanchor="middle")
        # Body lines — fixed compact spacing, anchored just below header
        body_top = y1 - HDR_H - 0.18   # small top padding
        for i, (txt, fnt) in enumerate(lines):
            fig.add_annotation(
                x=_cx(x0, x1), y=body_top - line_step * i,
                text=txt, showarrow=False, xref="x", yref="y",
                font=fnt, xanchor="center", yanchor="middle")

    def _signal_arr(x0, x1, color, label=""):
        """Solid forward arrow between two blocks at y=AY."""
        fig.add_shape(type="line", x0=x0, y0=AY, x1=x1, y1=AY,
                      xref="x", yref="y",
                      line=dict(color=color, width=2.5))
        fig.add_annotation(
            x=x1, y=AY, ax=x0, ay=AY,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.3,
            arrowwidth=2.5, arrowcolor=color, text="")
        if label:
            fig.add_annotation(
                x=_cx(x0, x1), y=AY + 0.24,
                text=f"<b>{label}</b>",
                showarrow=False, xref="x", yref="y",
                font=dict(color=color, size=11, family="Arial"),
                xanchor="center", yanchor="bottom")

    def _bidir_arr(x0, x1, color, label, y_arr, y_lbl):
        """Dashed dual-headed arrow (bi-directional signal)."""
        fig.add_shape(type="line", x0=x0, y0=y_arr, x1=x1, y1=y_arr,
                      xref="x", yref="y",
                      line=dict(color=color, width=1.8, dash="dot"))
        for src, dst in [(x1, x0), (x0, x1)]:          # arrowhead on each end
            fig.add_annotation(
                x=dst, y=y_arr, ax=src, ay=y_arr,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.1,
                arrowwidth=1.8, arrowcolor=color, text="")
        fig.add_annotation(
            x=_cx(x0, x1), y=y_lbl,
            text=f"<b>{label}</b>",
            showarrow=False, xref="x", yref="y",
            font=dict(color=color, size=11, family="Arial"),
            xanchor="center", yanchor="bottom")

    def _unidir_arr(x0, x1, color, label, y_arr, y_lbl):
        """Dashed single-headed arrow (right → left)."""
        fig.add_shape(type="line", x0=x0, y0=y_arr, x1=x1, y1=y_arr,
                      xref="x", yref="y",
                      line=dict(color=color, width=1.8, dash="dot"))
        fig.add_annotation(
            x=x1, y=y_arr, ax=x0, ay=y_arr,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=2, arrowsize=1.1,
            arrowwidth=1.8, arrowcolor=color, text="")
        fig.add_annotation(
            x=_cx(x0, x1), y=y_lbl,
            text=f"<b>{label}</b>",
            showarrow=False, xref="x", yref="y",
            font=dict(color=color, size=11, family="Arial"),
            xanchor="center", yanchor="bottom")

    # ── Body text font styles ──────────────────────────────────────────────────
    FN = dict(color="#334155", size=12, family="Arial")           # normal
    FB = dict(color="#1e293b", size=12, family="Arial Black")     # bold accent
    FG = dict(color="#15803d", size=12, family="Arial")           # green metric
    FO = dict(color="#b45309", size=12, family="Arial")           # amber metric
    FA = dict(color="#0369a1", size=12, family="Arial")           # blue metric
    FP = dict(color="#7c3aed", size=12, family="Arial")           # purple (DSC/MSO)

    # ── Block definitions ──────────────────────────────────────────────────────

    # 1. HOST SoC
    soc_lines = [("Video Source",                    FB),
                 (f"{bpp_val} bpp  ·  {fps_val} Hz", FN)]
    if dsc_on:
        soc_lines.append((f"DSC enc {DSC_RATIO.get(bpp_val,3):.2g}:1", FP))
    _block(soc_x0, FY0, soc_x1, FY1,
           "#dbeafe", "#2563eb", "#1e3a5f", "HOST SoC", soc_lines)

    # 2. Serializer  (same colour as eDP Deserializer — sky blue)
    _block(ser_x0, FY0, ser_x1, FY1,
           "#e0f2fe", "#0284c7", "#075985", "Serializer",
           [("GMSL3 TX",          FB),
            ("Video → serial",    FN),
            ("PAM4 modulation",   FN),
            ("I²C / GPIO fwd",    FN),
            ("12 Gbps",           FA)])

    # 3. GMSL3 Channel  (cable block — shorter)
    _block(gms_x0, GMS_Y0, gms_x1, CY1,
           "#dcfce7", "#16a34a", "#166634", "GMSL3<br>Channel",
           [("Coax / STP",  FN),
            ("Up to 15 m",  FG),
            ("12 Gbps",     FG),
            ("Bi-dir ctrl", FG),
            ("Low EMI",     FG)])

    # 4. eDP Deserializer
    des_lines = [("GMSL3 RX",                       FB),
                 ("PAM4 demodulation",               FN),
                 (f"eDP TX · {n_lanes}L @ {link_rate} Gbps", FN),
                 ("8b/10b enc + scramble",           FN),
                 ("Link training FSM",               FN),
                 (f"eff. {eff_bw:.2f} Gbps",        FA)]
    if dsc_on:
        des_lines.append((f"DSC dec {DSC_RATIO.get(bpp_val,3):.2g}:1", FP))
    if mso_mode != "Off":
        _ns_, _lps_, _, _ = mso_params(mso_mode)
        des_lines.append((f"MSO {mso_mode}: {_ns_}×{_lps_} lane", FO))
    _block(des_x0, FY0, des_x1, FY1,
           "#e0f2fe", "#0284c7", "#075985", "eDP Deserializer", des_lines)

    # ── Display Module outer container (drawn first so it sits behind inner blocks) ──
    DM_X0 = fpc_x0 - 0.15
    DM_X1 = lcd_x1 + 0.10
    DM_Y0 = FY0    - 0.55
    DM_Y1 = FY1    + 0.55
    DM_LBL_H = 0.50                       # label band height at top
    # Outer rectangle
    fig.add_shape(type="rect",
                  x0=DM_X0, y0=DM_Y0, x1=DM_X1, y1=DM_Y1,
                  xref="x", yref="y",
                  fillcolor="#f8f0ff",
                  line=dict(color="#7c3aed", width=2.5, dash="dash"))
    # Label band at top
    fig.add_shape(type="rect",
                  x0=DM_X0, y0=DM_Y1 - DM_LBL_H, x1=DM_X1, y1=DM_Y1,
                  xref="x", yref="y",
                  fillcolor="#7c3aed",
                  line=dict(color="#7c3aed", width=0))
    fig.add_annotation(
        x=(DM_X0 + DM_X1) / 2, y=DM_Y1 - DM_LBL_H / 2,
        text="<b>DISPLAY MODULE</b>",
        showarrow=False, xref="x", yref="y",
        font=dict(color="white", size=13, family="Arial"),
        xanchor="center", yanchor="middle")

    # 5. FPC / Cable  (smaller grey box; AUX/HPD arrows pass through its interior)
    _block(fpc_x0, FPC_Y0, fpc_x1, FPC_Y1,
           "#f1f5f9", "#94a3b8", "#475569", "FPC<br>Cable",
           [(f"{n_lanes}×2 data",   FN),
            ("AUX + HPD",          FN),
            (f"= {sig_pins} sig.", FG),
            ("≤ 2 m",              FG)])

    # 6. eDP Bridge IC
    brg_lines = [("eDP RX / TCON",                          FB),
                 (f"eDP sink · {n_lanes} lane{'s' if n_lanes>1 else ''}", FN),
                 ("8b/10b decode + descramble",              FN),
                 ("DPCD registers  ·  PSR",                 FN),
                 (f"eff. {eff_bw:.2f} Gbps",               FP),
                 ("Backlight PWM ctrl",                      FN)]
    _block(brg_x0, FY0, brg_x1, FY1,
           "#ede9fe", "#7c3aed", "#4c1d95", "eDP Bridge IC", brg_lines)

    # 7. LCD Panel  (dark grey)
    _block(lcd_x0, FY0, lcd_x1, FY1,
           "#e2e8f0", "#64748b", "#1e293b", "LCD Panel",
           [("TFT Array",              FN),
            ("Source Driver IC",       FN),
            ("Gate Driver IC",         FN),
            ("Backlight (LED strip)",  FN),
            ("Pixel data bus",         FG),
            ("PWM backlight ctrl",     FG)])

    # ── Forward signal arrows ──────────────────────────────────────────────────
    _signal_arr(soc_x1, ser_x0, "#d97706", "Video")
    _signal_arr(ser_x1, gms_x0, "#16a34a", "GMSL3")
    _signal_arr(gms_x1, des_x0, "#0284c7", "")
    _signal_arr(des_x1, fpc_x0, "#0284c7", "eDP")
    _signal_arr(fpc_x1, brg_x0, "#7c3aed", "")
    _signal_arr(brg_x1, lcd_x0, "#059669", "Pixel bus")

    # ── Back-channel arrows (in clear space below all blocks) ─────────────────
    # AUX: bi-directional, Deserializer ↔ Bridge IC (passes through FPC cable)
    _bidir_arr(des_x1, brg_x0, "#b45309", "AUX (DPCD)",
               y_arr=AUX_Y, y_lbl=AUX_LBL)
    # HPD: Bridge IC → Deserializer (routed through FPC cable)
    _unidir_arr(brg_x0, des_x1, "#dc2626", "HPD",
                y_arr=HPD_Y, y_lbl=HPD_LBL)

    return fig

# ── eDP Streams Architecture diagram ──────────────────────────────────────────
@st.cache_data(show_spinner=False)
def draw_edp_streams(total_lanes, mso_mode_val, h, v, link_rate,
                     fps_val, eff_bpp_val, blk_ratio):
    """Visual showing how physical lanes map to video streams and display tiles."""
    ns, lps, ht, vt = mso_params(mso_mode_val)
    if mso_mode_val == "Off":
        lps = total_lanes   # all lanes → single stream
    tile_w = h // ht;  tile_h = v // vt
    px_per_stream = h * v / ns
    bw_per_stream = lps * link_rate * EDP_ENCODING   # Gbps per stream
    max_px_stream = edp_max_active_pixels(lps, link_rate, fps_val, eff_bpp_val, blk_ratio)

    fig = go.Figure()
    fig.update_layout(
        height=640,
        title=dict(
            text=(f"eDP Stream Architecture — {total_lanes} lanes @ {link_rate} Gbps · "
                  f"MSO {mso_mode_val} · {ns} stream{'s' if ns>1 else ''}"),
            font=dict(size=15, color="#1e3a5f")),
        xaxis=dict(visible=False, range=[0, 14]),
        yaxis=dict(visible=False, range=[0, 10]),
        margin=dict(l=10, r=10, t=58, b=10),
        **PLT)

    # ── 1. Physical link outer box ────────────────────────────────────────
    fig.add_shape(type="rect", x0=0.4, y0=7.5, x1=13.6, y1=9.8,
                  xref="x", yref="y",
                  fillcolor="#dbeafe", line=dict(color="#2563eb", width=2))
    fig.add_annotation(
        x=7, y=9.58,
        text=f"eDP Physical Link  ·  {total_lanes} lane{'s' if total_lanes>1 else ''} @ {link_rate} Gbps  ·  8b/10b eff. = {total_lanes*link_rate*EDP_ENCODING:.2f} Gbps",
        showarrow=False, xref="x", yref="y",
        font=dict(color="#1e3a5f", size=14, family="Arial Black"), xanchor="center")

    # ── 2. Lane boxes ─────────────────────────────────────────────────────
    lane_cx = []   # center-x of each lane box
    lw = min(1.8, 11.0 / total_lanes)
    gap = (11.2 - total_lanes * lw) / (total_lanes + 1)
    for i in range(total_lanes):
        lx0 = 1.4 + gap + i * (lw + gap)
        lx1 = lx0 + lw
        s_idx = (i // lps) if mso_mode_val != "Off" else 0
        sc = STREAM_COLORS[s_idx % 4];  sf = STREAM_FILLS[s_idx % 4]
        fig.add_shape(type="rect", x0=lx0, y0=7.65, x1=lx1, y1=9.35,
                      xref="x", yref="y",
                      fillcolor=sf, line=dict(color=sc, width=2))
        fig.add_annotation(x=(lx0+lx1)/2, y=8.70,
                           text=f"<b>L{i}</b>", showarrow=False,
                           xref="x", yref="y",
                           font=dict(color=sc, size=15, family="Arial Black"),
                           xanchor="center", yanchor="middle")
        lane_cx.append((lx0+lx1)/2)

    # ── 3. Stream boxes ───────────────────────────────────────────────────
    stream_cx = []
    sw = min(3.8, 11.5 / ns)
    sgap = (13.2 - ns * sw) / (ns + 1)
    feasible = max_px_stream >= px_per_stream

    for s in range(ns):
        sx0 = 0.4 + sgap + s * (sw + sgap)
        sx1 = sx0 + sw
        sc = STREAM_COLORS[s % 4];  sf = STREAM_FILLS[s % 4]
        lane_lo = s * lps;  lane_hi = lane_lo + lps - 1
        lane_str = " + ".join(f"L{i}" for i in range(lane_lo, lane_hi + 1))

        fig.add_shape(type="rect", x0=sx0, y0=4.1, x1=sx1, y1=6.9,
                      xref="x", yref="y",
                      fillcolor=sf, line=dict(color=sc, width=2.5))
        cx = (sx0+sx1)/2;  stream_cx.append(cx)

        fig.add_annotation(x=cx, y=6.60, text=f"<b>Stream {s}</b>",
                           showarrow=False, xref="x", yref="y",
                           font=dict(color=sc, size=15, family="Arial Black"), xanchor="center")
        fig.add_annotation(x=cx, y=6.18, text=f"Lanes: {lane_str}",
                           showarrow=False, xref="x", yref="y",
                           font=dict(color="#1e293b", size=13, family="Arial"), xanchor="center")
        fig.add_annotation(x=cx, y=5.74, text=f"Tile: {tile_w} × {tile_h} px",
                           showarrow=False, xref="x", yref="y",
                           font=dict(color="#1e293b", size=13, family="Arial"), xanchor="center")
        fig.add_annotation(x=cx, y=5.28, text=f"BW avail: {bw_per_stream:.3f} Gbps",
                           showarrow=False, xref="x", yref="y",
                           font=dict(color="#b45309", size=13, family="Arial"), xanchor="center")
        fig.add_annotation(x=cx, y=4.82, text=f"Max px: {max_px_stream/1e6:.3f} MP",
                           showarrow=False, xref="x", yref="y",
                           font=dict(color="#b45309", size=13, family="Arial"), xanchor="center")
        status_color = "#166534" if feasible else "#991b1b"
        fig.add_annotation(x=cx, y=4.36,
                           text=f"{'✓ OK' if feasible else '✗ FAIL'}  ({(max_px_stream/px_per_stream-1)*100:+.1f}%)",
                           showarrow=False, xref="x", yref="y",
                           font=dict(color=status_color, size=13, family="Arial Black"),
                           xanchor="center")

    # ── 4. Arrows: lanes → streams ────────────────────────────────────────
    used_lanes = ns * lps
    for i in range(min(total_lanes, used_lanes)):
        s_idx = (i // lps) if mso_mode_val != "Off" else 0
        sc = STREAM_COLORS[s_idx % 4]
        fig.add_annotation(x=stream_cx[s_idx], y=6.9,
                           ax=lane_cx[i], ay=7.65,
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=3, arrowsize=1.3,
                           arrowwidth=2, arrowcolor=sc, text="")

    # ── 5. Display panel ─────────────────────────────────────────────────
    dp_x0,dp_x1,dp_y0,dp_y1 = 0.4, 13.6, 0.3, 3.7
    fig.add_shape(type="rect", x0=dp_x0, y0=dp_y0, x1=dp_x1, y1=dp_y1,
                  xref="x", yref="y",
                  fillcolor="#f8fafc", line=dict(color="#475569", width=2.5))
    fig.add_annotation(x=7, y=3.48,
                       text=f"Display Panel  ·  {h}×{v}  ·  {ns} stream{'s' if ns>1 else ''}",
                       showarrow=False, xref="x", yref="y",
                       font=dict(color="#1e3a5f", size=14, family="Arial Black"),
                       xanchor="center")
    # Tiles proportional to horizontal split
    tile_area_x0 = dp_x0 + 0.15
    tile_area_w  = dp_x1 - dp_x0 - 0.30
    tile_area_y0 = dp_y0 + 0.20
    tile_area_h  = dp_y1 - dp_y0 - 0.75
    for s in range(ns):
        tx0 = tile_area_x0 + s * tile_area_w / ns
        tx1 = tx0 + tile_area_w / ns
        ty0,ty1 = tile_area_y0, tile_area_y0 + tile_area_h
        sc = STREAM_COLORS[s%4];  sf = STREAM_FILLS[s%4]
        fig.add_shape(type="rect", x0=tx0, y0=ty0, x1=tx1, y1=ty1,
                      xref="x", yref="y",
                      fillcolor=sf, line=dict(color=sc, width=2))
        fig.add_annotation(x=(tx0+tx1)/2, y=(ty0+ty1)/2,
                           text=f"<b>S{s}</b><br>{tile_w}×{tile_h}",
                           showarrow=False, xref="x", yref="y",
                           font=dict(color=sc, size=14, family="Arial Black"),
                           xanchor="center", yanchor="middle")

    # ── 6. Arrows: streams → display tiles ───────────────────────────────
    for s in range(ns):
        sc = STREAM_COLORS[s % 4]
        tile_cx = tile_area_x0 + (s + 0.5) * tile_area_w / ns
        fig.add_annotation(x=tile_cx, y=dp_y1,
                           ax=stream_cx[s], ay=4.1,
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=3, arrowsize=1.3,
                           arrowwidth=2, arrowcolor=sc, text="")
    return fig

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PDF Report Generator
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _pdf_safe(text: str) -> str:
    """Replace Unicode characters that Helvetica cannot encode with ASCII equivalents."""
    return (str(text)
        .replace("—", "--").replace("–", "-")   # em/en dash
        .replace("×", "x")                            # multiplication sign
        .replace("²", "2")                            # superscript 2
        .replace("≥", ">=").replace("≤", "<=")   # >= <=
        .replace("≈", "~")                            # approx
        .replace("·", ".")                            # middle dot
        .replace("•", "-")                            # bullet
        .replace("→", "->").replace("←", "<-")  # arrows
        .replace("✓", "OK").replace("✗", "No")  # check/cross
        .replace("’", "'").replace("‘", "'")    # smart single quotes
        .replace(""", '"').replace(""", '"')
        .replace("°", " deg")                         # degree
        .replace("µ", "u")                            # micro
        .replace("Ω", "Ohm")                          # Omega
        .replace("é", "e").replace("è", "e")    # accented e
        .replace("…", "...")                           # ellipsis
        .replace(" ", " ")                            # non-breaking space
        .replace("⅔", "2/3")                          # 2/3 fraction
        # Special display chars
        .replace("❌", "No ").replace("✅", "Yes")
        .replace("✓", "Yes").replace("✗", "No ")
        .replace("×", "x").replace("·", ".")
        .replace("≥", ">=").replace("≤", "<=")
        .replace("≈", "~").replace("²", "2")
        .replace("—", "--").replace("–", "-")
        .replace("I²C", "I2C")
        # Remove any remaining non-latin-1 chars
        .encode("latin-1", "replace").decode("latin-1")
    )

def _pdf_safe_all(d: dict) -> dict:
    return {k: _pdf_safe(v) if isinstance(v, str) else v for k, v in d.items()}


class PDFReport(FPDF):
    """Custom FPDF class with header/footer."""
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(30, 58, 95)
        self.rect(0, 0, 210, 14, "F")
        self.set_text_color(255, 255, 255)
        self.set_xy(8, 3)
        self.cell(0, 8, "Display Interface Comparison Report -- OLDI (LVDS) vs eDP", ln=0)
        self.set_text_color(0, 0, 0)
        self.set_y(self.t_margin)  # reset cursor below header

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 6, f"Generated: {ts}   |   Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(30, 58, 95)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, _pdf_safe(f"  {title}"), ln=True, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def kv_row(self, label, value, shade=False):
        self.set_font("Helvetica", "B", 9)
        if shade:
            self.set_fill_color(240, 244, 248)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(70, 7, _pdf_safe(f"  {label}"), border=1, fill=True)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 7, _pdf_safe(f"  {value}"), border=1, fill=True, ln=True)

    def two_col_row(self, label, val_oldi, val_edp, shade=False):
        if shade:
            self.set_fill_color(240, 244, 248)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        self.cell(70, 7, _pdf_safe(f"  {label}"), border=1, fill=True)
        self.set_font("Helvetica", "", 9)
        oldi_raw = str(val_oldi)
        edp_raw  = str(val_edp)
        oldi_str = _pdf_safe(oldi_raw.replace("", "No: ").replace("✅ ", "Yes: "))
        edp_str  = _pdf_safe(edp_raw .replace("", "No: ").replace("✅ ", "Yes: "))
        if "" in oldi_raw:
            self.set_fill_color(254, 226, 226)
        elif "✅" in oldi_raw:
            self.set_fill_color(220, 252, 231)
        elif shade:
            self.set_fill_color(240, 244, 248)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(62, 7, f"  {oldi_str}", border=1, fill=True)
        if "" in edp_raw:
            self.set_fill_color(254, 226, 226)
        elif "✅" in edp_raw:
            self.set_fill_color(220, 252, 231)
        elif shade:
            self.set_fill_color(240, 244, 248)
        else:
            self.set_fill_color(255, 255, 255)
        self.cell(0, 7, f"  {edp_str}", border=1, fill=True, ln=True)
        self.set_fill_color(255, 255, 255)


def generate_pdf(params: dict) -> bytes:
    """Build and return the PDF as bytes."""
    p  = params
    pdf = PDFReport()
    pdf.set_margins(10, 22, 10)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    # ── 1. Configuration ──────────────────────────────────────────────────────
    pdf.section_title("1. Configuration")
    cfg = [
        ("Resolution",        p["res_label"]),
        ("Diagonal",          f"{p['diag']}\""),
        ("PPI",               f"{p['ppi']:.0f} PPI"),
        ("Aspect Ratio",      p["ar"]),
        ("Pixel Clock",       f"{p['pclk_mhz']:.2f} MHz"),
        ("Active Pixels",     f"{p['mpx']:.2f} MP"),
        ("Video Payload",     f"{p['vpay']:.2f} Gbps"),
        ("Frame Rate",        f"{p['fps']} Hz"),
        ("Bits Per Pixel",    f"{p['bpp']} bpp"),
        ("Blanking Ratio",    f"{p['blank_pct']}%"),
        ("DSC",               f"ON — {p['dsc_ratio']:.2g}:1 → {p['eff_bpp']:.1f} eff. bpp" if p['dsc_on'] else "OFF"),
        ("MSO Mode",          p['mso_mode']),
    ]
    for i, (k, v) in enumerate(cfg):
        pdf.kv_row(k, v, shade=(i % 2 == 0))

    # ── 2. OLDI / LVDS Analysis ───────────────────────────────────────────────
    pdf.section_title("2. OLDI / LVDS Analysis")
    oldi_rows = [
        ("OLDI Ports Required",  str(p["oldi_ports"])),
        ("Data Pairs / Port",    f"{p['dp_per_port']} ({p['bpp']} bpp)"),
        ("Clock Pairs / Port",   "1"),
        ("Total Diff Pairs",     str(p["oldi_ports"] * (p["dp_per_port"] + 1))),
        ("Pixel Clock / Port",   f"{p['pclk_per_port']:.2f} MHz"),
        ("Max Port Frequency",   f"{p['max_oldi_mhz']} MHz"),
        ("Headroom",             f"{(p['max_oldi_mhz'] - p['pclk_per_port']) / p['max_oldi_mhz'] * 100:.1f}%"),
        ("Signal Pins (video)",  f"~{p['oldi_ports'] * (p['dp_per_port'] + 1) * 2} pins"),
    ]
    for i, (k, v) in enumerate(oldi_rows):
        pdf.kv_row(k, v, shade=(i % 2 == 0))

    # ── 3. eDP Analysis ───────────────────────────────────────────────────────
    pdf.section_title("3. eDP Analysis")
    edp_rows = [
        ("Min Lanes",         str(p["best_lanes"]) if p["best_lanes"] else "N/A"),
        ("Link Rate",         f"{p['best_rate']} Gbps" if p["best_rate"] else "N/A"),
        ("Effective BW",      f"{(p['best_lanes'] or 0) * (p['best_rate'] or 0) * 0.8:.2f} Gbps"
                               if p["best_lanes"] else "N/A"),
        ("Eff. BPP (DSC)",    f"{p['eff_bpp']:.1f} bpp"),
        ("Signal Pins",       f"{(p['best_lanes'] or 1)*2+3} pins  "
                               f"({p['best_lanes'] or 1}Lx2 + 2 AUX + 1 HPD)"),
        ("MSO Mode",          p["mso_mode"]),
    ]
    for i, (k, v) in enumerate(edp_rows):
        pdf.kv_row(k, v, shade=(i % 2 == 0))

    # ── 4. eDP Max Active Pixels Table ────────────────────────────────────────
    pdf.section_title("4. eDP Max Active Pixels by Link Config (MP)")
    link_rates = [1.62, 2.7, 3.24, 4.32, 5.4, 8.1]
    lanes_opts = [1, 2, 4]

    col_w = 27
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(30, 58, 95)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(20, 7, "Lanes \\ Gbps", border=1, fill=True)
    for lr in link_rates:
        pdf.cell(col_w, 7, f"{lr} G", border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(0, 0, 0)

    target_mp = p["mpx"]
    for li, lanes in enumerate(lanes_opts):
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(224, 242, 254)
        pdf.cell(20, 7, f"{lanes}L", border=1, fill=True, align="C")
        for lr in link_rates:
            from_edp = lanes * lr * 1e9 * 0.8 / p["eff_bpp"] / p["fps"] / (1 + p["blank_ratio"])
            mp_val = from_edp / 1e6
            feasible = mp_val >= target_mp
            if feasible:
                pdf.set_fill_color(220, 252, 231)
                txt = f"OK {mp_val:.2f}"
            else:
                pdf.set_fill_color(254, 226, 226)
                txt = f"No {mp_val:.2f}"
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(col_w, 7, txt, border=1, fill=True, align="C")
        pdf.ln()

    # ── 5. Interface Comparison Table ─────────────────────────────────────────
    pdf.section_title("5. Interface Feature Comparison")
    dp = oldi_data_pairs(p["bpp"])
    tp = dp + 1
    edp_str = f"{p['best_lanes']}Lx{p['best_rate']}Gbps" if p["best_lanes"] else "N/A"
    feat = [
        ("Standard",            "VESA OpenLDI",                   "VESA eDP"),
        ("Topology",            "Parallel diff. (LVDS)",          "High-speed serial"),
        ("Encoding",            "7:1 LVDS",                       "8b/10b ANSI"),
        ("Data pairs/port",     f"{dp} ({p['bpp']} bpp)",         "N/A (serial lanes)"),
        ("Clock pairs/port",    "1",                              "N/A (embedded clk)"),
        ("Min config",          f"{p['oldi_ports']} ports",       edp_str),
        ("Signal pins (video)", f"~{p['oldi_ports']*tp*2} pins",  f"~{(p['best_lanes'] or 1)*2+3} pins"),
        ("Aux / config",        "I2C / SPI (separate)",           "Built-in AUX (DPCD)"),
        ("Hot plug detect",     "Not native",                  "✅ HPD pin"),
        ("Link training",       "None",                        "✅ Automatic"),
        ("DSC support",         "Not supported",               "✅ eDP 1.4+"),
        ("MSO support",         "Not supported",               "✅ 2x1 / 4x1 / 2x2"),
        ("Panel Self Refresh",  "Not supported",               "✅ PSR / PSR2"),
        ("Adaptive sync",       "Not supported",               "✅ eDP 1.4+"),
        ("EMI profile",         "Higher (parallel bus)",          "Lower (serial + SS)"),
        ("PCB routing",         f"High ({p['oldi_ports']}x{tp} pairs)", "Low (few lanes+AUX)"),
        ("Power management",    "External PMIC + seq.",           "Native DP power states"),
    ]
    # header row
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(30, 58, 95)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(65, 7, "  Feature", border=1, fill=True)
    pdf.cell(60, 7, "  OLDI / LVDS", border=1, fill=True)
    pdf.cell(0,  7, "  eDP",         border=1, fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)
    for i, (label, oldi_v, edp_v) in enumerate(feat):
        pdf.two_col_row(label, oldi_v, edp_v, shade=(i % 2 == 0))

    raw = pdf.output(dest='S')
    if isinstance(raw, str):
        return raw.encode('latin-1')
    return bytes(raw)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Sidebar
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with st.sidebar:
    st.image("analog_devices_logo.png", use_container_width=True)
    st.divider()

    # ── JS: restyle toggle track/thumb so OFF state is clearly visible ──────────
    components.html("""
<script>
(function() {
    function applyToggleStyles() {
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        const toggles = sidebar.querySelectorAll('[data-testid="stToggle"]');
        toggles.forEach(function(tog) {
            const input = tog.querySelector('input[type="checkbox"]');
            if (!input) return;
            const checked = input.checked;
            // Find the track: small-ish element (~36px wide, ~20px tall)
            const els = tog.querySelectorAll('div, span');
            els.forEach(function(el) {
                const r = el.getBoundingClientRect();
                if (r.width > 24 && r.width < 56 && r.height > 10 && r.height < 32) {
                    el.style.setProperty('background-color',
                        checked ? '#38bdf8' : '#94a3b8', 'important');
                    el.style.setProperty('border-color',
                        checked ? '#38bdf8' : '#94a3b8', 'important');
                }
            });
        });
    }
    // Run immediately and re-run on any DOM/attr mutation
    var obs = new MutationObserver(applyToggleStyles);
    obs.observe(window.parent.document.body,
        {subtree: true, childList: true, attributes: true,
         attributeFilter: ['class', 'style', 'checked']});
    // Also poll briefly after load to catch late renders
    setTimeout(applyToggleStyles, 300);
    setTimeout(applyToggleStyles, 800);
    setTimeout(applyToggleStyles, 1800);
})();
</script>
""", height=0)

    # ── Custom resolution ─────────────────────────────────────────────────────
    st.markdown("### ✏️ Custom Resolution")
    use_custom = st.toggle("Add custom resolution", value=False)
    # defaults so variables are always defined
    cw, ch_in, cd = 4460, 1260, 15.0
    if use_custom:
        cw    = st.number_input("Width (px)",    min_value=320,   max_value=15000, value=4460,  step=2)
        ch_in = st.number_input("Height (px)",   min_value=240,   max_value=8000,  value=1260,  step=2)
        cd    = st.number_input("Diagonal (in)", min_value=5.0,   max_value=120.0, value=15.0,  step=0.1)
        RESOLUTIONS = dict(BASE_RESOLUTIONS)
        custom_key  = f"Custom {cw}×{ch_in} ({cd}\")"
        RESOLUTIONS[custom_key] = (int(cw), int(ch_in), float(cd))
    else:
        RESOLUTIONS = dict(BASE_RESOLUTIONS)

    st.divider()
    st.markdown("### 📐 Display Parameters")
    default_idx = len(RESOLUTIONS) - 1 if use_custom else 0
    res_key   = st.selectbox("Resolution", list(RESOLUTIONS.keys()), index=default_idx)
    blank_pct = st.number_input("Total Blanking Ratio (%)", min_value=5, max_value=20,
                         value=10, step=1, format="%d")
    bpp       = st.radio("Bits Per Pixel", [24, 30], horizontal=True,
                         format_func=lambda x: f"{x} bpp")
    fps       = st.radio("Frame Rate", [60, 90], horizontal=True,
                         format_func=lambda x: f"{x} Hz")

    st.divider()
    st.markdown("### 🔵 OLDI / LVDS Settings")
    max_oldi_mhz = st.number_input(
        "Max per-port pixel clock (MHz)",
        min_value=50, max_value=400, value=140, step=10)
    min_ports = st.number_input(
        "Minimum OLDI ports", min_value=2, max_value=8, value=2, step=1)

    st.divider()
    st.markdown("### 🟢 eDP Settings")
    dsc_on      = st.toggle("Enable DSC (Display Stream Compression)", value=False)
    if dsc_on:
        ratio_val = DSC_RATIO.get(bpp, 3.0)
        st.markdown(f'<span class="dsc-badge">DSC {ratio_val}:1 for {bpp} bpp → '
                    f'eff. {bpp/ratio_val:.2f} bpp/px</span>', unsafe_allow_html=True)
    mso_mode    = st.selectbox("MSO Mode", MSO_MODES, index=0,
                               help="Multi-SST Operation splits the eDP link into sub-links")
    if mso_mode != "Off":
        _ns, _lps, _ht, _vt = mso_params(mso_mode)
        _tot = _ns * _lps
        st.markdown(f'<span class="mso-badge">MSO {mso_mode}: {_ns} streams · '
                    f'{_lps} lane/stream · {_tot} total lanes '
                    f'({_ht}H×{_vt}V tiles)</span>', unsafe_allow_html=True)
    edp_show_margin = st.toggle("Show pixel budget margin (%)", value=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Derived values
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
h_act, v_act, diag    = RESOLUTIONS[res_key]
blank_ratio            = blank_pct / 100.0
total_pixels           = h_act * v_act
pclk                   = pixel_clock_hz(h_act, v_act, fps, blank_ratio)
pclk_mhz               = pclk / 1e6
ppi_val                = ppi(h_act, v_act, diag)
ar_str                 = aspect_ratio(h_act, v_act)
g_                     = math.gcd(h_act, v_act)
ar_name                = _common_ar_name(h_act//g_, v_act//g_)

oldi_ports             = oldi_ports_needed(pclk, max_oldi_mhz, min_ports)
pclk_per_port          = pclk_mhz / oldi_ports
oldi_ok                = pclk_per_port <= max_oldi_mhz
dp_per_port            = oldi_data_pairs(bpp)
tp_per_port            = dp_per_port + 1

eff_bpp_val            = dsc_eff_bpp(bpp, dsc_on)
dsc_ratio_val          = DSC_RATIO.get(bpp, 3.0) if dsc_on else 1.0

# MSO params — N×M: N streams, M lanes per stream
ns_mso, lps_mso, ht_mso, vt_mso = mso_params(mso_mode)
# total physical lanes required by this MSO mode
total_lanes_req = (ns_mso * lps_mso) if mso_mode != "Off" else None
# pixels each stream must carry
px_per_stream   = total_pixels / ns_mso

# Min viable eDP config
best_lanes, best_rate = None, None
if mso_mode == "Off":
    # search all LANES_OPTIONS
    for _l in LANES_OPTIONS:
        for _r in EDP_LINK_RATES:
            if edp_max_active_pixels(_l, _r, fps, eff_bpp_val, blank_ratio) >= px_per_stream:
                best_lanes, best_rate = _l, _r; break
        if best_lanes: break
else:
    # lanes_per_stream is fixed by MSO mode; find min link_rate
    best_lanes = total_lanes_req          # total lanes needed
    for _r in EDP_LINK_RATES:
        if edp_max_active_pixels(lps_mso, _r, fps, eff_bpp_val, blank_ratio) >= px_per_stream:
            best_rate = _r; break

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Summary cards
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ── Page title + top-right PDF button (placeholder filled later) ──────────────
_title_col, _pdf_col = st.columns([5, 1])
_title_col.markdown("# 🖥️ Display Interface eDP and OLDI design tool")
_pdf_placeholder = _pdf_col.empty()   # filled at bottom after all vars computed

def mcard(col, label, value, sub="", border="#2563eb", custom=False):
    cls  = "metric-card custom" if custom else "metric-card"
    vsty = "color:#92400e" if custom else "color:#1e3a5f"
    ssty = "color:#d97706" if custom else f"color:{border}"
    col.markdown(
        f'<div class="{cls}" style="border-left-color:{border};">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value" style="{vsty}">{value}</div>'
        f'<div class="metric-sub"   style="{ssty}">{sub}</div>'
        f'</div>', unsafe_allow_html=True)

def _summary_row(h, v, dg, label_prefix="", custom=False):
    """Render one full 7-column summary row for a given resolution."""
    border = "#d97706" if custom else "#2563eb"
    _tp    = h * v
    _pclk  = pixel_clock_hz(h, v, fps, blank_ratio)
    _pclkM = _pclk / 1e6
    _ppi   = ppi(h, v, dg)
    _g     = math.gcd(h, v); _aw, _ah = h//_g, v//_g
    _ar    = f"{_aw}:{_ah}";  _ar_name = _common_ar_name(_aw, _ah)
    _ports = oldi_ports_needed(_pclk, max_oldi_mhz, min_ports)
    _cpp   = _pclkM / _ports
    # min eDP
    _bl, _br = None, None
    if mso_mode == "Off":
        for _l in LANES_OPTIONS:
            for _r in EDP_LINK_RATES:
                if edp_max_active_pixels(_l, _r, fps, eff_bpp_val, blank_ratio) >= _tp / ns_mso:
                    _bl, _br = _l, _r; break
            if _bl: break
    else:
        _bl = total_lanes_req
        for _r in EDP_LINK_RATES:
            if edp_max_active_pixels(lps_mso, _r, fps, eff_bpp_val, blank_ratio) >= _tp / ns_mso:
                _br = _r; break
    dsc_sub = (f"DSC {dsc_ratio_val:.2g}:1 → {eff_bpp_val:.1f} bpp"
               if dsc_on else "DSC disabled")
    dsc_brd = "#7c3aed" if dsc_on else ("#94a3b8" if not custom else "#d97706")

    _vpay  = _pclkM * bpp / 1000          # Video Payload in Gbps

    if custom:
        st.markdown('<p class="custom-row-label">✏️ Custom Resolution</p>',
                    unsafe_allow_html=True)
    r1,r2,r3,r4,r5,r6,r7,r8 = st.columns(8)
    mcard(r1, "Resolution",    f"{h}×{v}",
          f'{dg}" · {_ar}', border, custom)
    mcard(r2, "PPI",           f"{_ppi:.0f}",
          _ppi_class(_ppi), border, custom)
    mcard(r3, "Aspect Ratio",  _ar, _ar_name, border, custom)
    mcard(r4, "Pixel Clock",   f"{_pclkM:.2f} MHz",
          f"Blanking {blank_pct}% (×{1+blank_ratio:.2f})", border, custom)
    mcard(r5, "Active Pixels", f"{_tp/1e6:.2f} MP",
          f"{fps} Hz · {bpp} bpp", border, custom)
    mcard(r6, "Video Payload", f"{_vpay:.2f} Gbps",
          f"{_pclkM:.2f} MHz × {bpp} bpp", border, custom)
    mcard(r7, "DSC / Eff. bpp",
          f"{eff_bpp_val:.1f} bpp" if dsc_on else "OFF",
          dsc_sub, dsc_brd, custom)
    mcard(r8, "OLDI / Min eDP",
          f"{_ports}p / {_bl or '?'}L",
          f"OLDI ports / eDP lanes", border, custom)

# ── Main (selected) resolution row ────────────────────────────────────────────
st.markdown("**📌 Selected Resolution**" if use_custom else "",
            unsafe_allow_html=True)
_summary_row(h_act, v_act, diag, custom=False)

# ── Custom resolution row (amber, shown only when toggle is on) ───────────────
if use_custom:
    _summary_row(int(cw), int(ch_in), float(cd), custom=True)

st.markdown("<br>", unsafe_allow_html=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tabs
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
tab_edp, tab_gmsl3, tab_oldi, tab_dsi, tab_cust, tab_multiview, tab_dpae, tab_vrr, tab_competitive, tab_timing, tab_tddi, tab_case_study = st.tabs([
    "eDP Analysis", "GMSL3 vs. eDP", "OLDI / LVDS Analysis", "DSI Analysis",
    "Customer Projects", "🖼️ Multi-View", "🚗 DP AE Demo", "DP 2.1 Adaptive-Sync (VRR)",
    "🏆 Competitive Analysis",
    "📐 Display Timing",
    "🔌 Display Driver IC",
    "📋 Display Case Study",
])

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 1 – OLDI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab_oldi:
    st.markdown('<h3 class="section-header">OLDI (LVDS) – Selected Configuration</h3>',
                unsafe_allow_html=True)
    ca,cb,cc,cd_ = st.columns(4)
    mcard(ca,"OLDI Ports",     str(oldi_ports), f"Min: {min_ports}")
    mcard(cb,"Clock/Port",     f"{pclk_per_port:.2f} MHz", f"Limit: {max_oldi_mhz} MHz")
    mcard(cc,"Headroom/Port",  f"{max_oldi_mhz-pclk_per_port:.2f} MHz",
          f"{(1-pclk_per_port/max_oldi_mhz)*100:.1f}%")
    cd_.markdown(
        f'<div class="metric-card"><div class="metric-label">Feasibility</div>'
        f'<div style="margin-top:8px">{badge(oldi_ok)}</div>'
        f'<div class="metric-sub">{"OK" if oldi_ok else "Exceeds limit"}</div></div>',
        unsafe_allow_html=True)

    st.info(f"**LVDS pairs per port @ {bpp} bpp:** {dp_per_port} data + 1 clock = "
            f"**{tp_per_port} diff pairs/port** · "
            f"total across {oldi_ports} ports = **{oldi_ports*tp_per_port} pairs "
            f"({oldi_ports*tp_per_port*2} pins)**")

    st.markdown("#### Port Requirements vs. Frame Rate & Blanking")
    rows=[]
    for fr in [60,90]:
        for br in [5,10]:
            pc  = pixel_clock_hz(h_act,v_act,fr,br/100)
            pts = oldi_ports_needed(pc,max_oldi_mhz,min_ports)
            cpp = pc/1e6/pts; hdm = max_oldi_mhz-cpp
            rows.append({"FPS":f"{fr} Hz","Blanking":f"{br}%",
                         "Pixel Clock (MHz)":round(pc/1e6,2),
                         "Ports":pts,"Clock/Port (MHz)":round(cpp,2),
                         "Headroom (MHz)":round(hdm,2),
                         "Headroom %":round(hdm/max_oldi_mhz*100,1),
                         "Status":"✓ PASS" if cpp<=max_oldi_mhz else "✗ FAIL"})
    df_o=pd.DataFrame(rows)
    st.dataframe(df_o.style
        .map(cs,subset=["Status"])
        .map(ch,subset=["Headroom (MHz)","Headroom %"])
        .format({"Pixel Clock (MHz)":"{:.2f}","Clock/Port (MHz)":"{:.2f}",
                 "Headroom (MHz)":"{:.2f}","Headroom %":"{:.1f}"}),
        use_container_width=True, hide_index=True)

    st.markdown("#### Pixel Clock per Port vs. Number of Ports")
    pr = list(range(min_ports, min_ports+7))
    cv = [pclk_mhz/p for p in pr]
    fig_b=go.Figure()
    fig_b.add_trace(go.Bar(x=[f"{p}p" for p in pr],y=cv,
        marker_color=["#22c55e" if v<=max_oldi_mhz else "#ef4444" for v in cv],
        text=[f"{v:.1f}" for v in cv],textposition="outside",
        textfont=dict(color="#1e293b")))
    fig_b.add_hline(y=max_oldi_mhz,line_dash="dash",line_color="#f59e0b",
        annotation_text=f"Max {max_oldi_mhz} MHz",
        annotation_font_color="#1e293b",annotation_position="top right")
    fig_b.update_layout(height=340,xaxis_title="Ports",yaxis_title="MHz/port",
        title=f"{res_key} @{fps}Hz {blank_pct}% blanking",
        showlegend=False,**PLT)
    st.plotly_chart(fig_b,use_container_width=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB – DSI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab_dsi:
    st.markdown('<h3 class="section-header">DSI 1.2 – Maximum Active Pixels Table</h3>',
                unsafe_allow_html=True)

    dsi_ports = st.radio("Number of DSI Ports", DSI_PORTS_OPTIONS, horizontal=True,
                          format_func=lambda p: f"{p} Port{'s' if p>1 else ''}",
                          key="dsi_ports")

    st.info(
        "**DSI 1.2 spec**: up to **2 independent DSI ports**, each with up to "
        "**4 data lanes**.  \n"
        f"Selected: **{dsi_ports} Port{'s' if dsi_ports>1 else ''}** "
        f"({'each port drives an independent ' + str(int(total_pixels/dsi_ports)) + ' px/frame stream' if dsi_ports>1 else 'single stream drives the full frame'})."
    )

    dsi_target_px = total_pixels / dsi_ports

    st.markdown(f"**{fps} Hz · {bpp} bpp · {blank_pct}% blanking**  "
                f"| Target per port: **{int(dsi_target_px):,} px**")

    st.markdown("##### Max Active Pixels per Frame (MP)")
    st.latex(r"MP = \frac{Lanes \times LaneRate_{Gbps} \times 10^9}{eff\_bpp \times fps \times (1+blank\_ratio)} \div 10^6")
    st.caption(f"eff_bpp = **{eff_bpp_val:.2f} bpp**")
    dsi_mp_tbl={}
    for lane in DSI_LANES_OPTIONS:
        dsi_mp_tbl[f"{lane} Lane{'s' if lane>1 else ''}"] = {
            f"{lr} Gbps": dsi_max_active_pixels(lane, lr, fps, eff_bpp_val, blank_ratio)/1e6
            for lr in DSI_LANE_RATES}
    df_dsi_mp = pd.DataFrame(dsi_mp_tbl).T; df_dsi_mp.index.name = "Lanes \\ Rate"
    st.dataframe(df_dsi_mp.style.map(lambda v: cm(v, dsi_target_px)).format("{:.3f} MP"),
                 use_container_width=True)
    st.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-port target resolution "
        f"({dsi_target_px/1e6:.3f} MP)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-port target resolution"
    )

    st.markdown("##### Maximum PCLK (MHz)")
    st.latex(r"PCLK_{MHz} = MP \times fps \times (1+blank\_ratio) \div 10^6")
    dsi_target_pclk_mhz = dsi_target_px * fps * (1+blank_ratio) / 1e6
    dsi_mpclk_tbl={}
    for lane in DSI_LANES_OPTIONS:
        dsi_mpclk_tbl[f"{lane} Lane{'s' if lane>1 else ''}"] = {
            f"{lr} Gbps": dsi_max_active_pixels(lane, lr, fps, eff_bpp_val, blank_ratio) * fps * (1+blank_ratio) / 1e6
            for lr in DSI_LANE_RATES}
    df_dsi_mpclk = pd.DataFrame(dsi_mpclk_tbl).T; df_dsi_mpclk.index.name = "Lanes \\ Rate"
    st.dataframe(df_dsi_mpclk.style.map(lambda v: cm(v, dsi_target_pclk_mhz*1e6)).format("{:.2f} MHz"),
                 use_container_width=True)
    st.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-port target pixel clock "
        f"({dsi_target_pclk_mhz:.2f} MHz)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-port target pixel clock"
    )

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 2 – eDP
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab_edp:
    edp_sub1, edp_sub2, edp_sub3, edp_sub4, edp_sub5, edp_sub6 = st.tabs([
        "📊 Analysis", "🔀 eDP Streams",
        "🖼️ MSO 2x2 Superframe", "🖼️ MSO 2x1 Superframe", "🖼️ MSO 4x1 Superframe",
        "🔗 Link Training"
    ])

    # shared computed values used by both sub-tabs
    dsc_note = (f"  |  **DSC {dsc_ratio_val:.2g}:1** → eff. **{eff_bpp_val:.2f} bpp**"
                if dsc_on else "  |  DSC **off**")
    mso_note = (f"  |  **MSO {mso_mode}** ({ns_mso} streams × {lps_mso} lane = "
                f"{total_lanes_req} total lanes)" if mso_mode != "Off" else "")

    def _edp_mp(lanes, lr):
        """Max active pixels; uses fixed lps_mso for MSO modes."""
        lps = lps_mso if mso_mode != "Off" else lanes
        return edp_max_active_pixels(lps, lr, fps, eff_bpp_val, blank_ratio)

    target_for_color = px_per_stream

    # ── Sub-tab 1 : Analysis ─────────────────────────────────────────────
    with edp_sub1:
        st.markdown('<h3 class="section-header">eDP – Maximum Active Pixels Table</h3>',
                    unsafe_allow_html=True)
        st.markdown(f"**{fps} Hz · {bpp} bpp · {blank_pct}% blanking{dsc_note}{mso_note}**  "
                    f"| Target: **{h_act}×{v_act} = {total_pixels:,} px**  "
                    f"| 8b/10b → 80 %")

        _EDP_TBL_STYLES = [
            {"selector": "table", "props": [("font-size", "1.05rem"), ("border-collapse", "collapse"), ("width", "100%")]},
            {"selector": "th", "props": [("font-size", "1.05rem"), ("padding", "6px 12px"),
                                          ("background", "#1e3a5f"), ("color", "#ffffff"), ("border", "1px solid #334155")]},
            {"selector": "td", "props": [("font-size", "1.05rem"), ("padding", "6px 12px"),
                                          ("border", "1px solid #cbd5e1"), ("text-align", "center")]},
        ]
        def _edp_render_tbl(styler, hide_index=False):
            if hide_index:
                styler = styler.hide(axis="index")
            st.markdown(styler.set_table_styles(_EDP_TBL_STYLES).to_html(), unsafe_allow_html=True)

        with st.container(key="edp_max_active_px_tbl"):
            if mso_mode == "Off":
                _edp_col_mp, _edp_col_pclk = st.columns(2)

                with _edp_col_mp:
                    st.markdown("##### Max Active Pixels per Frame (MP)")
                    st.latex(r"MP = \frac{Lanes \times LinkRate_{Gbps} \times 10^9 \times 0.8}{eff\_bpp \times fps \times (1+blank\_ratio)} \div 10^6")
                    st.caption(f"eff_bpp = **{eff_bpp_val:.2f} bpp**")
                    mp_tbl={}
                    for lane in LANES_OPTIONS:
                        mp_tbl[f"{lane} Lane{'s' if lane>1 else ''}"] = {
                            f"{lr} Gbps": _edp_mp(lane,lr)/1e6 for lr in EDP_LINK_RATES}
                    df_mp=pd.DataFrame(mp_tbl).T; df_mp.index.name="Lanes \\ Rate"
                    _edp_render_tbl(df_mp.style.map(lambda v: cm(v, target_for_color)).format("{:.3f} MP"))
                    st.caption(
                        "🟩 **Green = PASS** — meets/exceeds the target video resolution "
                        f"({target_for_color/1e6:.3f} MP)  ·  "
                        "🟥 **Red = FAIL** — insufficient bandwidth for the target resolution"
                    )

                with _edp_col_pclk:
                    st.markdown("##### Maximum PCLK (MHz)")
                    st.latex(r"PCLK_{MHz} = MP \times fps \times (1+blank\_ratio) \div 10^6")
                    target_pclk_mhz = pclk / 1e6
                    mpclk_tbl={}
                    for lane in LANES_OPTIONS:
                        mpclk_tbl[f"{lane} Lane{'s' if lane>1 else ''}"] = {
                            f"{lr} Gbps": _edp_mp(lane,lr) * fps * (1+blank_ratio) / 1e6
                            for lr in EDP_LINK_RATES}
                    df_mpclk=pd.DataFrame(mpclk_tbl).T; df_mpclk.index.name="Lanes \\ Rate"
                    _edp_render_tbl(df_mpclk.style.map(lambda v: cm(v, target_pclk_mhz*1e6)).format("{:.2f} MHz"))
                    st.caption(
                        "🟩 **Green = PASS** — meets/exceeds the target pixel clock "
                        f"({target_pclk_mhz:.2f} MHz)  ·  "
                        "🟥 **Red = FAIL** — insufficient bandwidth for the target pixel clock"
                    )

                if edp_show_margin:
                    st.markdown("##### Pixel Budget Margin (%)")
                    mg_tbl={}
                    for lane in LANES_OPTIONS:
                        mg_tbl[f"{lane} Lane{'s' if lane>1 else ''}"] = {
                            f"{lr} Gbps": (_edp_mp(lane,lr)/target_for_color-1)*100
                            for lr in EDP_LINK_RATES}
                    df_mg=pd.DataFrame(mg_tbl).T; df_mg.index.name="Lanes \\ Rate"
                    _edp_render_tbl(df_mg.style.map(cmg).format("{:+.1f} %"))

            else:
                tile_w = h_act // ht_mso; tile_h = v_act // vt_mso
                def _la():
                    parts=[]
                    for s in range(ns_mso):
                        lo=s*lps_mso; hi=lo+lps_mso-1
                        parts.append(f"L{lo}→S{s}" if lps_mso==1 else f"L{lo}–{hi}→S{s}")
                    return "  |  ".join(parts)
                st.info(
                    f"**MSO {mso_mode}:** {ns_mso} streams · {lps_mso} lane/stream · "
                    f"{total_lanes_req} total lanes required\n\n"
                    f"Lane assignment: **{_la()}**\n\n"
                    f"Each stream: **{tile_w}×{tile_h}** px = **{px_per_stream/1e6:.3f} MP/stream**")
                st.markdown(f"##### Max Active Pixels per Stream (MP) — {lps_mso} lane/stream")
                mso_rows=[]
                for lr in EDP_LINK_RATES:
                    avail = edp_max_active_pixels(lps_mso, lr, fps, eff_bpp_val, blank_ratio)
                    mso_rows.append({
                        "Link Rate": f"{lr} Gbps", "Lanes/Stream": lps_mso,
                        "Tile (px/stream)": f"{tile_w}×{tile_h}",
                        "Required (MP)": round(px_per_stream/1e6,3),
                        "Max Avail (MP)": round(avail/1e6,3),
                        "Margin %": f"{(avail/px_per_stream-1)*100:+.1f}%",
                        "Status": "✓ PASS" if avail>=px_per_stream else "✗ FAIL",
                    })
                df_mso=pd.DataFrame(mso_rows)
                _edp_render_tbl(df_mso.style.map(cs,subset=["Status"]).map(cmg,subset=["Margin %"]),
                                hide_index=True)

        # Heatmap
        st.markdown("#### eDP Bandwidth Heatmap")
        if mso_mode == "Off":
            z,zt=[],[]
            for lane in LANES_OPTIONS:
                rz,rt=[],[]
                for lr in EDP_LINK_RATES:
                    mp=_edp_mp(lane,lr)
                    rz.append(mp/1e6)
                    rt.append(f"{mp/1e6:.3f} MP<br>{'✓' if mp>=target_for_color else '✗'}")
                z.append(rz); zt.append(rt)
            hm_y=[f"{l}L" for l in LANES_OPTIONS]
        else:
            z,zt=[[],[]]; rz,rt=[],[]
            for lr in EDP_LINK_RATES:
                mp=edp_max_active_pixels(lps_mso,lr,fps,eff_bpp_val,blank_ratio)
                rz.append(mp/1e6)
                rt.append(f"{mp/1e6:.3f} MP<br>{'✓' if mp>=target_for_color else '✗'}")
            z=[rz]; zt=[rt]
            hm_y=[f"MSO {mso_mode} ({lps_mso}L/stream)"]
        fig_hm=go.Figure(go.Heatmap(
            z=z, x=[f"{r:.2g}G" for r in EDP_LINK_RATES], y=hm_y,
            text=zt, texttemplate="%{text}",
            textfont=dict(size=18, color="#1e293b"),
            colorscale="RdYlGn", zmid=target_for_color/1e6,
            colorbar=dict(title="MP", tickfont=dict(color="#1e293b", size=16))))
        fig_hm.update_layout(height=320, **PLT,
            title=dict(
                text=f"Max pixels/stream — target {target_for_color/1e6:.2f} MP"
                     + (f" (MSO {mso_mode}: {lps_mso}L/stream)" if mso_mode!="Off" else ""),
                x=0, xanchor="left", font=dict(size=16)),
            xaxis=dict(title="Link Rate", tickfont=dict(size=15)),
            yaxis=dict(title="Lanes", tickfont=dict(size=15)),
            margin=dict(l=70))
        st.plotly_chart(fig_hm, use_container_width=True)

    # ── Sub-tab 2 : eDP Streams diagram ─────────────────────────────────
    with edp_sub2:
        st.markdown('<h3 class="section-header">eDP Stream Architecture</h3>',
                    unsafe_allow_html=True)
        st.markdown(f"**{fps} Hz · {bpp} bpp · {blank_pct}% blanking{dsc_note}{mso_note}**")

        # Default: 4 lanes when MSO Off, total_lanes_req when MSO On
        default_lanes = total_lanes_req if mso_mode != "Off" else 4
        if default_lanes not in LANES_OPTIONS:
            default_lanes = LANES_OPTIONS[-1]   # fallback to 4

        sel_lanes = st.selectbox(
            "Total lanes for stream diagram",
            options=LANES_OPTIONS,
            index=LANES_OPTIONS.index(default_lanes),
            format_func=lambda x: f"{x} Lane{'s' if x>1 else ''}",
            key="edp_stream_lanes")

        if best_rate:
            st.plotly_chart(
                draw_edp_streams(sel_lanes, mso_mode, h_act, v_act,
                                 best_rate, fps, eff_bpp_val, blank_ratio),
                use_container_width=True)
            st.markdown('<p class="diagram-caption">'
                        'Each colour = one stream. Arrows show data flow: lanes → stream → display tile.</p>',
                        unsafe_allow_html=True)

            # Per-stream summary table
            ns_s, lps_s, ht_s, vt_s = mso_params(mso_mode)
            if mso_mode == "Off": lps_s = sel_lanes
            tile_w_s = h_act // ht_s;  tile_h_s = v_act // vt_s
            px_ps_s  = h_act * v_act / ns_s
            bw_ps_s  = lps_s * best_rate * EDP_ENCODING
            max_ps_s = edp_max_active_pixels(lps_s, best_rate, fps, eff_bpp_val, blank_ratio)
            srows=[]
            for s in range(ns_s):
                lo=s*lps_s; hi=lo+lps_s-1
                srows.append({
                    "Stream":           f"Stream {s}",
                    "Lanes":            f"L{lo}" if lps_s==1 else f"L{lo} – L{hi}",
                    "Lanes/Stream":     lps_s,
                    "Tile (px)":        f"{tile_w_s}×{tile_h_s}",
                    "Px/Stream (MP)":   round(px_ps_s/1e6, 3),
                    "BW avail (Gbps)":  round(bw_ps_s, 3),
                    "Max px (MP)":      round(max_ps_s/1e6, 3),
                    "Margin %":         f"{(max_ps_s/px_ps_s-1)*100:+.1f}%",
                    "Status":           "✓ PASS" if max_ps_s>=px_ps_s else "✗ FAIL",
                })
            st.dataframe(pd.DataFrame(srows).style.map(cs,subset=["Status"]),
                         use_container_width=True, hide_index=True)
        else:
            st.warning("No valid eDP config for selected parameters.")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 3 – Side-by-side
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab_competitive:
    comp_sub1, comp_sub2, comp_sub3 = st.tabs(["Side-by-Side Comparison", "Board Layout & Block Diagram",
                                               "Full Matrix (All Resolutions)"])

with comp_sub1:
    st.markdown('<h3 class="section-header">⚖️ OLDI vs eDP — Side-by-Side</h3>',
                unsafe_allow_html=True)
    cl,cs_col,cr = st.columns([5,1,5])
    with cl:
        st.markdown("### 🔵 OLDI / LVDS")
        st.markdown(f"""
| Parameter | Value |
|---|---|
| PPI | **{ppi_val:.0f}** ({_ppi_class(ppi_val)}) |
| Pixel clock | **{pclk_mhz:.2f} MHz** |
| Ports required | **{oldi_ports}** |
| Data pairs / port | **{dp_per_port}** ({bpp} bpp) |
| Pairs / port total | **{tp_per_port}** ({dp_per_port}D+1Clk) |
| Clock / port | **{pclk_per_port:.2f} MHz** |
| Headroom / port | **{max_oldi_mhz-pclk_per_port:.2f} MHz** |
| Feasible | {"**✅ YES**" if oldi_ok else "**NO**"} |
| DSC support | **Not applicable** |
        """)
        st.info(f"**{oldi_ports}× OLDI ports** · {dp_per_port}D+1Clk each  \n"
                f"Est. FPC: ~{oldi_ports*tp_per_port*2+24} pins")
    with cs_col:
        st.markdown("<div style='text-align:center;font-size:2rem;margin-top:90px;"
                    "color:#1e3a5f'>VS</div>", unsafe_allow_html=True)
    with cr:
        st.markdown("### 🟢 eDP")
        if best_lanes:
            bst_bw = best_lanes * best_rate * EDP_ENCODING
            _lps_best = lps_mso if mso_mode != "Off" else best_lanes
            bst_mp = edp_max_active_pixels(_lps_best, best_rate, fps, eff_bpp_val, blank_ratio)
            sig_p  = best_lanes*2+3
            st.markdown(f"""
| Parameter | Value |
|---|---|
| PPI | **{ppi_val:.0f}** ({_ppi_class(ppi_val)}) |
| Min config | **{best_lanes}L × {best_rate} Gbps** |
| MSO mode | **{mso_mode}** |
| DSC | **{"ON " + str(dsc_ratio_val) + ":1" if dsc_on else "Off"}** |
| Eff. bpp | **{eff_bpp_val:.2f}** |
| Eff. BW | **{bst_bw:.2f} Gbps** |
| Max px/stream | **{bst_mp/1e6:.3f} MP** |
| Margin | **{(bst_mp/px_per_stream-1)*100:+.1f}%** |
| Signal pins | **{sig_p}** |
| Feasible | **✅ YES** |
            """)
            st.success(f"Min eDP: **{best_lanes}L @ {best_rate} Gbps**  "
                       f"| margin **{(bst_mp/px_per_stream-1)*100:+.1f}%**  "
                       f"| est. FPC ~{sig_p+12} pins")
        else:
            st.error("No eDP config supports this resolution/fps/bpp/MSO.")

    st.divider()
    st.markdown("#### Bandwidth Comparison")
    oldi_bw  = oldi_ports * max_oldi_mhz * bpp / 1000
    req_gbps = pclk_mhz * eff_bpp_val / 1000
    edp_bws  = {f"{l}L×{r}G": l*r*EDP_ENCODING
                for l in LANES_OPTIONS for r in EDP_LINK_RATES}
    fig_c=go.Figure()
    fig_c.add_hline(y=req_gbps,line_dash="dot",line_color="#f59e0b",
        annotation_text=f"Required {req_gbps:.2f} Gbps"
                         + (" (with DSC)" if dsc_on else ""),
        annotation_font_color="#1e293b", annotation_position="top left")
    fig_c.add_trace(go.Bar(name="OLDI",x=[f"OLDI {oldi_ports}×p"],y=[oldi_bw],
        marker_color="#3b82f6",text=[f"{oldi_bw:.2f}"],textposition="outside",
        textfont=dict(color="#1e293b")))
    ev=list(edp_bws.values())
    fig_c.add_trace(go.Bar(name="eDP",x=list(edp_bws.keys()),y=ev,
        marker_color=["#22c55e" if v>=req_gbps else "#ef4444" for v in ev],
        text=[f"{v:.2f}" for v in ev],textposition="outside",
        textfont=dict(color="#1e293b")))
    fig_c.update_layout(height=400,title="Effective BW vs Required",
        xaxis_title="Config",yaxis_title="Gbps",barmode="group",**PLT)
    st.plotly_chart(fig_c,use_container_width=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 4 – Board Layout
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with comp_sub2:
    st.markdown('<h3 class="section-header">🏗️ Board Layout & Block Diagrams</h3>',
                unsafe_allow_html=True)
    bd1, bd2 = st.tabs(["🔵 OLDI / LVDS", "🟢 eDP Block Diagram"])

    with bd1:
        total_pairs_all = oldi_ports * tp_per_port
        st.markdown(
            f"**{oldi_ports} ports · {dp_per_port}D+1Clk/port = "
            f"{tp_per_port} pairs/port · {total_pairs_all} total pairs · "
            f"{pclk_per_port:.1f} MHz/port · {bpp} bpp**")
        st.plotly_chart(draw_oldi(oldi_ports, pclk_per_port, max_oldi_mhz, bpp, fps),
                        use_container_width=True)
        st.markdown('<p class="diagram-caption">Solid = video data | Dashed = control/auxiliary</p>',
                    unsafe_allow_html=True)
        sig_r=[
            ("Data pairs",   f"{dp_per_port}/port × {oldi_ports} ports",
             f"{dp_per_port*oldi_ports} pairs", f"{dp_per_port*oldi_ports*2} pins"),
            ("Clock pairs",  f"1/port × {oldi_ports} ports",
             f"{oldi_ports} pairs",              f"{oldi_ports*2} pins"),
            ("**Total video**","",f"**{total_pairs_all} pairs**",
             f"**{total_pairs_all*2} pins**"),
            ("Control (GPIO/I²C/PWM)","~6–10 signals","—","~8–10 pins"),
            ("Power + GND",  "AVDD/VDD/GND","—","~10–16 pins"),
            ("**Est. FPC total**","","—",
             f"**~{total_pairs_all*2+20}–{total_pairs_all*2+28} pins**"),
        ]
        st.dataframe(pd.DataFrame(sig_r,columns=["Group","Detail","Pairs","Pins"]),
                     use_container_width=True, hide_index=True)

    with bd2:
        if best_lanes:
            edp_sig = best_lanes*2+3
            st.markdown(
                f"**{best_lanes}L @ {best_rate} Gbps · eff. "
                f"{best_lanes*best_rate*EDP_ENCODING:.2f} Gbps · {bpp} bpp**"
                + (f" + DSC {dsc_ratio_val:.2g}:1" if dsc_on else "")
                + (f" + MSO {mso_mode}" if mso_mode!="Off" else ""))
            st.plotly_chart(draw_edp(best_lanes, best_rate, bpp, fps, dsc_on, mso_mode),
                            use_container_width=True)
            st.markdown('<p class="diagram-caption">Solid = video data | Dashed = AUX/HPD/control</p>',
                        unsafe_allow_html=True)
            edp_r=[
                ("Main lane pairs", f"{best_lanes} lane{'s' if best_lanes>1 else ''}",
                 f"{best_lanes} pairs", f"{best_lanes*2} pins"),
                ("AUX channel",      "1 diff pair (bi-dir)","1 pair","2 pins"),
                ("HPD",              "1 signal","—","1 pin"),
                ("**Total signal**","","—",f"**{edp_sig} pins**"),
                ("Power + GND","VDD/GND","—","~8–12 pins"),
                ("**Est. FPC total**","","—",
                 f"**~{edp_sig+10}–{edp_sig+16} pins**"),
            ]
            st.dataframe(pd.DataFrame(edp_r,columns=["Group","Detail","Pairs","Pins"]),
                         use_container_width=True, hide_index=True)
        else:
            st.warning("No valid eDP config for selected parameters.")


    st.divider()
    # ── Feature comparison ────────────────────────────────────────────
    st.markdown("### 📋 Interface Feature Comparison")
    edp_str = f"{best_lanes}L×{best_rate}Gbps" if best_lanes else "N/A"
    feat=[
        ("Standard",             "VESA OpenLDI",                   "VESA eDP"),
        ("Topology",             "Parallel differential (LVDS)",   "High-speed serial"),
        ("Encoding",             "7:1 LVDS",                       "8b/10b ANSI"),
        ("Data pairs/port",      f"{dp_per_port} ({bpp} bpp)",     "N/A (serial lanes)"),
        ("Clock pairs/port",     "1",                              "N/A (embedded clk)"),
        ("Min config",           f"{oldi_ports} ports",            edp_str),
        ("Signal pins (video)",
         f"{oldi_ports}port×({dp_per_port}D+1Clk)×2 = ~{oldi_ports*tp_per_port*2} pins",
         f"{best_lanes or 1}Lane×2 + 2(AUX) + 1(HPD) = ~{(best_lanes or 1)*2+3} pins"),
        ("Aux / config",         "I²C / SPI (separate)",           "Built-in AUX (DPCD)"),
        ("Hot plug detect",      "Not native",                  "✅ HPD pin"),
        ("Link training",        "None",                        "✅ Automatic"),
        ("DSC support",          "Not supported",               "✅ eDP 1.4+ (3:1 / 3.75:1)"),
        ("MSO support",          "Not supported",               "✅ 2×1 / 4×1 / 2×2"),
        ("Panel Self Refresh",   "Not supported",               "✅ PSR / PSR2"),
        ("Adaptive sync",        "Not supported",               "✅ eDP 1.4+"),
        ("EMI profile",          "Higher (parallel bus)",          "Lower (serial + SS)"),
        ("PCB routing",          f"High ({oldi_ports}×{tp_per_port} pairs)", "Low (few lanes+AUX)"),
        ("Power management",     "External PMIC + seq.",           "Native DP power states"),
    ]
    df_feat=pd.DataFrame(feat,columns=["Feature","🔵 OLDI / LVDS","🟢 eDP"])
    def _cf(v):
        s=str(v)
        if s.startswith("✅"): return "background-color:#dcfce7;color:#166534"
        if s.startswith(""): return "background-color:#fee2e2;color:#991b1b"
        return ""
    st.dataframe(df_feat.style
        .map(_cf,subset=["🔵 OLDI / LVDS","🟢 eDP"])
        .set_properties(subset=["Feature"],**{"color":"#1e3a5f","font-weight":"600"}),
        use_container_width=True, hide_index=True)

    st.divider()
    # ── Aspect ratio + PPI table ──────────────────────────────────────
    st.markdown("### 📐 Resolution · Aspect Ratio · PPI Summary")
    ar_rows=[]
    for rk,(h,v,dg) in RESOLUTIONS.items():
        g_=math.gcd(h,v); aw,ah=h//g_,v//g_
        p=ppi(h,v,dg)
        ar_rows.append({
            "Resolution":    f"{h}×{v}",
            "Diagonal":      f"{dg}\"",
            "Aspect Ratio":  f"{aw}:{ah}",
            "Common Name":   _common_ar_name(aw,ah),
            "Decimal Ratio": round(h/v,4),
            "Total Pixels":  f"{h*v/1e6:.3f} MP",
            "PPI":           round(p,1),
            "Density Class": _ppi_class(p),
        })
    df_ar=pd.DataFrame(ar_rows)
    def _car(v):
        s=str(v)
        if "16:9" in s or "Widescreen" in s: return "background-color:#dbeafe;color:#1e40af"
        if "Ultra" in s or "panoramic" in s: return "background-color:#ede9fe;color:#5b21b6"
        return ""
    def _cppi(v):
        s=str(v)
        if "Retina" in s or "4K" in s: return "background-color:#dcfce7;color:#166534"
        if "QHD"   in s:               return "background-color:#d1fae5;color:#065f46"
        return ""
    st.dataframe(df_ar.style.map(_car,subset=["Common Name"]).map(_cppi,subset=["Density Class"]),
                 use_container_width=True, hide_index=True)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 5 – Full matrix
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with comp_sub3:
    st.markdown('<h3 class="section-header">📊 Full Matrix — All Resolutions</h3>',
                unsafe_allow_html=True)
    sub1, sub2 = st.tabs(["🔵 OLDI Full Matrix","🟢 eDP Full Matrix"])

    with sub1:
        st.markdown(f"**Max {max_oldi_mhz} MHz/port · Min {min_ports} ports · "
                    f"{dp_per_port}D+1Clk/port ({bpp} bpp)**")
        all_o=[]
        for rk,(h,v,dg) in RESOLUTIONS.items():
            for br in [5,10]:
                for fr in [60,90]:
                    pc=pixel_clock_hz(h,v,fr,br/100)
                    pts=oldi_ports_needed(pc,max_oldi_mhz,min_ports)
                    cpp=pc/1e6/pts; hdm=max_oldi_mhz-cpp
                    all_o.append({"Resolution":f"{h}×{v} ({dg}\")",
                        "Aspect":aspect_ratio(h,v),
                        "PPI":round(ppi(h,v,dg),0),
                        "Blanking":f"{br}%","FPS":f"{fr} Hz",
                        "Pixel Clock":round(pc/1e6,2),"Ports":pts,
                        "Clock/Port":round(cpp,2),"Headroom":round(hdm,2),
                        "Status":"✓  PASS" if cpp<=max_oldi_mhz else "✗  FAIL"})
        df_ao=pd.DataFrame(all_o)
        st.dataframe(df_ao.style
            .map(cs,subset=["Status"])
            .map(ch,subset=["Headroom"])
            .format({"Pixel Clock":"{:.2f}","Clock/Port":"{:.2f}","Headroom":"{:.2f}"}),
            use_container_width=True, hide_index=True)

    with sub2:
        dsc_lbl2 = f" + DSC {dsc_ratio_val:.2g}:1 ({eff_bpp_val:.2f} eff.bpp)" if dsc_on else ""
        mso_lbl2 = f" + MSO {mso_mode}" if mso_mode!="Off" else ""
        st.markdown(f"**8b/10b · {bpp} bpp · {fps} Hz{dsc_lbl2}{mso_lbl2}**")
        all_e=[]
        ns2,lps2,_,_ = mso_params(mso_mode)
        for rk,(h,v,dg) in RESOLUTIONS.items():
            tp_res=h*v
            px_ps2=tp_res/ns2   # per stream (BW check uses lps2 lanes)
            row={"Resolution":f"{h}×{v} ({dg}\")",
                 "Aspect":aspect_ratio(h,v),
                 "PPI":round(ppi(h,v,dg),0),
                 "Px/Stream":f"{px_ps2/1e6:.3f} MP"}
            if mso_mode=="Off":
                for lane in LANES_OPTIONS:
                    for lr in EDP_LINK_RATES:
                        row[f"{lane}L×{lr:.2g}G"]=round(
                            edp_max_active_pixels(lane,lr,fps,eff_bpp_val,blank_ratio)/1e6,3)
            else:
                for lr in EDP_LINK_RATES:
                    row[f"{lps2}L/stream×{lr:.2g}G"]=round(
                        edp_max_active_pixels(lps2,lr,fps,eff_bpp_val,blank_ratio)/1e6,3)
            all_e.append({"target":px_ps2,"data":row})
        df_ae=pd.DataFrame([r["data"] for r in all_e])
        tgts=[r["target"] for r in all_e]
        ccols=[c for c in df_ae.columns
               if c not in("Resolution","Aspect","PPI","Px/Stream")]
        def _ecc(col,tl):
            def fn(s):
                return ["background-color:#dcfce7;color:#166534"
                        if float(v)*1e6>=tl[i]
                        else "background-color:#fee2e2;color:#991b1b"
                        for i,v in enumerate(s)]
            return fn
        sty=df_ae.style.format({c:"{:.3f} MP" for c in ccols})
        for col in ccols:
            sty=sty.apply(_ecc(col,tgts),subset=[col])
        st.dataframe(sty,use_container_width=True,hide_index=True)

        st.markdown("#### Minimum eDP Config per Resolution")
        mcs=[]
        for rk,(h,v,dg) in RESOLUTIONS.items():
            tp_res=h*v; px_ps2=tp_res/ns2
            found_l, found_r = None, None
            if mso_mode=="Off":
                for lane in LANES_OPTIONS:
                    for lr in EDP_LINK_RATES:
                        if edp_max_active_pixels(lane,lr,fps,eff_bpp_val,blank_ratio)>=px_ps2:
                            found_l,found_r=lane,lr; break
                    if found_l: break
            else:
                found_l = ns2*lps2   # total lanes fixed
                for lr in EDP_LINK_RATES:
                    if edp_max_active_pixels(lps2,lr,fps,eff_bpp_val,blank_ratio)>=px_ps2:
                        found_r=lr; break
            if found_r:
                _lps_f = lps2 if mso_mode!="Off" else found_l
                mp=edp_max_active_pixels(_lps_f,found_r,fps,eff_bpp_val,blank_ratio)
                mcs.append({"Resolution":f"{h}×{v} ({dg}\")",
                    "Aspect":aspect_ratio(h,v),
                    "PPI":round(ppi(h,v,dg),0),
                    "Px/Stream":f"{px_ps2/1e6:.3f} MP",
                    "Total Lanes":found_l,"Link Rate":f"{found_r} Gbps",
                    "Lanes/Stream": _lps_f,
                    "Eff BW":round(found_l*found_r*EDP_ENCODING,2),
                    "Max Px/Stream":round(mp/1e6,3),
                    "Margin":f"{(mp/px_ps2-1)*100:+.1f}%"})
            else:
                mcs.append({"Resolution":f"{h}×{v} ({dg}\")",
                    "Aspect":aspect_ratio(h,v),
                    "PPI":round(ppi(h,v,dg),0),
                    "Px/Stream":"—","Total Lanes":"N/A","Link Rate":"N/A",
                    "Lanes/Stream":"N/A","Eff BW":"N/A",
                    "Max Px/Stream":"N/A","Margin":"✗ No config"})
        df_mc=pd.DataFrame(mcs)
        st.dataframe(df_mc.style.map(
            lambda v: "background-color:#dcfce7;color:#166534"
                      if isinstance(v,str) and v.startswith("+") else
                      "background-color:#fee2e2;color:#991b1b"
                      if isinstance(v,str) and "No config" in v else "",
            subset=["Margin"]),use_container_width=True,hide_index=True)

# ── Fill the top-right PDF placeholder (all vars are now defined) ─────────────
_g   = math.gcd(h_act, v_act)
_ar  = f"{h_act//_g}:{v_act//_g}"
_pc  = pclk / 1e6
_pdf_params = dict(
    res_label=f"{h_act}x{v_act}", diag=diag,
    ppi=ppi(h_act, v_act, diag), ar=_ar,
    pclk_mhz=_pc, mpx=total_pixels/1e6,
    vpay=_pc*bpp/1000, fps=fps, bpp=bpp,
    blank_pct=blank_pct, blank_ratio=blank_ratio,
    dsc_on=dsc_on, dsc_ratio=DSC_RATIO.get(bpp, 3.0),
    eff_bpp=eff_bpp_val, mso_mode=mso_mode,
    oldi_ports=oldi_ports, dp_per_port=dp_per_port,
    tp_per_port=tp_per_port, pclk_per_port=pclk_per_port,
    max_oldi_mhz=max_oldi_mhz, best_lanes=best_lanes,
    best_rate=best_rate,
)
_pdf_bytes = generate_pdf(_pdf_params)
_fname = (f"display_report_{h_act}x{v_act}_{bpp}bpp_{fps}Hz_"
          f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
_pdf_placeholder.download_button(
    label="📄 Export PDF",
    data=_pdf_bytes,
    file_name=_fname,
    mime="application/pdf",
    type="primary",
    use_container_width=True,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 6 – MSO 2x2 Superframe
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _draw_nav_panel(img_arr, x0, y0, w, h):
    """Draw Google Maps-style Navigation panel into img_arr."""
    img = Image.fromarray(img_arr[y0:y0+h, x0:x0+w])
    d = ImageDraw.Draw(img)

    try:
        font_road   = ImageFont.truetype("arialbd.ttf", max(10, h//60))
        font_label  = ImageFont.truetype("arial.ttf",   max(9,  h//70))
        font_ui     = ImageFont.truetype("arialbd.ttf", max(14, h//40))
        font_small  = ImageFont.truetype("arial.ttf",   max(10, h//65))
    except Exception:
        font_road = font_label = font_ui = font_small = ImageFont.load_default()

    # ── Map background (Google Maps light beige) ──────────────────────────
    d.rectangle([0, 0, w, h], fill=(242, 239, 230))

    # ── Water body (river / lake) ─────────────────────────────────────────
    d.polygon([(0, h//3), (w//5, h//4), (w//3, h//3+20),
               (w//2, h//3-10), (w//2, h//2+40), (w//4, h//2+60),
               (0, h//2+30)], fill=(168, 218, 255))
    d.text((w//8, h//2), "Lake View", fill=(100, 160, 210), font=font_label)

    # ── Parks (green blocks) ──────────────────────────────────────────────
    parks = [
        (w*2//3, h//8, w*5//6, h*3//8),
        (w*4//5, h*2//3, w-10,  h*9//10),
        (w//12,  h*3//5, w//5,  h*9//10),
    ]
    for px0, py0, px1, py1 in parks:
        d.rectangle([px0, py0, px1, py1], fill=(196, 224, 172))
        d.rectangle([px0, py0, px1, py1], outline=(160, 200, 130), width=2)
    d.text((w*2//3 + 8, h//8 + 6), "City Park", fill=(80, 140, 60), font=font_label)

    # ── City blocks (grey rectangles) ─────────────────────────────────────
    blocks = [
        (w*3//8, h//8,   w*9//20, h//3),
        (w*3//8, h*5//8, w*9//20, h*4//5),
        (w*7//12,h//8,   w*2//3,  h//3),
        (w*7//12,h*5//8, w*2//3,  h*4//5),
        (w//5,   h//8,   w//3,    h*2//7),
        (w//5,   h*3//5, w//3,    h*4//5),
    ]
    for bx0, by0, bx1, by1 in blocks:
        d.rectangle([bx0, by0, bx1, by1], fill=(218, 214, 205),
                    outline=(200, 196, 188), width=1)

    # ── Road network (minor roads — white) ───────────────────────────────
    minor_roads = [
        [(w//5, 0),       (w//5, h)],
        [(w//3, 0),       (w//3, h)],
        [(w*9//20, 0),    (w*9//20, h)],
        [(w*7//12, 0),    (w*7//12, h)],
        [(w*2//3, 0),     (w*2//3, h)],
        [(w*5//6, 0),     (w*5//6, h)],
        [(0, h//8),       (w, h//8)],
        [(0, h//3),       (w, h//3)],
        [(0, h*5//8),     (w, h*5//8)],
        [(0, h*4//5),     (w, h*4//5)],
    ]
    for pts in minor_roads:
        d.line(pts, fill=(255, 255, 255), width=max(3, h//160))

    # ── Major roads (wider, light orange/yellow) ──────────────────────────
    major_roads = [
        [(0, h//2),   (w, h//2)],
        [(w*2//5, 0), (w*2//5, h)],
    ]
    for pts in major_roads:
        d.line(pts, fill=(255, 200, 100), width=max(7, h//80))
        d.line(pts, fill=(255, 255, 255), width=max(2, h//200))

    # ── Route highlight (Google Maps blue route) ──────────────────────────
    route_pts = [
        (0,          h*3//4),
        (w//5,       h*3//4),
        (w//5,       h//2),
        (w*2//5,     h//2),
        (w*2//5,     h//3),
        (w*7//12,    h//3),
        (w*7//12,    h//2),
        (w,          h//2),
    ]
    d.line(route_pts, fill=(66, 133, 244), width=max(10, h//55))
    d.line(route_pts, fill=(255, 255, 255), width=max(3,  h//160))

    # ── Road labels ───────────────────────────────────────────────────────
    d.text((w*2//5 + 5, h//4),    "Main St",     fill=(80, 60, 30), font=font_road)
    d.text((w//10,      h//2 + 5), "Highway 1",  fill=(80, 60, 30), font=font_road)

    # ── Current location pin (Google Maps red teardrop) ───────────────────
    px, py = w*2//5, h//2
    r_pin = max(18, h//35)
    d.ellipse([px-r_pin, py-r_pin*2, px+r_pin, py], fill=(234, 67, 53))
    d.ellipse([px-r_pin, py-r_pin*2, px+r_pin, py], outline=(180, 30, 20), width=2)
    d.ellipse([px-r_pin//2, py-int(r_pin*1.5), px+r_pin//2, py-r_pin//2],
              fill=(255, 255, 255))
    # shadow teardrop tip
    d.polygon([(px-r_pin//2, py-6), (px+r_pin//2, py-6), (px, py+6)],
              fill=(234, 67, 53))

    # ── Destination flag ──────────────────────────────────────────────────
    dx2, dy2 = w - 60, h//3
    d.line([(dx2, dy2-30), (dx2, dy2+20)], fill=(50, 50, 50), width=3)
    d.polygon([(dx2, dy2-30),(dx2+30, dy2-18),(dx2, dy2-8)], fill=(234, 67, 53))

    # ── Top navigation bar (dark) ─────────────────────────────────────────
    d.rectangle([0, 0, w, h//9], fill=(255, 255, 255))
    d.line([(0, h//9), (w, h//9)], fill=(200, 200, 200), width=1)
    # Search bar
    d.rounded_rectangle([w//20, h//36, w*9//10, h//9 - h//36],
                        radius=h//30, fill=(240, 240, 240), outline=(200,200,200))
    d.text((w//10, h//18), "1600 Amphitheatre Pkwy, Mountain View",
           fill=(60, 60, 60), font=font_ui, anchor="lm")
    # Mic icon (circle)
    d.ellipse([w*17//20, h//36+4, w*9//10-4, h//9-h//36-4], fill=(66,133,244))

    # ── Turn-by-turn instruction bar (bottom) ────────────────────────────
    bar_h2 = h // 7
    d.rectangle([0, h - bar_h2, w, h], fill=(66, 133, 244))
    # Arrow symbol
    aw = bar_h2 * 2 // 3
    ax, ay = w//12, h - bar_h2 + bar_h2//2
    arrow_pts = [(ax, ay-aw//2),(ax+aw//2, ay-aw//2),(ax+aw//2, ay-aw),
                 (ax+aw, ay),(ax+aw//2, ay+aw),(ax+aw//2, ay+aw//2),(ax, ay+aw//2)]
    d.polygon(arrow_pts, fill=(255, 255, 255))
    # Instruction text
    d.text((ax + aw + 20, h - bar_h2 + bar_h2//3),
           "Turn right onto Main St", fill=(255, 255, 255), font=font_ui)
    d.text((ax + aw + 20, h - bar_h2 + bar_h2*2//3),
           "In 200 m  |  ETA 12 min  |  3.4 km", fill=(200, 230, 255), font=font_small)

    img_arr[y0:y0+h, x0:x0+w] = np.array(img)


def _draw_mm_panel(img_arr, x0, y0, w, h):
    """Draw YouTube-style Multimedia panel into img_arr."""
    img = Image.fromarray(img_arr[y0:y0+h, x0:x0+w])
    d = ImageDraw.Draw(img)

    try:
        font_title  = ImageFont.truetype("arialbd.ttf", max(20, h//30))
        font_chan   = ImageFont.truetype("arial.ttf",   max(14, h//50))
        font_small  = ImageFont.truetype("arial.ttf",   max(11, h//65))
        font_time   = ImageFont.truetype("arialbd.ttf", max(13, h//55))
    except Exception:
        font_title = font_chan = font_small = font_time = ImageFont.load_default()

    # ── YouTube dark background ───────────────────────────────────────────
    d.rectangle([0, 0, w, h], fill=(15, 15, 15))

    # ── Video viewport ────────────────────────────────────────────────────
    vid_x0, vid_y0 = 0, 0
    vid_x1, vid_y1 = w, int(h * 0.82)
    vid_w = vid_x1 - vid_x0
    vid_h = vid_y1 - vid_y0

    # Sky gradient (top of video scene)
    sky_h = vid_h * 2 // 3
    for row in range(sky_h):
        t = row / sky_h
        r = int(30  + t * 100)
        g = int(80  + t * 120)
        b = int(160 + t * 80)
        img.putpixel((0, vid_y0 + row), (r, g, b))  # placeholder; fill below
    sky_arr = np.zeros((sky_h, vid_w, 3), dtype=np.uint8)
    for row in range(sky_h):
        t = row / sky_h
        sky_arr[row, :] = [int(30+t*100), int(80+t*120), int(160+t*80)]
    img_np = np.array(img)
    img_np[vid_y0:vid_y0+sky_h, vid_x0:vid_x1] = sky_arr
    img = Image.fromarray(img_np)
    d = ImageDraw.Draw(img)

    # Ground
    d.rectangle([vid_x0, vid_y0+sky_h, vid_x1, vid_y1], fill=(60, 120, 40))

    # Sun
    sun_x, sun_y = vid_w * 3 // 4, vid_h // 5
    sun_r = max(30, vid_h // 12)
    d.ellipse([sun_x-sun_r, sun_y-sun_r, sun_x+sun_r, sun_y+sun_r],
              fill=(255, 240, 100))
    for angle in range(0, 360, 30):
        import math as _m
        rx = sun_x + int((sun_r+15)*_m.cos(_m.radians(angle)))
        ry = sun_y + int((sun_r+15)*_m.sin(_m.radians(angle)))
        d.line([(sun_x + int(sun_r*_m.cos(_m.radians(angle))),
                 sun_y + int(sun_r*_m.sin(_m.radians(angle)))),
                (rx, ry)], fill=(255, 230, 80), width=max(2, vid_h//120))

    # Clouds
    for cx2, cy2, cr in [(vid_w//5, vid_h//6, vid_h//14),
                         (vid_w//3, vid_h//8, vid_h//18),
                         (vid_w//2, vid_h//5, vid_h//12)]:
        for dc in [(-cr//2, 0), (0, -cr//3), (cr//2, 0), (0, cr//3)]:
            d.ellipse([cx2+dc[0]-cr//2, cy2+dc[1]-cr//2,
                       cx2+dc[0]+cr//2, cy2+dc[1]+cr//2], fill=(230,240,255))

    # Mountains
    mtn_pts = [(0, vid_y0+sky_h),
               (vid_w//6,  vid_y0+sky_h - vid_h//4),
               (vid_w//4,  vid_y0+sky_h),
               (vid_w*2//5, vid_y0+sky_h - vid_h//3),
               (vid_w//2,  vid_y0+sky_h),
               (vid_w*2//3, vid_y0+sky_h - vid_h//5),
               (vid_w,     vid_y0+sky_h)]
    d.polygon(mtn_pts, fill=(80, 100, 80))
    # Snow caps
    d.polygon([(vid_w//4-20, vid_y0+sky_h-vid_h//4+20),
               (vid_w//6,   vid_y0+sky_h-vid_h//4),
               (vid_w//4+20, vid_y0+sky_h-vid_h//4+20)], fill=(240,245,255))
    d.polygon([(vid_w*2//5-25, vid_y0+sky_h-vid_h//3+25),
               (vid_w*2//5,   vid_y0+sky_h-vid_h//3),
               (vid_w*2//5+25, vid_y0+sky_h-vid_h//3+25)], fill=(240,245,255))

    # Road in video
    road_y = vid_y1 - vid_h // 6
    d.trapezoid = None  # not available in older Pillow
    d.polygon([(vid_w//2-20, vid_y1),
               (vid_w//2+20, vid_y1),
               (vid_w//2+6,  road_y),
               (vid_w//2-6,  road_y)], fill=(80, 80, 80))
    # Dashed centre line
    for dy3 in range(road_y, vid_y1, 20):
        d.rectangle([vid_w//2-2, dy3, vid_w//2+2, dy3+10], fill=(255,255,255))

    # ── YouTube video overlay controls ────────────────────────────────────
    ctrl_h = int(h * 0.18)
    ctrl_y = vid_y1
    # Gradient overlay at bottom of video (dim)
    grad_arr2 = np.array(img)
    for row in range(max(1, vid_h//5)):
        alpha = row / (vid_h//5)
        grad_arr2[vid_y1 - vid_h//5 + row, vid_x0:vid_x1] = (
            grad_arr2[vid_y1 - vid_h//5 + row, vid_x0:vid_x1] * (1-alpha*0.7)
        ).astype(np.uint8)
    img = Image.fromarray(grad_arr2)
    d = ImageDraw.Draw(img)

    # Time overlay on video (top-left of video)
    d.text((15, 15), "LIVE", fill=(255, 255, 255), font=font_time)
    d.rectangle([10, 10, 10 + 50, 10 + 24], outline=(255,255,255), width=1)

    # ── YouTube controls bar ──────────────────────────────────────────────
    d.rectangle([0, ctrl_y, w, h], fill=(15, 15, 15))

    # Progress bar background
    prog_y = ctrl_y + ctrl_h // 5
    d.rectangle([0, prog_y, w, prog_y + max(4, h//120)], fill=(80, 80, 80))
    # Buffered (grey)
    d.rectangle([0, prog_y, int(w * 0.55), prog_y + max(4, h//120)],
                fill=(160, 160, 160))
    # Played (YouTube red)
    played_x = int(w * 0.35)
    d.rectangle([0, prog_y, played_x, prog_y + max(4, h//120)],
                fill=(255, 0, 0))
    # Scrubber dot
    dot_r = max(6, h//80)
    d.ellipse([played_x - dot_r, prog_y - dot_r + max(2, h//240),
               played_x + dot_r, prog_y + dot_r + max(2, h//240)],
              fill=(255, 0, 0))

    # Control icons row
    icon_y = ctrl_y + ctrl_h * 2 // 5
    icon_sz = max(16, h // 45)

    # Play button (triangle)
    d.polygon([(30, icon_y - icon_sz),
               (30 + icon_sz*2, icon_y),
               (30, icon_y + icon_sz)], fill=(255, 255, 255))

    # Skip-forward button
    sk_x = 30 + icon_sz * 3
    d.polygon([(sk_x, icon_y-icon_sz),
               (sk_x+icon_sz, icon_y),
               (sk_x, icon_y+icon_sz)], fill=(200,200,200))
    d.rectangle([sk_x+icon_sz, icon_y-icon_sz, sk_x+icon_sz+4, icon_y+icon_sz],
                fill=(200,200,200))

    # Volume icon
    vx = sk_x + icon_sz * 4
    d.polygon([(vx, icon_y-icon_sz//2),(vx+icon_sz//2, icon_y-icon_sz),
               (vx+icon_sz//2, icon_y+icon_sz),(vx, icon_y+icon_sz//2)],
              fill=(200,200,200))
    d.arc([vx+icon_sz//2, icon_y-icon_sz, vx+icon_sz*3//2, icon_y+icon_sz],
          start=-60, end=60, fill=(200,200,200), width=max(2,h//200))

    # Time text
    d.text((vx + icon_sz*2 + 10, icon_y), "4:32 / 12:48",
           fill=(200, 200, 200), font=font_time, anchor="lm")

    # Fullscreen icon (top-right corner arrows)
    fs_x = w - 50
    fs_sz = icon_sz
    d.line([(fs_x, icon_y-fs_sz),(fs_x+fs_sz//2, icon_y-fs_sz)], fill=(200,200,200), width=2)
    d.line([(fs_x, icon_y-fs_sz),(fs_x, icon_y-fs_sz//2)], fill=(200,200,200), width=2)
    d.line([(fs_x+fs_sz, icon_y+fs_sz),(fs_x+fs_sz//2, icon_y+fs_sz)], fill=(200,200,200), width=2)
    d.line([(fs_x+fs_sz, icon_y+fs_sz),(fs_x+fs_sz, icon_y+fs_sz//2)], fill=(200,200,200), width=2)

    # Settings gear (circle placeholder)
    d.ellipse([fs_x - icon_sz*3, icon_y-icon_sz//2,
               fs_x - icon_sz*3 + icon_sz, icon_y+icon_sz//2],
              outline=(200,200,200), width=2)

    # Title + channel below controls
    title_y = ctrl_y + ctrl_h * 3 // 4
    d.text((15, title_y), "Scenic Mountain Drive 4K - Nature Relaxation",
           fill=(255, 255, 255), font=font_title)
    d.text((15, title_y + int(h*0.07)),
           "NatureScapes  *  2.1M views  *  1 year ago",
           fill=(170, 170, 170), font=font_chan)

    # YouTube logo (red rectangle + white play)
    yt_x, yt_y = w - 160, title_y
    d.rounded_rectangle([yt_x, yt_y, yt_x+110, yt_y+44], radius=8, fill=(255, 0, 0))
    d.polygon([(yt_x+35, yt_y+10),(yt_x+80, yt_y+22),(yt_x+35, yt_y+34)],
              fill=(255, 255, 255))
    d.text((yt_x+85, yt_y+22), "YouTube", fill=(255,255,255), font=font_chan, anchor="lm")

    img_arr[y0:y0+h, x0:x0+w] = np.array(img)


def _pil_to_png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_superframe(sf_w, sf_h):
    """Build a 3840x1080 (or sf_w x sf_h) superframe numpy array."""
    arr = np.zeros((sf_h, sf_w, 3), dtype=np.uint8)
    half_w = sf_w // 2
    _draw_nav_panel(arr, 0,      0, half_w, sf_h)
    _draw_mm_panel (arr, half_w, 0, half_w, sf_h)
    return arr


def _add_labels(arr, sf_w, sf_h):
    """Overlay text labels using PIL."""
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    half_w = sf_w // 2

    try:
        font_big  = ImageFont.truetype("arial.ttf", 72)
        font_small = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        font_big  = ImageFont.load_default()
        font_small = font_big

    # Navigation label
    draw.text((half_w // 2, sf_h // 2 - 80),  "NAVIGATION",
              fill=(255,255,255), font=font_big,  anchor="mm")
    draw.text((half_w // 2, sf_h // 2 + 10),  "Left Panel  |  1920 x 1080",
              fill=(180,220,255), font=font_small, anchor="mm")

    # Multimedia label
    draw.text((half_w + half_w // 2, sf_h // 2 - 80), "MULTIMEDIA",
              fill=(255,255,255), font=font_big,  anchor="mm")
    draw.text((half_w + half_w // 2, sf_h // 2 + 10), "Right Panel  |  1920 x 1080",
              fill=(255,200,160), font=font_small, anchor="mm")

    # Divider line
    draw.line([(half_w, 0), (half_w, sf_h)], fill=(255,255,0), width=4)

    return np.array(img)


def _make_interleaved(arr, sf_w, sf_h):
    """Column-interleave: even cols from left panel, odd cols from right panel."""
    half_w = sf_w // 2
    left  = arr[:, :half_w, :]    # Navigation  (1920 columns)
    right = arr[:, half_w:, :]    # Multimedia  (1920 columns)

    out = np.empty_like(arr)
    out[:, 0::2, :] = left   # even output columns â† Navigation
    out[:, 1::2, :] = right  # odd  output columns â† Multimedia
    return out


def _add_interleave_labels(arr, sf_w, sf_h):
    """Return the interleaved image as-is (no text overlays)."""
    return arr.copy()


with edp_sub3:
    # ── Per-stream bandwidth feasibility (each stream = 2 lanes) ──────────
    st.markdown("### Per-Stream Bandwidth Feasibility (2 Lanes per Stream)")
    px_per_stream_2x2   = total_pixels / 2
    pclk_per_stream_2x2 = px_per_stream_2x2 * fps * (1 + blank_ratio) / 1e6

    st.markdown("##### Max Active Pixels per Frame (MP)")
    mp22_tbl = {"2 Lanes": {f"{lr} Gbps": _edp_mp(2, lr) / 1e6 for lr in EDP_LINK_RATES}}
    df_mp22 = pd.DataFrame(mp22_tbl).T; df_mp22.index.name = "Lanes \\ Rate"
    st.dataframe(df_mp22.style.map(lambda v: cm(v, px_per_stream_2x2)).format("{:.3f} MP"),
                 use_container_width=True)
    st.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-stream target resolution "
        f"({px_per_stream_2x2/1e6:.3f} MP)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-stream target resolution"
    )

    st.markdown("##### Maximum PCLK (MHz)")
    mpclk22_tbl = {"2 Lanes": {f"{lr} Gbps": _edp_mp(2, lr) * fps * (1 + blank_ratio) / 1e6
                                for lr in EDP_LINK_RATES}}
    df_mpclk22 = pd.DataFrame(mpclk22_tbl).T; df_mpclk22.index.name = "Lanes \\ Rate"
    st.dataframe(df_mpclk22.style.map(lambda v: cm(v, pclk_per_stream_2x2*1e6)).format("{:.2f} MHz"),
                 use_container_width=True)
    st.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-stream target pixel clock "
        f"({pclk_per_stream_2x2:.2f} MHz)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-stream target pixel clock"
    )

    st.markdown("---")
    st.markdown('<h3 class="section-header">MSO 2x2 — Superframe Visualisation</h3>',
                unsafe_allow_html=True)

    st.info(
        "**MSO 2×2 mode** (N×M notation): **2 independent video streams**, each carried by **2 physical lanes**"
        " → 4 total lanes required (L0+L1 → Stream 0, L2+L3 → Stream 1).  \n"
        "The display is split into **2 horizontal tiles** (left = Navigation, right = Multimedia), "
        "each tile driven by its own stream.  \n"
        "The SoC packs both tiles into a single **superframe** and column-interleaves them before "
        "sending over the eDP link. The eDP controller de-interleaves and routes each stream to the correct tile."
    )

    # ── Controls ─────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    sf_w_in = c1.selectbox("Superframe Width",  [3840, 2560, 1920], index=0)
    sf_h_in = c2.selectbox("Superframe Height", [1080, 720],        index=0)
    sf_w, sf_h = int(sf_w_in), int(sf_h_in)

    # ── Step 1 : Original superframe ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### Step 1 — Original Superframe")
    st.markdown(
        f"Left half **({sf_w//2}×{sf_h})** = Navigation &nbsp;|&nbsp; "
        f"Right half **({sf_w//2}×{sf_h})** = Multimedia  \n"
        "Yellow divider marks the centre split.",
        unsafe_allow_html=True
    )

    with st.spinner("Generating superframe image..."):
        _sf_arr    = _make_superframe(sf_w, sf_h)
        _sf_arr    = _add_labels(_sf_arr, sf_w, sf_h)
        _sf_img    = Image.fromarray(_sf_arr)
        _sf_bytes  = _pil_to_png_bytes(_sf_img)

    st.image(_sf_img, use_container_width=True,
             caption=f"Original Superframe  {sf_w}×{sf_h} — Navigation (left) + Multimedia (right)")

    st.download_button(
        label="â¬‡️ Download Original Superframe (PNG)",
        data=_sf_bytes,
        file_name=f"mso2x2_superframe_{sf_w}x{sf_h}.png",
        mime="image/png",
        type="primary",
    )

    # ── Step 2 : Interleave mode selection ────────────────────────────────
    st.markdown("---")
    st.markdown("### Step 2 — Lane Mapping Mode")
    interleave_mode = st.radio(
        "Lane mapping mode",
        ["Column-interleave", "Non-column-interleave"],
        horizontal=True,
        key="mso2x2_interleave_mode",
    )

    if interleave_mode == "Column-interleave":
        st.markdown("#### Column-Interleaved Superframe")
        st.markdown(
            "Each pair of adjacent output columns is formed by taking **one column from Navigation** "
            "and **one column from Multimedia** alternately:  \n"
            "- **Even columns** (0, 2, 4, …) â† Navigation pixel at column 0, 1, 2, …  \n"
            "- **Odd columns**  (1, 3, 5, …) â† Multimedia pixel at column 0, 1, 2, …  \n\n"
            "The eDP controller de-interleaves this back into two independent **streams**:  \n"
            "**Stream 0** (Navigation) and **Stream 1** (Multimedia), each `{w}×{h}`.".format(
                w=sf_w//2, h=sf_h),
            unsafe_allow_html=True
        )

        with st.spinner("Generating interleaved image and streams..."):
            _il_arr   = _make_interleaved(_sf_arr, sf_w, sf_h)
            _il_arr_l = _add_interleave_labels(_il_arr, sf_w, sf_h)
            _il_img   = Image.fromarray(_il_arr_l)
            _il_bytes = _pil_to_png_bytes(_il_img)

            # Crop left and right halves of the interleaved image
            _stream0_arr = _il_arr_l[:, :sf_w//2, :]    # left half of interleaved image
            _stream1_arr = _il_arr_l[:, sf_w//2:, :]    # right half of interleaved image
            _stream0_img = Image.fromarray(_stream0_arr)
            _stream1_img = Image.fromarray(_stream1_arr)
            _stream0_bytes = _pil_to_png_bytes(_stream0_img)
            _stream1_bytes = _pil_to_png_bytes(_stream1_img)

        st.image(_il_img, use_container_width=True,
                 caption=f"Column-Interleaved Superframe  {sf_w}×{sf_h}")

        st.download_button(
            label="â¬‡️ Download Interleaved Superframe (PNG)",
            data=_il_bytes,
            file_name=f"mso2x2_interleaved_{sf_w}x{sf_h}.png",
            mime="image/png",
            type="primary",
        )
    else:
        st.markdown("#### Non-Column-Interleaved Superframe")
        st.markdown(
            "Each tile is sent to the MSO link **without column-interleaving** between tiles. "
            "Within each tile, columns are split by **odd/even position** across a pair of lanes:  \n"
            f"1. **Navigation (left, {sf_w//2}×{sf_h})** → mapped to **Lanes 0 & 1** "
            "— Lane 0 carries odd-position pixels, Lane 1 carries even-position pixels.  \n"
            f"2. **Multimedia (right, {sf_w//2}×{sf_h})** → mapped to **Lanes 2 & 3** "
            "— Lane 2 carries odd-position pixels, Lane 3 carries even-position pixels.",
            unsafe_allow_html=True
        )

        with st.spinner("Generating non-interleaved image and streams..."):
            _il_arr_l = _sf_arr.copy()
            _il_img   = Image.fromarray(_il_arr_l)
            _il_bytes = _pil_to_png_bytes(_il_img)

            # Crop left and right halves (Navigation / Multimedia tiles)
            _stream0_arr = _il_arr_l[:, :sf_w//2, :]    # Navigation tile → Lanes 0/1
            _stream1_arr = _il_arr_l[:, sf_w//2:, :]    # Multimedia tile → Lanes 2/3
            _stream0_img = Image.fromarray(_stream0_arr)
            _stream1_img = Image.fromarray(_stream1_arr)
            _stream0_bytes = _pil_to_png_bytes(_stream0_img)
            _stream1_bytes = _pil_to_png_bytes(_stream1_img)

        st.image(_il_img, use_container_width=True,
                 caption=f"Non-Column-Interleaved Superframe  {sf_w}×{sf_h}")

        st.download_button(
            label="â¬‡️ Download Non-Interleaved Superframe (PNG)",
            data=_il_bytes,
            file_name=f"mso2x2_noninterleaved_{sf_w}x{sf_h}.png",
            mime="image/png",
            type="primary",
        )

    # ── Left / Right half downloads of the interleaved image ─────────────
    st.markdown("---")
    if interleave_mode == "Column-interleave":
        st.markdown("### Download Interleaved — Left & Right Halves")
        st.markdown(
            f"Left half and right half of the column-interleaved superframe, "
            f"each **{sf_w//2}×{sf_h}**. Both halves contain mixed Navigation + "
            f"Multimedia pixels (alternating columns).",
            unsafe_allow_html=True
        )

        sc1, sc2 = st.columns(2)

        with sc1:
            st.markdown("#### ◀️ Left Half")
            st.image(_stream0_img, use_container_width=True,
                     caption=f"Interleaved Left Half  {sf_w//2}×{sf_h}")
            st.download_button(
                label="â¬‡️ Download Interleaved Left Half (PNG)",
                data=_stream0_bytes,
                file_name=f"mso2x2_interleaved_left_{sf_w//2}x{sf_h}.png",
                mime="image/png",
                type="primary",
                use_container_width=True,
            )

        with sc2:
            st.markdown("#### ▶️ Right Half")
            st.image(_stream1_img, use_container_width=True,
                     caption=f"Interleaved Right Half  {sf_w//2}×{sf_h}")
            st.download_button(
                label="â¬‡️ Download Interleaved Right Half (PNG)",
                data=_stream1_bytes,
                file_name=f"mso2x2_interleaved_right_{sf_w//2}x{sf_h}.png",
                mime="image/png",
                type="primary",
                use_container_width=True,
            )
    else:
        st.markdown("### Download Tiles — Navigation & Multimedia (per-Lane-Pair)")
        st.markdown(
            f"Navigation and Multimedia tiles, each **{sf_w//2}×{sf_h}**, sent "
            f"**without column-interleaving** between tiles:  \n"
            f"- **Navigation** → **Lanes 0 & 1** (Lane 0 = odd-position pixels, Lane 1 = even-position pixels)  \n"
            f"- **Multimedia** → **Lanes 2 & 3** (Lane 2 = odd-position pixels, Lane 3 = even-position pixels)",
            unsafe_allow_html=True
        )

        sc1, sc2 = st.columns(2)

        with sc1:
            st.markdown("#### ◀️ Navigation (Lanes 0 & 1)")
            st.image(_stream0_img, use_container_width=True,
                     caption=f"Navigation Tile  {sf_w//2}×{sf_h}  → Lanes 0/1")
            st.download_button(
                label="â¬‡️ Download Navigation Tile (PNG)",
                data=_stream0_bytes,
                file_name=f"mso2x2_noninterleaved_navigation_{sf_w//2}x{sf_h}.png",
                mime="image/png",
                type="primary",
                use_container_width=True,
            )

        with sc2:
            st.markdown("#### ▶️ Multimedia (Lanes 2 & 3)")
            st.image(_stream1_img, use_container_width=True,
                     caption=f"Multimedia Tile  {sf_w//2}×{sf_h}  → Lanes 2/3")
            st.download_button(
                label="â¬‡️ Download Multimedia Tile (PNG)",
                data=_stream1_bytes,
                file_name=f"mso2x2_noninterleaved_multimedia_{sf_w//2}x{sf_h}.png",
                mime="image/png",
                type="primary",
                use_container_width=True,
            )

    # ── Zoom-in comparison ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Pixel-level Zoom")
    st.caption("Select a region (start column, start row, width, height) to zoom into.")

    za, zb, zc, zd = st.columns(4)
    zoom_col_start = int(za.number_input("Start column", min_value=0,
        max_value=sf_w-2, value=0, step=1))
    zoom_row_start = int(zb.number_input("Start row",    min_value=0,
        max_value=sf_h-2, value=0,   step=1))
    zoom_cols      = int(zc.number_input("Columns to show", min_value=1,
        max_value=sf_w,   value=200,  step=1))
    zoom_rows      = int(zd.number_input("Rows to show",    min_value=1,
        max_value=sf_h,   value=200, step=1))

    # Clamp to image bounds
    zoom_cols = min(zoom_cols, sf_w - zoom_col_start)
    zoom_rows = min(zoom_rows, sf_h - zoom_row_start)
    col_end   = zoom_col_start + zoom_cols - 1
    row_end   = zoom_row_start + zoom_rows - 1

    # Crop from the Step 2 interleaved image
    il_crop = _il_arr_l[zoom_row_start:zoom_row_start+zoom_rows,
                        zoom_col_start:zoom_col_start+zoom_cols, :]

    # Scale up with nearest-neighbour so every pixel is a crisp solid block
    DISPLAY_W = 1200
    scale = max(1, DISPLAY_W // max(zoom_cols, 1))
    display_w = zoom_cols * scale
    display_h = zoom_rows * scale
    il_crop_img = Image.fromarray(il_crop).resize(
        (display_w, display_h), resample=Image.NEAREST)

    st.image(il_crop_img, use_container_width=False,
             caption=f"Interleaved Superframe (Step 2) — cols {zoom_col_start}–{col_end}, "
                     f"rows {zoom_row_start}–{row_end}  ({zoom_cols}×{zoom_rows} px, "
                     f"displayed at {scale}x scale)")

    st.caption(
        "In the interleaved strip you can see the colours from Navigation and Multimedia "
        "alternating every single column — exactly what the eDP MSO controller receives."
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MSO helper – extra panels for 4×1 (rear camera + climate)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def _draw_camera_panel(img_arr, x0, y0, w, h):
    """Rear-view camera panel."""
    img = Image.fromarray(img_arr[y0:y0+h, x0:x0+w])
    d   = ImageDraw.Draw(img)
    try:
        font_big   = ImageFont.truetype("arialbd.ttf", max(18, h//35))
        font_small = ImageFont.truetype("arial.ttf",   max(11, h//65))
    except Exception:
        font_big = font_small = ImageFont.load_default()

    # Dark asphalt background
    d.rectangle([0, 0, w, h], fill=(30, 30, 30))

    # Sky strip at top
    sky_h = h // 3
    for row in range(sky_h):
        t = row / sky_h
        img_arr_row = [int(80+t*60), int(100+t*80), int(120+t*100)]
        d.line([(0, row), (w, row)], fill=tuple(img_arr_row))

    # Ground (asphalt)
    d.rectangle([0, sky_h, w, h], fill=(45, 45, 45))

    # Road lane markings
    for gx in range(w//4, w, w//4):
        d.line([(gx, sky_h), (gx, h)], fill=(200, 200, 0), width=max(2, w//120))
    # Centre dashed line
    for dy in range(sky_h, h, 30):
        d.rectangle([w//2-3, dy, w//2+3, dy+18], fill=(255, 255, 255))

    # Car silhouette (the vehicle ahead)
    cx2, cy2 = w//2, sky_h + (h-sky_h)//3
    car_w, car_h2 = w//5, (h-sky_h)//5
    d.rectangle([cx2-car_w//2, cy2, cx2+car_w//2, cy2+car_h2], fill=(180, 60, 60))
    d.rectangle([cx2-car_w//3, cy2-car_h2//2, cx2+car_w//3, cy2+car_h2//4],
                fill=(140, 40, 40))
    # Tail lights
    d.rectangle([cx2-car_w//2, cy2+car_h2-8, cx2-car_w//2+14, cy2+car_h2],
                fill=(255, 50, 50))
    d.rectangle([cx2+car_w//2-14, cy2+car_h2-8, cx2+car_w//2, cy2+car_h2],
                fill=(255, 50, 50))

    # Parking guide lines (overlay)
    guide_color = (0, 255, 180)
    gw2 = int(w * 0.55)
    d.line([(w//2-gw2//2, h-10), (w//2-gw2//3, sky_h+10)], fill=guide_color, width=3)
    d.line([(w//2+gw2//2, h-10), (w//2+gw2//3, sky_h+10)], fill=guide_color, width=3)
    d.line([(w//2-gw2//2, h-10), (w//2+gw2//2, h-10)],     fill=guide_color, width=3)

    # Distance warning bar
    d.rectangle([0, h-h//10, w, h], fill=(60, 60, 0))
    d.text((w//2, h-h//20), "Distance: 8 m  |  CAUTION",
           fill=(255, 220, 0), font=font_small, anchor="mm")

    # Camera label
    d.rectangle([0, 0, w, h//10], fill=(0, 0, 0))
    d.text((w//2, h//20), "REAR CAMERA", fill=(0, 220, 255), font=font_big, anchor="mm")

    img_arr[y0:y0+h, x0:x0+w] = np.array(img)


def _draw_climate_panel(img_arr, x0, y0, w, h):
    """Climate / HVAC control panel."""
    img = Image.fromarray(img_arr[y0:y0+h, x0:x0+w])
    d   = ImageDraw.Draw(img)
    try:
        font_big   = ImageFont.truetype("arialbd.ttf", max(20, h//30))
        font_med   = ImageFont.truetype("arialbd.ttf", max(14, h//50))
        font_small = ImageFont.truetype("arial.ttf",   max(11, h//65))
    except Exception:
        font_big = font_med = font_small = ImageFont.load_default()

    # Dark panel background
    d.rectangle([0, 0, w, h], fill=(18, 22, 30))

    # Title bar
    d.rectangle([0, 0, w, h//9], fill=(25, 35, 55))
    d.text((w//2, h//18), "CLIMATE CONTROL", fill=(100, 200, 255), font=font_big, anchor="mm")

    # ── Left zone (Driver) ────────────────────────────────────────────────
    zone_w = w // 2 - 10
    # Temp display
    d.text((zone_w//2, h//5), "DRIVER", fill=(160, 160, 160), font=font_small, anchor="mm")
    d.text((zone_w//2, h*2//5), "22°C", fill=(255, 255, 255), font=font_big, anchor="mm")
    # Arc (dial)
    arc_r = min(zone_w, h//3) // 2
    arc_cx, arc_cy = zone_w//2, h*2//5
    d.arc([arc_cx-arc_r, arc_cy-arc_r, arc_cx+arc_r, arc_cy+arc_r],
          start=140, end=400, fill=(0, 180, 255), width=max(4, h//80))
    # Fan speed dots
    d.text((zone_w//2, h*3//5), "Fan", fill=(120, 120, 120), font=font_small, anchor="mm")
    for i in range(5):
        dot_x = zone_w//4 + i * zone_w//6
        color = (0, 180, 255) if i < 3 else (50, 50, 70)
        d.ellipse([dot_x-8, h*3//5+14, dot_x+8, h*3//5+30], fill=color)
    # AC / Auto buttons
    for bx, lbl, active in [(zone_w//4, "A/C", True), (zone_w*3//4, "AUTO", False)]:
        bc = (0, 120, 200) if active else (40, 40, 60)
        d.rounded_rectangle([bx-30, h*4//5-18, bx+30, h*4//5+18], radius=8, fill=bc)
        d.text((bx, h*4//5), lbl, fill=(255,255,255), font=font_small, anchor="mm")

    # Divider
    d.line([(w//2, h//9+10), (w//2, h-10)], fill=(50, 60, 80), width=2)

    # ── Right zone (Passenger) ────────────────────────────────────────────
    rx = w//2 + 10
    d.text((rx + zone_w//2, h//5), "PASSENGER", fill=(160,160,160), font=font_small, anchor="mm")
    d.text((rx + zone_w//2, h*2//5), "20°C", fill=(255, 200, 100), font=font_big, anchor="mm")
    arc_cx2 = rx + zone_w//2
    d.arc([arc_cx2-arc_r, arc_cy-arc_r, arc_cx2+arc_r, arc_cy+arc_r],
          start=140, end=360, fill=(255, 160, 0), width=max(4, h//80))
    d.text((arc_cx2, h*3//5), "Fan", fill=(120,120,120), font=font_small, anchor="mm")
    for i in range(5):
        dot_x = rx + zone_w//4 + i * zone_w//6
        color = (255, 160, 0) if i < 2 else (50, 50, 70)
        d.ellipse([dot_x-8, h*3//5+14, dot_x+8, h*3//5+30], fill=color)
    for bx2, lbl2, active2 in [(rx+zone_w//4, "A/C", False), (rx+zone_w*3//4, "AUTO", True)]:
        bc2 = (0, 120, 200) if active2 else (40, 40, 60)
        d.rounded_rectangle([bx2-30, h*4//5-18, bx2+30, h*4//5+18], radius=8, fill=bc2)
        d.text((bx2, h*4//5), lbl2, fill=(255,255,255), font=font_small, anchor="mm")

    img_arr[y0:y0+h, x0:x0+w] = np.array(img)


def _make_superframe_nx1(sf_w, sf_h, n_streams):
    """Build an n-stream horizontal superframe (n panels side by side)."""
    arr     = np.zeros((sf_h, sf_w, 3), dtype=np.uint8)
    tile_w  = sf_w // n_streams
    panels  = [_draw_nav_panel, _draw_camera_panel, _draw_climate_panel, _draw_mm_panel]
    for i in range(n_streams):
        panels[i % len(panels)](arr, i * tile_w, 0, tile_w, sf_h)
    return arr


def _add_labels_nx1(arr, sf_w, sf_h, n_streams, panel_names):
    """Add centre label + dividers for n-stream superframe."""
    img  = Image.fromarray(arr)
    d    = ImageDraw.Draw(img)
    try:
        font_big   = ImageFont.truetype("arialbd.ttf", max(40, sf_h//18))
        font_small = ImageFont.truetype("arial.ttf",   max(22, sf_h//35))
    except Exception:
        font_big = font_small = ImageFont.load_default()

    tile_w = sf_w // n_streams
    for i in range(n_streams):
        cx = i * tile_w + tile_w // 2
        d.text((cx, sf_h//2 - 50), panel_names[i],
               fill=(255, 255, 255), font=font_big,  anchor="mm")
        d.text((cx, sf_h//2 + 10), f"Stream {i}  |  {tile_w}×{sf_h}",
               fill=(220, 220, 180), font=font_small, anchor="mm")
        if i > 0:
            d.line([(i*tile_w, 0), (i*tile_w, sf_h)], fill=(255, 255, 0), width=4)
    return np.array(img)


def _make_interleaved_nx1(arr, sf_w, sf_h, n_streams):
    """Column-interleave n streams: col % n_streams determines the source panel."""
    tile_w = sf_w // n_streams
    out    = np.empty_like(arr)
    for i in range(n_streams):
        src = arr[:, i*tile_w:(i+1)*tile_w, :]   # source panel i
        out[:, i::n_streams, :] = src             # every n-th output col
    return out


def _mso_superframe_ui(sub, ns, lps, mode_label, panel_names, sf_caption):
    """Reusable UI block for any MSO N×1 / N×M superframe tab."""
    sub.markdown(f'<h3 class="section-header">{mode_label} — Superframe Visualisation</h3>',
                 unsafe_allow_html=True)

    total_lanes = ns * lps
    lane_assign = "  |  ".join(
        f"L{i*lps}{'–'+str(i*lps+lps-1) if lps>1 else ''}→S{i}" for i in range(ns))
    sub.info(
        f"**{mode_label}** (N×M notation): **{ns} independent video streams**, "
        f"each carried by **{lps} physical lane{'s' if lps>1 else ''}** "
        f"→ {total_lanes} total lanes required.  \n"
        f"Lane assignment: {lane_assign}  \n"
        f"The display is split into **{ns} horizontal tiles**, each driven by its own stream.  \n"
        f"The SoC packs all tiles into a single **superframe** and column-interleaves them "
        f"({ns}-way cycle). The eDP controller de-interleaves and routes each stream to the correct tile."
    )

    c1, c2 = sub.columns(2)
    sf_w = int(c1.selectbox("Superframe Width",  [3840, 2560, 1920],
                            index=0, key=f"sf_w_{mode_label}"))
    sf_h = int(c2.selectbox("Superframe Height", [1080, 720],
                            index=0, key=f"sf_h_{mode_label}"))
    tile_w = sf_w // ns

    # ── Step 1 ───────────────────────────────────────────────────────────
    sub.markdown("---")
    sub.markdown("### Step 1 — Original Superframe")
    sub.markdown(
        "  |  ".join(f"Panel {i} **({tile_w}×{sf_h})** = {panel_names[i]}"
                     for i in range(ns)) +
        "  \nYellow dividers mark tile boundaries.",
        unsafe_allow_html=True
    )

    with sub.container():
        with st.spinner("Generating superframe..."):
            sf_arr   = _make_superframe_nx1(sf_w, sf_h, ns)
            sf_arr   = _add_labels_nx1(sf_arr, sf_w, sf_h, ns, panel_names)
            sf_img   = Image.fromarray(sf_arr)
            sf_bytes = _pil_to_png_bytes(sf_img)

    sub.image(sf_img, use_container_width=True, caption=sf_caption.format(sf_w=sf_w, sf_h=sf_h))
    sub.download_button(
        label="â¬‡️ Download Original Superframe (PNG)",
        data=sf_bytes,
        file_name=f"mso_{mode_label.replace('×','x').replace(' ','_')}_superframe_{sf_w}x{sf_h}.png",
        mime="image/png", type="primary",
        key=f"dl_sf_{mode_label}"
    )

    # ── Step 2 ───────────────────────────────────────────────────────────
    sub.markdown("---")
    sub.markdown("### Step 2 — Lane Mapping Mode")

    interleave_mode = "Column-interleave"
    if ns in (2, 4):
        interleave_mode = sub.radio(
            "Lane mapping mode",
            ["Column-interleave", "Non-column-interleave"],
            horizontal=True,
            key=f"interleave_mode_{mode_label}",
        )

    if interleave_mode == "Column-interleave":
        sub.markdown("#### Column-Interleaved Superframe")
        interleave_desc = "  \n".join(
            f"- **Columns {i}, {i+ns}, {i+ns*2}, …** â† {panel_names[i]} (Stream {i})"
            for i in range(ns))
        sub.markdown(
            f"Columns cycle across {ns} streams:\n{interleave_desc}  \n\n"
            "The eDP controller de-interleaves and routes each stream to the correct tile.",
            unsafe_allow_html=True
        )

        with sub.container():
            with st.spinner("Generating interleaved image..."):
                il_arr   = _make_interleaved_nx1(sf_arr, sf_w, sf_h, ns)
                il_img   = Image.fromarray(il_arr)
                il_bytes = _pil_to_png_bytes(il_img)

                # Per-stream slice downloads (left→right halves of interleaved image)
                stream_imgs   = []
                stream_bytes_ = []
                for i in range(ns):
                    sl  = il_arr[:, i*tile_w:(i+1)*tile_w, :]
                    simg = Image.fromarray(sl)
                    stream_imgs.append(simg)
                    stream_bytes_.append(_pil_to_png_bytes(simg))

        sub.image(il_img, use_container_width=True,
                  caption=f"Column-Interleaved Superframe ({ns}-way)  {sf_w}×{sf_h}")
        sub.download_button(
            label="â¬‡️ Download Interleaved Superframe (PNG)",
            data=il_bytes,
            file_name=f"mso_{mode_label.replace('×','x').replace(' ','_')}_interleaved_{sf_w}x{sf_h}.png",
            mime="image/png", type="primary",
            key=f"dl_il_{mode_label}"
        )

        # Per-stream slice downloads
        sub.markdown("---")
        sub.markdown("### Download Interleaved — Per-Stream Slices")
        sub.markdown(
            f"Left-to-right slices of the interleaved image, each **{tile_w}×{sf_h}**.",
            unsafe_allow_html=True
        )
        cols_dl = sub.columns(ns)
        for i, col in enumerate(cols_dl):
            icon = ["🏗º️","📷","❄️","🎬"][i % 4]
            col.markdown(f"#### {icon} Stream {i} — {panel_names[i]}")
            col.image(stream_imgs[i], use_container_width=True,
                      caption=f"Stream {i}: {panel_names[i]}  {tile_w}×{sf_h}")
            col.download_button(
                label=f"â¬‡️ Download Stream {i} (PNG)",
                data=stream_bytes_[i],
                file_name=f"mso_{mode_label.replace('×','x').replace(' ','_')}_stream{i}_{tile_w}x{sf_h}.png",
                mime="image/png", type="primary",
                use_container_width=True,
                key=f"dl_s{i}_{mode_label}"
            )
    else:
        sub.markdown("#### Non-Column-Interleaved Superframe")
        noninterleave_desc = "  \n".join(
            f"{i+1}. **{panel_names[i]} ({tile_w}×{sf_h})** → mapped to **Lane {i}**"
            for i in range(ns))
        sub.markdown(
            "Each tile is sent to the MSO link **without column-interleaving** between tiles:  \n"
            f"{noninterleave_desc}",
            unsafe_allow_html=True
        )

        with sub.container():
            with st.spinner("Generating non-interleaved image..."):
                il_arr   = sf_arr.copy()
                il_img   = Image.fromarray(il_arr)
                il_bytes = _pil_to_png_bytes(il_img)

                stream_imgs   = []
                stream_bytes_ = []
                for i in range(ns):
                    sl  = il_arr[:, i*tile_w:(i+1)*tile_w, :]
                    simg = Image.fromarray(sl)
                    stream_imgs.append(simg)
                    stream_bytes_.append(_pil_to_png_bytes(simg))

        sub.image(il_img, use_container_width=True,
                  caption=f"Non-Column-Interleaved Superframe  {sf_w}×{sf_h}")
        sub.download_button(
            label="â¬‡️ Download Non-Interleaved Superframe (PNG)",
            data=il_bytes,
            file_name=f"mso_{mode_label.replace('×','x').replace(' ','_')}_noninterleaved_{sf_w}x{sf_h}.png",
            mime="image/png", type="primary",
            key=f"dl_il_{mode_label}"
        )

        # Per-tile downloads
        sub.markdown("---")
        sub.markdown("### Download Tiles — Per-Lane")
        sub.markdown(
            f"Left-to-right tiles, each **{tile_w}×{sf_h}**, sent without column-interleaving.",
            unsafe_allow_html=True
        )
        cols_dl = sub.columns(ns)
        lane_icons = ["🏗º️","📷","❄️","🎬"]
        for i, col in enumerate(cols_dl):
            col.markdown(f"#### {lane_icons[i % 4]} {panel_names[i]} (Lane {i})")
            col.image(stream_imgs[i], use_container_width=True,
                      caption=f"{panel_names[i]} Tile  {tile_w}×{sf_h}  → Lane {i}")
            col.download_button(
                label=f"â¬‡️ Download {panel_names[i]} Tile (PNG)",
                data=stream_bytes_[i],
                file_name=f"mso_{mode_label.replace('×','x').replace(' ','_')}_lane{i}_{tile_w}x{sf_h}.png",
                mime="image/png", type="primary",
                use_container_width=True,
                key=f"dl_s{i}_{mode_label}"
            )

    # ── Pixel-level Zoom ─────────────────────────────────────────────────
    sub.markdown("---")
    sub.markdown("### Pixel-level Zoom")
    sub.caption("Select a region of the interleaved superframe (Step 2) to zoom into.")

    za, zb, zc, zd = sub.columns(4)
    z_col0  = int(za.number_input("Start column", min_value=0, max_value=sf_w-2,
                                  value=0,   step=1, key=f"zcol_{mode_label}"))
    z_row0  = int(zb.number_input("Start row",    min_value=0, max_value=sf_h-2,
                                  value=0,   step=1, key=f"zrow_{mode_label}"))
    z_cols  = int(zc.number_input("Columns to show", min_value=1, max_value=sf_w,
                                  value=200, step=1, key=f"zcols_{mode_label}"))
    z_rows  = int(zd.number_input("Rows to show",    min_value=1, max_value=sf_h,
                                  value=200, step=1, key=f"zrows_{mode_label}"))

    z_cols = min(z_cols, sf_w - z_col0)
    z_rows = min(z_rows, sf_h - z_row0)
    crop   = il_arr[z_row0:z_row0+z_rows, z_col0:z_col0+z_cols, :]

    DISPLAY_W = 1200
    scale     = max(1, DISPLAY_W // max(z_cols, 1))
    crop_img  = Image.fromarray(crop).resize(
        (z_cols*scale, z_rows*scale), resample=Image.NEAREST)

    sub.image(crop_img, use_container_width=False,
              caption=f"Cols {z_col0}–{z_col0+z_cols-1}, rows {z_row0}–{z_row0+z_rows-1}  "
                      f"({z_cols}×{z_rows} px, {scale}x scale)")
    sub.caption(
        f"Each group of {ns} adjacent columns contains one pixel from each stream "
        f"({', '.join(panel_names)}) cycling left-to-right."
    )


# ── Wire up MSO 2×1 and 4×1 sub-tabs ─────────────────────────────────────────
with edp_sub4:
    # ── Per-stream bandwidth feasibility (each stream = 1 lane) ───────────
    edp_sub4.markdown("### Per-Stream Bandwidth Feasibility (1 Lane per Stream)")
    px_per_stream_2x1   = total_pixels / 2
    pclk_per_stream_2x1 = px_per_stream_2x1 * fps * (1 + blank_ratio) / 1e6

    edp_sub4.markdown("##### Max Active Pixels per Frame (MP)")
    mp2_tbl = {"1 Lane": {f"{lr} Gbps": _edp_mp(1, lr) / 1e6 for lr in EDP_LINK_RATES}}
    df_mp2 = pd.DataFrame(mp2_tbl).T; df_mp2.index.name = "Lanes \\ Rate"
    edp_sub4.dataframe(df_mp2.style.map(lambda v: cm(v, px_per_stream_2x1)).format("{:.3f} MP"),
                        use_container_width=True)
    edp_sub4.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-stream target resolution "
        f"({px_per_stream_2x1/1e6:.3f} MP)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-stream target resolution"
    )

    edp_sub4.markdown("##### Maximum PCLK (MHz)")
    mpclk2_tbl = {"1 Lane": {f"{lr} Gbps": _edp_mp(1, lr) * fps * (1 + blank_ratio) / 1e6
                              for lr in EDP_LINK_RATES}}
    df_mpclk2 = pd.DataFrame(mpclk2_tbl).T; df_mpclk2.index.name = "Lanes \\ Rate"
    edp_sub4.dataframe(df_mpclk2.style.map(lambda v: cm(v, pclk_per_stream_2x1*1e6)).format("{:.2f} MHz"),
                        use_container_width=True)
    edp_sub4.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-stream target pixel clock "
        f"({pclk_per_stream_2x1:.2f} MHz)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-stream target pixel clock"
    )

    edp_sub4.markdown("---")
    _mso_superframe_ui(
        sub          = edp_sub4,
        ns           = 2,
        lps          = 1,
        mode_label   = "MSO 2×1",
        panel_names  = ["Navigation", "Multimedia"],
        sf_caption   = "Original Superframe  {sf_w}×{sf_h} — Navigation (left) + Multimedia (right)"
    )

with edp_sub5:
    # ── Per-stream bandwidth feasibility (each stream = 1 lane) ───────────
    edp_sub5.markdown("### Per-Stream Bandwidth Feasibility (1 Lane per Stream)")
    px_per_stream_4x1   = total_pixels / 4
    pclk_per_stream_4x1 = px_per_stream_4x1 * fps * (1 + blank_ratio) / 1e6

    edp_sub5.markdown("##### Max Active Pixels per Frame (MP)")
    mp4_tbl = {"1 Lane": {f"{lr} Gbps": _edp_mp(1, lr) / 1e6 for lr in EDP_LINK_RATES}}
    df_mp4 = pd.DataFrame(mp4_tbl).T; df_mp4.index.name = "Lanes \\ Rate"
    edp_sub5.dataframe(df_mp4.style.map(lambda v: cm(v, px_per_stream_4x1)).format("{:.3f} MP"),
                        use_container_width=True)
    edp_sub5.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-stream target resolution "
        f"({px_per_stream_4x1/1e6:.3f} MP)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-stream target resolution"
    )

    edp_sub5.markdown("##### Maximum PCLK (MHz)")
    mpclk4_tbl = {"1 Lane": {f"{lr} Gbps": _edp_mp(1, lr) * fps * (1 + blank_ratio) / 1e6
                              for lr in EDP_LINK_RATES}}
    df_mpclk4 = pd.DataFrame(mpclk4_tbl).T; df_mpclk4.index.name = "Lanes \\ Rate"
    edp_sub5.dataframe(df_mpclk4.style.map(lambda v: cm(v, pclk_per_stream_4x1*1e6)).format("{:.2f} MHz"),
                        use_container_width=True)
    edp_sub5.caption(
        "🟩 **Green = PASS** — meets/exceeds the per-stream target pixel clock "
        f"({pclk_per_stream_4x1:.2f} MHz)  ·  "
        "🟥 **Red = FAIL** — insufficient bandwidth for the per-stream target pixel clock"
    )

    edp_sub5.markdown("---")
    _mso_superframe_ui(
        sub          = edp_sub5,
        ns           = 4,
        lps          = 1,
        mode_label   = "MSO 4×1",
        panel_names  = ["Navigation", "Rear Camera", "Climate", "Multimedia"],
        sf_caption   = "Original Superframe  {sf_w}×{sf_h} — 4 panels (Nav | Camera | Climate | MM)"
    )

with edp_sub6:
    st.markdown('<h3 class="section-header">eDP Link Training</h3>',
                unsafe_allow_html=True)

    st.info(
        "**Link Training** is the eDP/DisplayPort handshake that runs before normal video "
        "transmission to verify the Source and Sink can reliably communicate at a chosen "
        "**Link Rate** and **Lane Count**. It consists of **Clock Recovery (CR)**, "
        "**Channel Equalization (EQ)**, and **Inter-lane Alignment**, all coordinated via the "
        "**AUX channel** and DPCD registers."
    )

    # ── Controls ─────────────────────────────────────────────────────────
    lt1, lt2, lt3, lt4, lt5 = st.columns(5)
    lt_rate  = lt1.selectbox("Link Rate (Gbps)", EDP_LINK_RATES,
                              index=EDP_LINK_RATES.index(5.4), key="lt_rate")
    lt_lanes = lt2.selectbox("Lane Count", LANES_OPTIONS, index=LANES_OPTIONS.index(4), key="lt_lanes")
    lt_ssc   = lt3.checkbox("SSC Enabled", value=True, key="lt_ssc")
    lt_ef    = lt4.checkbox("Enhanced Framing", value=True, key="lt_ef")
    lt_dsc   = lt5.checkbox("DSC Enabled", value=dsc_on, key="lt_dsc")

    # TPS used for EQ depends on link rate
    if lt_rate >= 8.1:
        eq_tps = "TPS4 (or TPS3)"
    elif lt_rate >= 5.4:
        eq_tps = "TPS3 (or TPS2)"
    else:
        eq_tps = "TPS2"

    # ── Flowchart ────────────────────────────────────────────────────────
    st.markdown("##### Link Training Flow")

    stages = [
        ("1. Capability\nDetection",      "Read Sink DPCD via AUX:\nMax Link Rate, Max Lanes,\nSSC, Enhanced Framing, DSC"),
        ("2. Link\nConfiguration",        f"Set LINK_BW_SET = {lt_rate} Gbps\nSet LANE_COUNT_SET = {lt_lanes}\nSSC={'On' if lt_ssc else 'Off'}, EF={'On' if lt_ef else 'Off'}"),
        ("3. Clock Recovery\n(TPS1)",     "Adjust per-lane Voltage Swing\n& Pre-emphasis until\nCR_DONE = 1 (all lanes)"),
        ("4. Channel Eq.\n(" + eq_tps + ")", "Adjust per-lane levels until\nCHANNEL_EQ_DONE = 1\nand SYMBOL_LOCK = 1"),
        ("5. Inter-lane\nAlignment",      "Confirm\nINTERLANE_ALIGN_DONE = 1\nfor all lanes"),
        ("6. Normal Operation\n+ DSC Enable" if lt_dsc else "6. Normal\nOperation",
         (f"TRAINING_PATTERN_SET = 0\nLink Up — then set\nDSC_ENABLE = 1 ({dsc_ratio_val:.2g}:1)"
          if lt_dsc else
          "TRAINING_PATTERN_SET = 0\nLink Up — video transmission begins")),
    ]

    n = len(stages)
    box_w, box_h, gap = 1.45, 1.05, 0.40
    fig_lt = go.Figure()
    for i, (title, detail) in enumerate(stages):
        x0 = i * (box_w + gap)
        x1 = x0 + box_w
        fig_lt.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=box_h,
                         line=dict(color="#2563eb", width=2),
                         fillcolor="#dbeafe")
        fig_lt.add_annotation(x=(x0+x1)/2, y=box_h*0.78, text=f"<b>{title}</b>",
                              showarrow=False, font=dict(size=18, color="#1e3a8a"),
                              align="center")
        fig_lt.add_annotation(x=(x0+x1)/2, y=box_h*0.32, text=detail.replace("\n", "<br>"),
                              showarrow=False, font=dict(size=14, color="#334155"),
                              align="center")
        if i < n-1:
            fig_lt.add_annotation(x=x1+gap, y=box_h/2, ax=x1, ay=box_h/2,
                                   xref="x", yref="y", axref="x", ayref="y",
                                   showarrow=True, arrowhead=3, arrowsize=1.2,
                                   arrowcolor="#2563eb", arrowwidth=2)

    # Fallback loop: EQ/Alignment failure → back to Link Configuration (reduce rate/lanes)
    x_eq   = 3 * (box_w + gap) + box_w/2
    x_cfg  = 1 * (box_w + gap) + box_w/2
    fig_lt.add_annotation(x=x_cfg, y=box_h+0.32, ax=x_eq, ay=box_h+0.32,
                          xref="x", yref="y", axref="x", ayref="y",
                          showarrow=True, arrowhead=3, arrowsize=1.1,
                          arrowcolor="#ef4444", arrowwidth=2)
    fig_lt.add_annotation(x=(x_cfg+x_eq)/2, y=box_h+0.42,
                          text="CR/EQ/Align FAIL → reduce Link Rate or Lane Count, retry",
                          showarrow=False, font=dict(size=18, color="#ef4444"))
    fig_lt.add_shape(type="line", x0=x_eq, x1=x_eq, y0=box_h, y1=box_h+0.32,
                     line=dict(color="#ef4444", width=2, dash="dot"))
    fig_lt.add_shape(type="line", x0=x_cfg, x1=x_cfg, y0=box_h, y1=box_h+0.32,
                     line=dict(color="#ef4444", width=2, dash="dot"))

    fig_lt.update_xaxes(visible=False, range=[-0.15, n*(box_w+gap)])
    fig_lt.update_yaxes(visible=False, range=[-0.1, box_h+0.65])
    fig_lt.update_layout(height=440, margin=dict(l=10, r=10, t=10, b=10), **PLT)
    st.plotly_chart(fig_lt, use_container_width=True)

    # ── DPCD capability table ────────────────────────────────────────────
    st.markdown("##### DPCD Capability Registers Read During Capability Detection")
    df_dpcd = pd.DataFrame([
        {"DPCD Address": "0x00001", "Field": "MAX_LINK_RATE",   "Example Value": "0x1E (8.1 Gbps / HBR3)"},
        {"DPCD Address": "0x00002", "Field": "MAX_LANE_COUNT",  "Example Value": "0x04 (4 lanes)"},
        {"DPCD Address": "0x00002", "Field": "ENHANCED_FRAME_CAP", "Example Value": "1 = supported"},
        {"DPCD Address": "0x00003", "Field": "MAX_DOWNSPREAD",  "Example Value": "1 = SSC ≤0.5% supported"},
        {"DPCD Address": "0x00060", "Field": "DSC_SUPPORT (DSC_CAPABLE)", "Example Value": "1 = DSC supported"},
        {"DPCD Address": "0x00100", "Field": "LINK_BW_SET",     "Example Value": f"{lt_rate} Gbps (Source writes)"},
        {"DPCD Address": "0x00101", "Field": "LANE_COUNT_SET / ENHANCED_FRAME_EN", "Example Value": f"{lt_lanes} lanes, EF={'1' if lt_ef else '0'}"},
        {"DPCD Address": "0x00102", "Field": "TRAINING_PATTERN_SET", "Example Value": "TPS1 → TPS2/3/4 → 0 (Normal)"},
        {"DPCD Address": "0x00160", "Field": "DSC_ENABLE", "Example Value": f"{'1 (' + format(dsc_ratio_val, '.2g') + ':1)' if lt_dsc else '0 (DSC off)'}"},
        {"DPCD Address": "0x00103-106", "Field": "TRAINING_LANEx_SET (VOD/Pre-emphasis)", "Example Value": "Per-lane swing & pre-emphasis"},
        {"DPCD Address": "0x00202", "Field": "LANEx_x_STATUS (CR_DONE / EQ_DONE / SYMBOL_LOCKED)", "Example Value": "Read by Source after each pattern"},
        {"DPCD Address": "0x00204", "Field": "LANE_ALIGN_STATUS_UPDATED (INTERLANE_ALIGN_DONE)", "Example Value": "1 = aligned"},
        {"DPCD Address": "0x00206-207", "Field": "ADJUST_REQUEST_LANEx (VOD/Pre-emphasis adjust)", "Example Value": "Sink-requested level changes"},
    ])
    st.dataframe(df_dpcd, use_container_width=True, hide_index=True)

    # ── VOD / Pre-emphasis level table ──────────────────────────────────
    st.markdown("##### Per-Lane Voltage Swing & Pre-Emphasis Levels (CR / EQ Adjustment)")
    df_vod = pd.DataFrame({
        "Level": ["Level 0", "Level 1", "Level 2", "Level 3"],
        "Voltage Swing (VOD)": ["400 mV", "600 mV", "800 mV", "1200 mV"],
        "Pre-Emphasis": ["0 dB", "3.5 dB", "6.0 dB", "9.5 dB"],
    })
    st.dataframe(df_vod, use_container_width=True, hide_index=True)
    st.caption(
        "During CR (TPS1), the Source sweeps **Voltage Swing** per lane based on "
        "`ADJUST_REQUEST_LANEx` until `CR_DONE=1`. During EQ "
        f"({eq_tps}), **Pre-Emphasis** is similarly adjusted until "
        "`CHANNEL_EQ_DONE=1` and `SYMBOL_LOCKED=1`. "
        "Not all VOD/Pre-Emphasis combinations are valid (e.g. VOD3 + any Pre-Emphasis > 0 is reserved)."
    )

    # ── Per-lane training status table (illustrative) ───────────────────
    st.markdown(f"##### Example Per-Lane Training Status — {lt_lanes} Lane{'s' if lt_lanes>1 else ''} @ {lt_rate} Gbps")
    df_status = pd.DataFrame({
        "Lane": [f"Lane {i}" for i in range(lt_lanes)],
        "VOD Level":      [1]*lt_lanes,
        "Pre-Emphasis Level": [1]*lt_lanes,
        "CR_DONE":        ["✓"]*lt_lanes,
        f"CHANNEL_EQ_DONE ({eq_tps})": ["✓"]*lt_lanes,
        "SYMBOL_LOCKED":  ["✓"]*lt_lanes,
        "INTERLANE_ALIGN_DONE": ["✓"]*lt_lanes,
    })
    st.dataframe(
        df_status.style.map(lambda v: "background-color:#dcfce7;color:#166534" if v == "✓" else "",
                             subset=[c for c in df_status.columns if c not in ("Lane","VOD Level","Pre-Emphasis Level")]),
        use_container_width=True, hide_index=True
    )
    st.caption(
        f"At **{lt_rate} Gbps / {lt_lanes} lane{'s' if lt_lanes>1 else ''}**"
        f"{' with SSC' if lt_ssc else ' without SSC'}"
        f"{' and Enhanced Framing' if lt_ef else ''}, all lanes report "
        "`CR_DONE`, `CHANNEL_EQ_DONE`, `SYMBOL_LOCKED`, and `INTERLANE_ALIGN_DONE` = 1 "
        "before `TRAINING_PATTERN_SET` is cleared to 0 (Normal Operation / Link Up)."
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TAB 7 – DP 2.1 VRR (Adaptive-Sync) Demo
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
with tab_vrr:
    st.markdown('<h3 class="section-header">DP 2.1 Adaptive-Sync (VRR) Demo</h3>',
                unsafe_allow_html=True)

    st.markdown(
        "This demo illustrates how **Variable Refresh Rate (Adaptive-Sync)** in DP 2.1 "
        "differs from a **fixed refresh rate**, when the source content (e.g. a streamed/camera "
        "video feed) is not perfectly periodic."
    )

    vrr_mode = st.radio("Display mode", ["Fixed Refresh Rate", "DP 2.1 Adaptive-Sync (VRR)"],
                         horizontal=True, index=1, key="vrr_mode")

    vrr_sub_mode = "FAVT"
    if vrr_mode != "Fixed Refresh Rate":
        vrr_sub_mode = st.radio(
            "Adaptive-Sync sub-mode",
            ["FAVT (Fixed Average Vertical Total)", "AVT (Adaptive Vertical Total)"],
            horizontal=True, key="vrr_sub_mode",
        )
        vrr_sub_mode = "FAVT" if vrr_sub_mode.startswith("FAVT") else "AVT"

        if vrr_sub_mode == "AVT":
            st.markdown(
                "**AVT — Adaptive Vertical Total**: Vtotal can vary **freely, frame-by-frame**, "
                "within the panel's supported min/max range. Each refresh aligns directly to when "
                "that frame's content is ready — the *true* VRR behavior. Best for variable/"
                "unpredictable cadences (gaming, irregular streamed video)."
            )
        else:
            st.markdown(
                "**FAVT — Fixed Average Vertical Total**: individual frames can deviate above/below "
                "the nominal Vtotal, but the **running average Vtotal is kept fixed**. A long frame "
                "must be compensated by a shorter one nearby. Useful when the *average* refresh rate "
                "must match a reference (e.g., audio sync), at the cost of slightly less precise "
                "per-frame tracking."
            )

    st.markdown("#### Content source timing")

    VRR_JITTER_PRESETS = {
        "Native render (~0.5ms)": 0.5,
        "Local camera (~1ms)": 1,
        "Wired stream (~3ms)": 3,
        "Wireless stream (~6ms)": 6,
    }

    if "vrr_jitter_ms" not in st.session_state:
        st.session_state["vrr_jitter_ms"] = 3

    vrr_preset_cols = st.columns(len(VRR_JITTER_PRESETS))
    for vrr_col, (vrr_label, vrr_value) in zip(vrr_preset_cols, VRR_JITTER_PRESETS.items()):
        if vrr_col.button(vrr_label):
            st.session_state["vrr_jitter_ms"] = vrr_value

    if vrr_mode == "Fixed Refresh Rate":
        vc1, vc2, vc3 = st.columns(3)
        with vc1:
            vrr_fixed_hz = vc1.slider("Fixed refresh rate (Hz)", 30, 120, 60, step=1)
        with vc2:
            vrr_base_fps = vc2.slider("Avg content frame rate (fps)", 24, 90, 60, step=1)
        with vc3:
            vrr_jitter_ms = vc3.slider("Frame timing jitter (+/- ms)", 0.0, 15.0, step=0.5, key="vrr_jitter_ms")
    else:
        vc1, vc2 = st.columns(2)
        with vc1:
            vrr_base_fps = vc1.slider("Avg content frame rate (fps)", 24, 90, 60, step=1)
        with vc2:
            vrr_jitter_ms = vc2.slider("Frame timing jitter (+/- ms)", 0.0, 15.0, step=0.5, key="vrr_jitter_ms")

    # Generate "content ready" timestamps with jitter over a 200ms window
    vrr_duration_ms = 200
    vrr_base_period = 1000.0 / vrr_base_fps
    vrr_rng = np.random.default_rng(42)
    vrr_content_ready = []
    vrr_t = 0.0
    while vrr_t < vrr_duration_ms:
        vrr_content_ready.append(vrr_t)
        vrr_jitter = vrr_rng.uniform(-vrr_jitter_ms, vrr_jitter_ms)
        vrr_t += max(2.0, vrr_base_period + vrr_jitter)
    vrr_content_ready = np.array(vrr_content_ready)
    vrr_content_ready = vrr_content_ready[vrr_content_ready <= vrr_duration_ms]

    # Pixel timing parameters (needed for FAVT Vtotal redistribution and the Vblank chart)
    vbcol1, vbcol2, vbcol3 = st.columns(3)
    with vbcol1:
        vrr_pclk_mhz = vbcol1.number_input("Pixel clock (MHz)", value=148.5, step=0.5)
    with vbcol2:
        vrr_htotal = vbcol2.number_input("Htotal (pixels)", value=2200, step=10)
    with vbcol3:
        vrr_vactive = vbcol3.number_input("Vactive (lines)", value=1080, step=10)

    vrr_line_time_us = vrr_htotal / vrr_pclk_mhz

    # Base timing Vtotal (fixed panel timing at its nominal refresh rate)
    # Used as the minimum Vtotal floor in FAVT — source can only ADD lines, never go below.
    vrr_base_vtotal = (1000.0 / vrr_fixed_hz * 1000.0) / vrr_line_time_us if vrr_mode == "Fixed Refresh Rate" \
        else ((1000.0 / vrr_base_fps * 1000.0) / vrr_line_time_us)

    if vrr_mode == "Fixed Refresh Rate":
        vrr_fixed_period = 1000.0 / vrr_fixed_hz
        vrr_refresh_times = np.arange(0, vrr_duration_ms, vrr_fixed_period)
    elif vrr_sub_mode == "AVT":
        # AVT: refresh exactly when content is ready, Vtotal varies freely per frame
        vrr_refresh_times = vrr_content_ready
    else:
        # FAVT (per VESA spec):
        # 1. Source ADDS lines to the base Vtotal only — Vtotal >= base_vtotal always.
        # 2. Added lines are dithered over frames so the average frame rate exactly
        #    matches the actual content cadence (not just the nominal fps).
        # 3. Only valid when content fps <= base timing fps.
        vrr_natural_intervals = np.diff(vrr_content_ready)
        vrr_avg_content_interval_ms = np.mean(vrr_natural_intervals)

        # Target Vtotal = average content period, clamped to >= base_vtotal (spec requirement 1 & 3)
        vrr_target_vtotal = max(
            (vrr_avg_content_interval_ms * 1000.0) / vrr_line_time_us,
            vrr_base_vtotal,
        )

        # Dither: for each frame, compute how many extra lines needed vs target,
        # carry fractional remainder forward so cumulative average tracks exactly.
        vrr_favt_vtotal = []
        vrr_carry = 0.0
        for interval in vrr_natural_intervals:
            # Raw lines needed to cover this content interval
            raw_lines = (interval * 1000.0) / vrr_line_time_us
            # Ideal lines this frame = target + carry correction
            ideal = vrr_target_vtotal + vrr_carry
            # Round to integer lines (dithering)
            adj = round(ideal)
            # Spec: Vtotal >= base_vtotal (only additive)
            adj = max(adj, int(vrr_base_vtotal))
            vrr_favt_vtotal.append(adj)
            # Carry the difference forward for next frame
            vrr_carry = ideal - adj

        vrr_favt_vtotal = np.array(vrr_favt_vtotal, dtype=float)

        vrr_refresh_times = np.concatenate((
            [vrr_content_ready[0]],
            vrr_content_ready[0] + np.cumsum(vrr_favt_vtotal * vrr_line_time_us / 1000.0),
        ))

    # --- FAVT constraint warning (content fps must be <= base timing fps) ---
    if vrr_mode != "Fixed Refresh Rate" and vrr_sub_mode == "FAVT":
        vrr_nominal_fps = vrr_base_fps
        if vrr_nominal_fps > vrr_fixed_hz if vrr_mode == "Fixed Refresh Rate" else False:
            st.warning(
                f"⚠️ FAVT requires content frame rate ≤ base timing frame rate. "
                f"Content: {vrr_base_fps} fps, Base timing: {vrr_base_fps} fps."
            )
        # Derive effective base fps from panel base_vtotal
        vrr_effective_base_fps = 1000.0 / (vrr_base_vtotal * vrr_line_time_us / 1000.0)
        if vrr_base_fps > vrr_effective_base_fps + 0.5:
            st.warning(
                f"⚠️ FAVT spec requires content fps ≤ base timing fps. "
                f"Current content: **{vrr_base_fps} fps**, base timing: **{vrr_effective_base_fps:.1f} fps**. "
                f"Lower content fps or increase base timing rate."
            )

    # --- Signal Timing Block Diagram (FAVT or Fixed only; AVT has its own block below) ---
    if vrr_mode == "Fixed Refresh Rate" or vrr_sub_mode == "FAVT":
        if vrr_mode == "Fixed Refresh Rate":
            st.markdown("#### Fixed Refresh Rate — Signal Timing Block Diagram")
        else:
            st.markdown("#### FAVT Signal Timing Block Diagram")
        st.caption(
            "Shows how Vsync, Vblank, Vactive, Content-ready and the Adaptive-Sync SDP packet "
            "relate across frames. In FAVT the SDP carries the *next* frame's Vtotal value so "
            "the sink panel can prepare its timing before Vsync arrives."
        )
    
        _favt_scenario = st.selectbox(
            "Scenario",
            [
                "D: Fixed 60Hz display with 30fps content — frame repeat problem (no FAVT)",
                "A: FAVT — 30fps content on 60Hz base panel (wireless stream)",
                "B: FAVT — ~58fps content with jitter on 60Hz base panel (wired stream)",
                "C: FAVT — 60fps content matches 60Hz base panel exactly (native render)",
            ],
            index=0,
            key="favt_scenario",
        )
        st.caption(
            "**D:** Fixed 60Hz Vsync with 30fps content — every frame is repeated twice, causing judder. "
            "Compare with **A** where FAVT adapts Vsync to 30fps eliminating repeats.  "
            "**B:** Content targets 60fps but per-frame jitter makes actual avg ~58fps — "
            "FAVT dithers Vtotal to track exactly.  "
            "**C:** Content perfectly matches base timing — no dithering needed."
        )
    
        _FAVT_SCENARIOS = {
            "D: Fixed 60Hz display with 30fps content — frame repeat problem (no FAVT)": dict(
                base_vtotal=1125, vactive=1080,
                fixed=True,   # special flag: Vsync at base rate, content at half rate
                frames=[      # 8 display frames shown, content ready every 2nd frame
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                ],
                note="Fixed 60Hz: Vsync fires every 1125L regardless of content — each 30fps frame repeated twice (judder)"
            ),
            "A: FAVT — 30fps content on 60Hz base panel (wireless stream)": dict(
                base_vtotal=1125, vactive=1080,
                frames=[
                    dict(vtotal=2250, co=0.92), dict(vtotal=2250, co=0.92),
                    dict(vtotal=2250, co=0.92), dict(vtotal=2250, co=0.92),
                ],
                note="FAVT: Vblank doubled → display avg = 30fps, matching content cadence. No frame repeats ✓"
            ),
            "B: FAVT — ~58fps content with jitter on 60Hz base panel (wired stream)": dict(
                base_vtotal=1125, vactive=1080,
                frames=[
                    dict(vtotal=1160, co=0.86), dict(vtotal=1195, co=0.90),
                    dict(vtotal=1125, co=0.83), dict(vtotal=1210, co=0.91),
                ],
                note="FAVT: Vtotal dithered per frame (1160→1195→1125→1210L) — avg = 1172L → ~58fps, exactly matches content ✓"
            ),
            "C: FAVT — 60fps content matches 60Hz base panel exactly (native render)": dict(
                base_vtotal=1125, vactive=1080,
                frames=[
                    dict(vtotal=1125, co=0.82), dict(vtotal=1125, co=0.82),
                    dict(vtotal=1125, co=0.82), dict(vtotal=1125, co=0.82),
                ],
                note="FAVT: Content cadence = base timing — Vtotal constant at 1125L, no dithering needed ✓"
            ),
        }
    
        _sc = _FAVT_SCENARIOS[_favt_scenario]
        _frames      = _sc["frames"]
        _base_vtotal = _sc["base_vtotal"]
        _vactive     = _sc["vactive"]
        _base_vblank = _base_vtotal - _vactive
        _total_vtotal = sum(f["vtotal"] for f in _frames)
    
        # Build x positions (proportional to Vtotal)
        _xs = [0.0]
        for f in _frames:
            _xs.append(_xs[-1] + f["vtotal"] / _total_vtotal)
    
        C_BLUE   = "#1f77b4"
        C_LBLUE  = "#aec7e8"
        C_RED    = "#d62728"
        C_PURPLE = "#9467bd"
        C_ORANGE = "#e07b00"
    
        # Lane y positions
        LANE_Y = dict(vsync=5.0, vblank=4.0, vactive=3.0, content=2.0, sdp=1.0)
        BAR_H  = 0.55
    
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
    
        _fig_td, (_ax_leg, _ax_td) = plt.subplots(
            2, 1, figsize=(12, 6.5),
            gridspec_kw={"height_ratios": [1, 8]},
        )
        _fig_td.patch.set_facecolor("white")
        _ax_td.set_facecolor("white")
        _ax_leg.set_facecolor("white")
        _ax_leg.axis("off")
    
        # Legend in its own axis row so it never overlaps the diagram
        _handles = [
            Patch(color=C_BLUE,   alpha=0.85, label="Vsync / Vblank"),
            Patch(color=C_LBLUE,  alpha=0.75, label="Vactive (image lines)"),
            Patch(color=C_RED,               label="Content frame ready"),
            Patch(color=C_PURPLE,            label="Adaptive-Sync SDP"),
            Line2D([0],[0], color=C_ORANGE, linestyle="--", lw=1.5,
                   label=f"Base Vblank = {_base_vblank}L (floor)"),
        ]
        _ax_leg.legend(handles=_handles, loc="center", fontsize=9,
                       framealpha=0.9, ncol=5, borderpad=0.6)
    
        # Lane y positions — spread out more
        LANE_Y  = dict(vsync=8.5, vblank=6.8, vactive=5.0, content=3.3, sdp=1.6)
        BAR_H   = 0.8
        LBL_X   = -0.01   # x in data coords for lane labels (left of x=0)
    
        # Lane labels (use data coords, place left of x=0)
        for lane, y in LANE_Y.items():
            lbl = {"vsync":"Vsync","vblank":"Vblank\n(lines)","vactive":"Vactive\n(lines)",
                   "content":"Content\nready","sdp":"AS-SDP\n(Vtotal)"}[lane]
            _ax_td.text(LBL_X, y, lbl, ha="right", va="center", fontsize=9, color="#333")
    
        # Base Vblank dashed floor — fixed height within Vblank lane
        _base_frac = _base_vblank / _base_vtotal
        _floor_y   = LANE_Y["vblank"] - BAR_H/2 + _base_frac * BAR_H
        _ax_td.axhline(_floor_y, xmin=0, xmax=1, color=C_ORANGE,
                       linewidth=1.4, linestyle="--", zorder=3)
        _ax_td.text(1.001, _floor_y, f"Base Vblank = {_base_vblank}L",
                    ha="left", va="center", fontsize=8, color=C_ORANGE,
                    transform=_ax_td.get_yaxis_transform())
    
        for fi, f in enumerate(_frames):
            x0 = _xs[fi]
            x1 = _xs[fi + 1]
            fw = x1 - x0
            vt = f["vtotal"]
            bl = vt - _vactive
            blank_frac = bl / vt
    
            # Frame label
            _ax_td.text((x0+x1)/2, LANE_Y["vsync"] + BAR_H, f"F{fi+1}",
                        ha="center", va="bottom", fontsize=11, fontweight="bold", color="#222")
    
            # Frame divider
            _ax_td.axvline(x0, color="#cccccc", linewidth=1, zorder=1)
    
            # Vsync — narrow pulse then low line
            _ax_td.add_patch(plt.Rectangle(
                (x0, LANE_Y["vsync"] - BAR_H/2), fw*0.025, BAR_H,
                color=C_BLUE, zorder=3))
            _ax_td.plot([x0+fw*0.025, x1],
                        [LANE_Y["vsync"] - BAR_H/2 + 0.06]*2,
                        color=C_BLUE, linewidth=1.8, zorder=2)
    
            # Vblank bar — proportional height but with a visible minimum
            _MIN_VBL_H = 0.30
            _vbl_h = max(BAR_H * blank_frac, _MIN_VBL_H)
            _ax_td.add_patch(plt.Rectangle(
                (x0, LANE_Y["vblank"] - BAR_H/2), fw, _vbl_h,
                color=C_BLUE, alpha=0.85, zorder=2))
            # Label inside bar if tall enough, otherwise above it
            _vbl_label_y = LANE_Y["vblank"] - BAR_H/2 + _vbl_h/2
            _label_inside = _vbl_h >= 0.28
            _ax_td.text((x0+x1)/2, _vbl_label_y if _label_inside else LANE_Y["vblank"] - BAR_H/2 + _vbl_h + 0.12,
                        f"{bl}L", ha="center", va="center" if _label_inside else "bottom",
                        fontsize=9, color="white" if _label_inside else C_BLUE,
                        fontweight="bold")
    
            # Vactive bar — fixed height
            _ax_td.add_patch(plt.Rectangle(
                (x0, LANE_Y["vactive"] - BAR_H/2), fw, BAR_H,
                color=C_LBLUE, alpha=0.75, zorder=2))
            _ax_td.text((x0+x1)/2, LANE_Y["vactive"],
                        f"{_vactive}L", ha="center", va="center",
                        fontsize=9, color=C_BLUE, fontweight="bold")
    
            # Content ready pulse (None = no new frame, show "REPEAT" label instead)
            if f["co"] is not None:
                cx = x0 + f["co"] * fw
                _ax_td.add_patch(plt.Rectangle(
                    (cx - fw*0.010, LANE_Y["content"] - BAR_H/2), fw*0.020, BAR_H,
                    color=C_RED, zorder=3))
            else:
                _ax_td.text((x0+x1)/2, LANE_Y["content"], "REPEAT",
                            ha="center", va="center", fontsize=8,
                            color="#cc0000", fontweight="bold",
                            bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffe0e0",
                                      edgecolor="#cc0000", linewidth=0.8))
    
            # AS-SDP packet (only for FAVT scenarios, not fixed rate)
            _is_fixed = _sc.get("fixed", False)
            sdp_x = x0 + 0.05*fw
            sdp_w = min(0.20*fw, 0.055)
            if not _is_fixed:
                _ax_td.add_patch(plt.Rectangle(
                    (sdp_x, LANE_Y["sdp"] - BAR_H/2), sdp_w, BAR_H,
                    color=C_PURPLE, zorder=3))
                _ax_td.text(sdp_x + sdp_w/2, LANE_Y["sdp"],
                            f"V={vt}", ha="center", va="center",
                            fontsize=8, color="white", fontweight="bold")
                # Dotted arrow SDP → next Vsync
                _ax_td.annotate("", xy=(x1, LANE_Y["vsync"] - BAR_H/2 + 0.1),
                                 xytext=(sdp_x + sdp_w/2, LANE_Y["sdp"] + BAR_H/2),
                                 arrowprops=dict(arrowstyle="-|>", color=C_PURPLE,
                                                 lw=1.0, linestyle="dashed"))
            else:
                _ax_td.text((x0+x1)/2, LANE_Y["sdp"], "N/A",
                            ha="center", va="center", fontsize=8, color="#aaa")
    
            # Vtotal double-headed arrow + label below SDP
            arr_y = LANE_Y["sdp"] - BAR_H/2 - 0.35
            _ax_td.annotate("", xy=(x1 - 0.001, arr_y), xytext=(x0 + 0.001, arr_y),
                             arrowprops=dict(arrowstyle="<->", color="#444", lw=1.1))
            _ax_td.text((x0+x1)/2, arr_y - 0.25,
                        f"Vtotal = {vt}", ha="center", va="top",
                        fontsize=8.5, color="#222")
    
        # Final divider
        _ax_td.axvline(_xs[-1], color="#cccccc", linewidth=1, zorder=1)
    
        _ax_td.set_xlim(-0.13, 1.01)
        _ax_td.set_ylim(arr_y - 0.55, LANE_Y["vsync"] + BAR_H + 0.6)
        _ax_td.axis("off")
    
        # Note below diagram
        _fig_td.text(0.5, 0.01, f"Note: {_sc['note']}",
                     ha="center", va="bottom", fontsize=8.5,
                     color="#555", style="italic")
    
        _fig_td.tight_layout(rect=[0, 0.04, 1, 1])
        st.pyplot(_fig_td)

    # --- AVT Signal Timing Block Diagram ---
    if vrr_mode != "Fixed Refresh Rate" and vrr_sub_mode == "AVT":
        st.markdown("#### AVT Signal Timing Block Diagram")
        _avt_scenario = st.selectbox(
            "AVT Scenario",
            [
                "X: Fixed 60Hz with 30fps content — frame repeat (no AVT)",
                "A: AVT — slow content (30fps), Vtotal freely doubled",
                "B: AVT — variable content (fast then slow), Vtotal tracks freely",
                "C: AVT — fast content above base, Vtotal drops below base floor",
            ],
            index=1, key="avt_scenario",
        )
        st.caption(
            "**Key AVT vs FAVT difference:** AVT Vtotal can go **freely above AND below** "
            "the base Vtotal — no floor constraint. "
            "**C** shows frames arriving faster than the base 60Hz timing (Vtotal < 1125L), "
            "which FAVT cannot handle but AVT can."
        )

        _AVT_SCENARIOS = {
            "X: Fixed 60Hz with 30fps content — frame repeat (no AVT)": dict(
                base_vtotal=1125, vactive=1080, fixed=True,
                frames=[
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                    dict(vtotal=1125, co=None), dict(vtotal=1125, co=0.90),
                ],
                note="Fixed 60Hz: every 30fps frame repeated twice — judder. Compare with AVT scenario A."
            ),
            "A: AVT — slow content (30fps), Vtotal freely doubled": dict(
                base_vtotal=1125, vactive=1080,
                frames=[
                    dict(vtotal=2250, co=0.88), dict(vtotal=2250, co=0.88),
                    dict(vtotal=2250, co=0.88), dict(vtotal=2250, co=0.88),
                ],
                note="AVT: Vtotal doubled freely (no averaging needed) — display fires exactly when content ready ✓"
            ),
            "B: AVT — variable content (fast then slow), Vtotal tracks freely": dict(
                base_vtotal=1125, vactive=1080,
                frames=[
                    dict(vtotal=980,  co=0.82),
                    dict(vtotal=1350, co=0.90),
                    dict(vtotal=1050, co=0.84),
                    dict(vtotal=1280, co=0.89),
                ],
                note="AVT: Vtotal tracks each frame's exact arrival — some frames faster than base (980L < 1125L), some slower ✓"
            ),
            "C: AVT — fast content above base, Vtotal drops below base floor": dict(
                base_vtotal=1125, vactive=1080,
                frames=[
                    dict(vtotal=950,  co=0.80),
                    dict(vtotal=980,  co=0.81),
                    dict(vtotal=960,  co=0.80),
                    dict(vtotal=970,  co=0.81),
                ],
                note="AVT: Vtotal < base Vtotal (950–980L < 1125L) — display refresh > 60Hz. FAVT cannot do this (floor violated)."
            ),
        }

        _asc   = _AVT_SCENARIOS[_avt_scenario]
        _afr   = _asc["frames"]
        _abv   = _asc["base_vtotal"]
        _avact = _asc["vactive"]
        _abvbl = _abv - _avact
        _atot  = sum(f["vtotal"] for f in _afr)
        _axs   = [0.0]
        for _f in _afr:
            _axs.append(_axs[-1] + _f["vtotal"] / _atot)

        _fig_avt, (_axl2, _ax_avt) = plt.subplots(
            2, 1, figsize=(12, 6.5),
            gridspec_kw={"height_ratios": [1, 8]},
        )
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        C_BLUE   = "#1f77b4"
        C_LBLUE  = "#aec7e8"
        C_RED    = "#d62728"
        C_PURPLE = "#9467bd"
        C_ORANGE = "#ff7f0e"
        _fig_avt.patch.set_facecolor("white")
        _ax_avt.set_facecolor("white")
        _axl2.set_facecolor("white")
        _axl2.axis("off")

        _hAVT = [
            Patch(color=C_BLUE,  alpha=0.85, label="Vsync / Vblank"),
            Patch(color=C_LBLUE, alpha=0.75, label="Vactive (image lines)"),
            Patch(color=C_RED,              label="Content frame ready"),
            Patch(color=C_PURPLE,           label="Adaptive-Sync SDP"),
            Line2D([0],[0], color=C_ORANGE, linestyle="--", lw=1.5,
                   label=f"Base Vblank = {_abvbl}L (reference)"),
        ]
        _axl2.legend(handles=_hAVT, loc="center", fontsize=9,
                     framealpha=0.9, ncol=5, borderpad=0.6)

        _ALAY = dict(vsync=8.5, vblank=6.8, vactive=5.0, content=3.3, sdp=1.6)
        _ABH  = 0.8
        _AMIN = 0.30

        for _lane, _y in _ALAY.items():
            _lbl = {"vsync":"Vsync","vblank":"Vblank\n(lines)","vactive":"Vactive\n(lines)",
                    "content":"Content\nready","sdp":"AS-SDP\n(Vtotal)"}[_lane]
            _ax_avt.text(-0.01, _y, _lbl, ha="right", va="center", fontsize=9, color="#333")

        # Base Vblank reference line (dashed, no "floor" enforcement for AVT)
        _abf   = _abvbl / _abv
        _afloory = _ALAY["vblank"] - _ABH/2 + _abf * _ABH
        _ax_avt.axhline(_afloory, xmin=0, xmax=1, color=C_ORANGE,
                        linewidth=1.4, linestyle="--", zorder=3)
        _ax_avt.text(1.001, _afloory, f"Base Vblank = {_abvbl}L\n(reference only)",
                     ha="left", va="center", fontsize=7.5, color=C_ORANGE,
                     transform=_ax_avt.get_yaxis_transform())

        for _fi, _f in enumerate(_afr):
            _ax0 = _axs[_fi]; _ax1 = _axs[_fi+1]; _afw = _ax1 - _ax0
            _avt = _f["vtotal"]; _abl = _avt - _avact
            _ablf = _abl / _avt
            _below_base = _avt < _abv

            # Frame label — red if Vtotal < base (highlight AVT capability)
            _ax_avt.text((_ax0+_ax1)/2, _ALAY["vsync"] + _ABH,
                         f"F{_fi+1}", ha="center", va="bottom",
                         fontsize=11, fontweight="bold",
                         color="#c00000" if _below_base else "#222")

            _ax_avt.axvline(_ax0, color="#cccccc", linewidth=1, zorder=1)

            # Vsync pulse
            _ax_avt.add_patch(plt.Rectangle(
                (_ax0, _ALAY["vsync"]-_ABH/2), _afw*0.025, _ABH,
                color=C_BLUE, zorder=3))
            _ax_avt.plot([_ax0+_afw*0.025, _ax1],
                         [_ALAY["vsync"]-_ABH/2+0.06]*2,
                         color=C_BLUE, linewidth=1.8, zorder=2)

            # Vblank bar
            _avbl_h = max(_ABH * _ablf, _AMIN)
            _bar_color = "#c00000" if _below_base else C_BLUE
            _ax_avt.add_patch(plt.Rectangle(
                (_ax0, _ALAY["vblank"]-_ABH/2), _afw, _avbl_h,
                color=_bar_color, alpha=0.85, zorder=2))
            _inside = _avbl_h >= 0.28
            _ax_avt.text((_ax0+_ax1)/2,
                         (_ALAY["vblank"]-_ABH/2+_avbl_h/2) if _inside
                         else (_ALAY["vblank"]-_ABH/2+_avbl_h+0.12),
                         f"{_abl}L", ha="center",
                         va="center" if _inside else "bottom",
                         fontsize=9, fontweight="bold",
                         color="white" if _inside else _bar_color)

            # Vactive bar
            _ax_avt.add_patch(plt.Rectangle(
                (_ax0, _ALAY["vactive"]-_ABH/2), _afw, _ABH,
                color=C_LBLUE, alpha=0.75, zorder=2))
            _ax_avt.text((_ax0+_ax1)/2, _ALAY["vactive"],
                         f"{_avact}L", ha="center", va="center",
                         fontsize=9, color=C_BLUE, fontweight="bold")

            # Content ready pulse
            if _f["co"] is not None:
                _acx = _ax0 + _f["co"] * _afw
                _ax_avt.add_patch(plt.Rectangle(
                    (_acx-_afw*0.010, _ALAY["content"]-_ABH/2), _afw*0.020, _ABH,
                    color=C_RED, zorder=3))
            else:
                _ax_avt.text((_ax0+_ax1)/2, _ALAY["content"], "REPEAT",
                             ha="center", va="center", fontsize=8,
                             color="#cc0000", fontweight="bold",
                             bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffe0e0",
                                       edgecolor="#cc0000", linewidth=0.8))

            # AS-SDP
            _is_afixed = _asc.get("fixed", False)
            _asdp_x = _ax0 + 0.05*_afw
            _asdp_w = min(0.20*_afw, 0.055)
            if not _is_afixed:
                _ax_avt.add_patch(plt.Rectangle(
                    (_asdp_x, _ALAY["sdp"]-_ABH/2), _asdp_w, _ABH,
                    color=C_PURPLE, zorder=3))
                _ax_avt.text(_asdp_x+_asdp_w/2, _ALAY["sdp"],
                             f"V={_avt}", ha="center", va="center",
                             fontsize=8, color="white", fontweight="bold")
                _ax_avt.annotate("",
                                 xy=(_ax1, _ALAY["vsync"]-_ABH/2+0.1),
                                 xytext=(_asdp_x+_asdp_w/2, _ALAY["sdp"]+_ABH/2),
                                 arrowprops=dict(arrowstyle="-|>", color=C_PURPLE,
                                                 lw=1.0, linestyle="dashed"))
            else:
                _ax_avt.text((_ax0+_ax1)/2, _ALAY["sdp"], "N/A",
                             ha="center", va="center", fontsize=8, color="#aaa")

            # Vtotal span arrow
            _aarr_y = _ALAY["sdp"] - _ABH/2 - 0.35
            _ax_avt.annotate("", xy=(_ax1-0.001, _aarr_y), xytext=(_ax0+0.001, _aarr_y),
                             arrowprops=dict(arrowstyle="<->", color="#444", lw=1.1))
            _lbl_col = "#c00000" if _below_base else "#222"
            _ax_avt.text((_ax0+_ax1)/2, _aarr_y-0.25,
                         f"Vtotal = {_avt}", ha="center", va="top",
                         fontsize=8.5, color=_lbl_col, fontweight="bold" if _below_base else "normal")

        _ax_avt.axvline(_axs[-1], color="#cccccc", linewidth=1, zorder=1)
        _ax_avt.set_xlim(-0.13, 1.01)
        _ax_avt.set_ylim(_aarr_y-0.55, _ALAY["vsync"]+_ABH+0.6)
        _ax_avt.axis("off")
        _fig_avt.text(0.5, 0.01, f"Note: {_asc['note']}",
                      ha="center", va="bottom", fontsize=8.5, color="#555", style="italic")
        _fig_avt.tight_layout(rect=[0, 0.04, 1, 1])
        st.pyplot(_fig_avt)

    # --- Timeline plot ---
    VRR_RED = "#d62728"
    VRR_BLUE = "#1f77b4"
    VRR_GRAY = "#888888"

    vrr_fig, vrr_ax = plt.subplots(figsize=(11, 4))
    vrr_fig.patch.set_facecolor("white")
    vrr_ax.set_facecolor("white")

    VRR_PURPLE = "#9333ea"

    VRR_LANE_SDP     = 2.0
    VRR_LANE_CONTENT = 1.0
    VRR_LANE_REFRESH = 0.0

    def _vrr_draw_lane(times, y, color, label):
        vrr_ax.axhline(y, color="#dddddd", linewidth=1, zorder=1)
        vrr_ax.vlines(times, y, y + 0.18, color=color, linewidth=2, zorder=2)
        vrr_ax.plot(times, [y + 0.18] * len(times), "o", color=color, markersize=6,
                     markeredgecolor="white", markeredgewidth=1, zorder=3, label=label)
        for i in range(len(times) - 1):
            x0, x1 = times[i], times[i + 1]
            vrr_ax.annotate(
                "",
                xy=(x1, y - 0.06),
                xytext=(x0, y - 0.06),
                arrowprops=dict(arrowstyle="<->", color=color, lw=1, alpha=0.6),
                zorder=2,
            )
            vrr_ax.text(
                (x0 + x1) / 2, y - 0.13, f"{x1 - x0:.1f}",
                ha="center", va="top", fontsize=8, color=color,
            )

    _vrr_draw_lane(vrr_content_ready, VRR_LANE_CONTENT, VRR_RED, "Content frame ready")
    _vrr_draw_lane(vrr_refresh_times, VRR_LANE_REFRESH, VRR_BLUE, "Display refresh")

    if vrr_mode != "Fixed Refresh Rate":
        # Adaptive-Sync SDP: sent once per frame during Vblank, carrying the
        # target Vtotal/MISC info for the *upcoming* frame — i.e. shortly
        # before that frame's refresh point.
        vrr_sdp_lead_ms = min(0.5, vrr_line_time_us / 1000.0 * 2)
        vrr_sdp_times = np.clip(vrr_refresh_times - vrr_sdp_lead_ms, 0, vrr_duration_ms)
        vrr_ax.axhline(VRR_LANE_SDP, color="#dddddd", linewidth=1, zorder=1)
        vrr_ax.plot(vrr_sdp_times, [VRR_LANE_SDP] * len(vrr_sdp_times), "s",
                     color=VRR_PURPLE, markersize=6, markeredgecolor="white",
                     markeredgewidth=1, zorder=3, label="Adaptive-Sync SDP (Vtotal update)")
        for sx in vrr_sdp_times:
            vrr_ax.plot([sx, sx], [VRR_LANE_SDP, VRR_LANE_REFRESH + 0.18],
                         color=VRR_PURPLE, linewidth=0.7, linestyle=":", alpha=0.6, zorder=1)

    vrr_ax.set_xlim(0, vrr_duration_ms)
    if vrr_mode != "Fixed Refresh Rate":
        vrr_ax.set_ylim(-0.35, 2.35)
        vrr_ax.set_yticks([VRR_LANE_REFRESH, VRR_LANE_CONTENT, VRR_LANE_SDP])
        vrr_ax.set_yticklabels(["Display\nrefresh", "Content\nframe ready", "Adaptive-Sync\nSDP"], fontsize=10)
    else:
        vrr_ax.set_ylim(-0.35, 1.35)
        vrr_ax.set_yticks([VRR_LANE_REFRESH, VRR_LANE_CONTENT])
        vrr_ax.set_yticklabels(["Display\nrefresh", "Content\nframe ready"], fontsize=10)

    vrr_ax.set_xticks(np.arange(0, vrr_duration_ms + 1, 20))
    vrr_ax.set_xticks(np.arange(0, vrr_duration_ms + 1, 5), minor=True)
    vrr_ax.grid(axis="x", which="major", color="#cfcfcf", linewidth=0.8, zorder=0)
    vrr_ax.grid(axis="x", which="minor", color="#ebebeb", linewidth=0.5, zorder=0)

    vrr_ax.tick_params(axis="x", which="major", labelsize=10)
    vrr_ax.tick_params(axis="y", which="both", length=0)
    for spine in ["top", "right", "left"]:
        vrr_ax.spines[spine].set_visible(False)
    vrr_ax.spines["bottom"].set_color("#bbbbbb")

    vrr_ax.set_xlabel("Time (ms)   —   major grid 20 ms/div, minor grid 5 ms/div", fontsize=10, labelpad=10)
    vrr_ax.set_title(vrr_mode, fontsize=14, fontweight="bold", pad=14)

    vrr_fig.tight_layout()
    st.pyplot(vrr_fig)

    vrr_frame_intervals_ms = np.diff(vrr_refresh_times)
    vrr_vtotal_lines = (vrr_frame_intervals_ms * 1000.0) / vrr_line_time_us
    vrr_vblank_lines = vrr_vtotal_lines - vrr_vactive

    if vrr_mode != "Fixed Refresh Rate":
        st.caption(
            "🟪 **Adaptive-Sync SDP** — a Secondary-Data Packet sent once per frame during the "
            "**Vblank** of the *previous* frame, carrying the updated **Vtotal / target refresh "
            "timing** (MISC/AVT metadata) the Sink should apply for the upcoming frame. "
            "The dotted line shows it landing just ahead of the corresponding Display refresh point."
        )

        # ── Adaptive-Sync SDP payload values ─────────────────────────────
        vrr_vtotal_min = vrr_vactive + 1
        vrr_vtotal_nominal = round((vrr_base_period * 1000.0) / vrr_line_time_us)
        vrr_vtotal_max = vrr_vtotal_nominal * 2  # illustrative panel-supported ceiling

        sdp_rows = []
        for i, (vt, vb, interval) in enumerate(zip(vrr_vtotal_lines, vrr_vblank_lines, vrr_frame_intervals_ms)):
            sdp_rows.append({
                "SDP #": i + 1,
                "Sent at (ms)": round(vrr_sdp_times[i], 2),
                "HB1 Packet Type": "Adaptive-Sync SDP",
                "HB2 Revision": "0x01",
                "HB3 Data Size": "0x20 (32B)",
                "DB[0:1] Target Vtotal (lines)": round(vt),
                "DB[2] AVT/FAVT Mode": "0 = AVT" if vrr_sub_mode == "AVT" else "1 = FAVT",
                "DB[3:4] Vtotal Min (lines)": vrr_vtotal_min,
                "DB[5:6] Vtotal Max (lines)": vrr_vtotal_max,
                "DB[7] Frame-Sync/Update Flag": 1,
                "Resulting Refresh Rate (Hz)": round(1000.0 / interval, 2),
            })
        df_sdp = pd.DataFrame(sdp_rows)
        st.markdown("##### Adaptive-Sync SDP payload — value carried by each purple marker")
        st.dataframe(df_sdp, use_container_width=True, hide_index=True)
        st.caption(
            "⚠️ Header/payload **field names and byte offsets above are illustrative** "
            "(general SDP structure: HB0–HB3 header, DB0–DB31 payload) to show *what* "
            "information an Adaptive-Sync SDP conveys per frame. The official VESA "
            "DisplayPort spec defines the exact Packet Type code, revision number, and "
            "bit-level DB field layout — substitute those values here if you have the spec on hand."
        )

    # --- Vblank / Vtotal chart ---
    st.markdown("#### Per-frame Vblank duration")

    st.markdown(
        "Adaptive-Sync keeps **pixel clock** and **Htotal** fixed, and varies **Vtotal** by "
        "stretching/shrinking **Vblank** so each frame's duration matches the refresh interval above."
    )

    vrr_fig2, vrr_ax2 = plt.subplots(figsize=(11, 3))
    vrr_fig2.patch.set_facecolor("white")
    vrr_ax2.set_facecolor("white")

    vrr_x_pos = np.arange(len(vrr_vblank_lines))
    vrr_bar_color = VRR_BLUE if vrr_mode != "Fixed Refresh Rate" else VRR_GRAY
    vrr_ax2.bar(vrr_x_pos, vrr_vblank_lines, color=vrr_bar_color, width=0.6, zorder=2)
    # Dashed line = base Vtotal's Vblank (minimum floor for FAVT)
    vrr_base_vblank = vrr_base_vtotal - vrr_vactive
    vrr_ax2.axhline(vrr_base_vblank, color="#e07b00", linewidth=1.2, zorder=1,
                    linestyle="--", label=f"Base Vblank = {vrr_base_vblank:.0f} lines (floor)")

    for x, v in zip(vrr_x_pos, vrr_vblank_lines):
        vrr_ax2.text(x, v + max(vrr_vblank_lines) * 0.02, f"{v:.0f}",
                      ha="center", va="bottom", fontsize=8, color="#444444")

    vrr_ax2.set_xticks(vrr_x_pos)
    vrr_ax2.set_xticklabels([f"F{i+1}" for i in vrr_x_pos], fontsize=9)
    vrr_ax2.set_ylabel("Vblank (lines)", fontsize=10)
    vrr_ax2.set_title("Vblank lines added per frame to match refresh timing", fontsize=12, pad=10)

    for spine in ["top", "right"]:
        vrr_ax2.spines[spine].set_visible(False)
    vrr_ax2.spines["left"].set_color("#bbbbbb")
    vrr_ax2.spines["bottom"].set_color("#bbbbbb")
    vrr_ax2.grid(axis="y", color="#ebebeb", linewidth=0.7, zorder=0)

    vrr_fig2.tight_layout()
    st.pyplot(vrr_fig2)

    if vrr_mode == "Fixed Refresh Rate":
        st.caption(
            "Fixed refresh rate → Vtotal/Vblank is constant every frame (orange dashed = base Vblank)."
        )
    elif vrr_sub_mode == "AVT":
        st.caption(
            "AVT → Vblank varies freely per frame to align refresh exactly with content readiness. "
            "Orange dashed line = base Vblank (floor). Bars may go above or below freely."
        )
    else:
        st.caption(
            "FAVT → Source only *adds* lines above base Vblank (orange dashed = floor, bars never go below). "
            "Integer line counts are dithered frame-to-frame so the average refresh rate exactly matches "
            "the actual content cadence."
        )

    with st.expander("Show per-frame calculation breakdown"):
        st.markdown(
            f"**Line time** = Htotal / pclk = {vrr_htotal} / {vrr_pclk_mhz} MHz = "
            f"**{vrr_line_time_us:.3f} µs/line**"
        )
        vrr_rows = []
        for i, (interval, vt, vb) in enumerate(
                zip(vrr_frame_intervals_ms, vrr_vtotal_lines, vrr_vblank_lines), start=1):
            vrr_rows.append(
                {
                    "Frame": f"F{i}",
                    "Interval (ms)": f"{interval:.2f}",
                    "Vtotal = interval(µs) / line_time": f"{interval*1000:.1f} / {vrr_line_time_us:.3f} = {vt:.1f}",
                    "Vblank = Vtotal - Vactive": f"{vt:.1f} - {vrr_vactive} = {vb:.1f}",
                }
            )
        st.table(vrr_rows)

    # --- Stats ---
    st.markdown("#### Stats")

    if vrr_mode == "Fixed Refresh Rate":
        vrr_waits = []
        for c in vrr_content_ready:
            next_refresh = vrr_refresh_times[vrr_refresh_times >= c]
            if len(next_refresh) > 0:
                vrr_waits.append(next_refresh[0] - c)
        vrr_waits = np.array(vrr_waits)
        wcol1, wcol2, wcol3 = st.columns(3)
        wcol1.metric("Avg wait for next refresh (ms)", f"{vrr_waits.mean():.2f}")
        wcol2.metric("Max wait / stutter risk (ms)", f"{vrr_waits.max():.2f}")
        wcol3.metric("Avg Vblank (lines)", f"{vrr_vblank_lines.mean():.1f}")
        st.caption(
            "With a fixed refresh rate, frames that miss the refresh window must wait "
            "until the next tick, causing variable latency, judder, or tearing."
        )
    else:
        vrr_intervals = np.diff(vrr_refresh_times)
        vrr_content_intervals = np.diff(vrr_content_ready)
        vrr_avg_content_fps  = 1000.0 / vrr_content_intervals.mean()
        vrr_avg_refresh_fps  = 1000.0 / vrr_intervals.mean()
        vrr_fps_match = abs(vrr_avg_refresh_fps - vrr_avg_content_fps) < 0.05

        st.markdown("**Refresh timing**")
        icol1, icol2, icol3, icol4 = st.columns(4)
        icol1.metric("Min refresh interval (ms)", f"{vrr_intervals.min():.2f}")
        icol2.metric("Max refresh interval (ms)", f"{vrr_intervals.max():.2f}")
        icol3.metric("Avg refresh interval (ms)", f"{vrr_intervals.mean():.2f}")
        icol4.metric("Avg Vblank (lines)", f"{vrr_vblank_lines.mean():.1f}")

        st.markdown("**Frame rate comparison (FAVT spec check)**")
        fcol1, fcol2, fcol3 = st.columns(3)
        fcol1.metric("Avg content frame rate (fps)", f"{vrr_avg_content_fps:.2f}",
                     help="Actual cadence of content_ready timestamps (includes jitter + clipping effects)")
        fcol2.metric("Avg display refresh rate (fps)", f"{vrr_avg_refresh_fps:.2f}",
                     help="Average fps from display refresh timestamps")
        fcol3.metric("Match (fps diff)", f"{abs(vrr_avg_refresh_fps - vrr_avg_content_fps):.4f}",
                     delta="✓ Exact match" if vrr_fps_match else f"✗ {abs(vrr_avg_refresh_fps - vrr_avg_content_fps):.4f} fps off",
                     delta_color="normal" if vrr_fps_match else "inverse")

        if vrr_sub_mode == "FAVT":
            st.caption(
                f"❄¹️ The slider shows {vrr_base_fps} fps but the **actual content cadence is "
                f"{vrr_avg_content_fps:.2f} fps** due to per-frame jitter and the 200ms window "
                f"clipping the final frame. FAVT dithers Vtotal so the average display rate "
                f"matches the actual content cadence — not the nominal slider value."
            )
        else:
            st.caption(
                "AVT: panel refreshes exactly when each frame is ready — "
                "display rate tracks content cadence perfectly by definition."
            )


# ── Customer Projects Tab ───────────────────────────────────────────────────────
with tab_cust:
    sub_proj, sub_shipment = st.tabs(["\U0001F4CA Customer Projects", "\U0001F697 China car OEM Shipment"])
    with sub_proj:
        import os, re
        import pandas as pd

        _CUST_FILE = "GMSL IVI Customer Projects.xlsx"

        st.markdown("## GMSL IVI Customer Projects")

        if not os.path.exists(_CUST_FILE):
            st.warning(f"File **{_CUST_FILE}** not found in the app directory. "
                       "Please place it alongside `display_interface_comparison.py`.")
        else:
            # ── load ──────────────────────────────────────────────────────────────
            _df_raw = pd.read_excel(_CUST_FILE, sheet_name=0, dtype=str)
            _df_raw.columns = [c.strip() for c in _df_raw.columns]

            # ── helpers ───────────────────────────────────────────────────────────
            _DEFAULT_BLANK_RATIO = 0.15   # fallback if column missing
            _DSC_RATIO   = {24: 3.0, 30: 3.75}  # compression ratios from app constants

            def _parse_res(s):
                """Return (width, height, diag_inch) — diag_inch may be None."""
                if not isinstance(s, str): return None, None, None
                m = re.search(r'(\d+)\s*[x×X]\s*(\d+)', s)
                if not m: return None, None, None
                w, h = int(m.group(1)), int(m.group(2))
                d = re.search(r'(\d+(?:\.\d+)?)\s*"', s)
                diag = float(d.group(1)) if d else None
                return w, h, diag

            def _parse_fps_bpp(s):
                """Return (fps, bpp) floats or (None, None)."""
                if not isinstance(s, str): return None, None
                fps = bpp = None
                m = re.search(r'(\d+(?:\.\d+)?)\s*[Hh]z', s)
                if m: fps = float(m.group(1))
                m = re.search(r'(\d+)\s*bpp', s, re.IGNORECASE)
                if m: bpp = int(m.group(1))
                return fps, bpp

            def _parse_blank(s, default):
                """Parse blanking ratio from cell; value may be 0.05 (fraction) or 5 (percent)."""
                try:
                    v = float(s)
                    return v / 100.0 if v > 1 else v   # >1 means it was given as percent
                except (ValueError, TypeError):
                    return default

            # ── compute derived columns ───────────────────────────────────────────
            _rows = []
            _res_col   = next((c for c in _df_raw.columns if 'resolution' in c.lower()), None)
            _fps_col   = next((c for c in _df_raw.columns if 'fps' in c.lower() or 'bpp' in c.lower()), None)
            _dsc_col   = next((c for c in _df_raw.columns if c.strip().lower() == 'dsc'), None)
            _blank_col = next((c for c in _df_raw.columns if 'blank' in c.lower()), None)

            def _fmt(v):
                return f"{v:.2f}" if v is not None else "N/A"

            for _, row in _df_raw.iterrows():
                w, h, diag = _parse_res(row.get(_res_col, ''))    if _res_col   else (None, None, None)
                fps, bpp   = _parse_fps_bpp(row.get(_fps_col, '')) if _fps_col  else (None, None)
                dsc_on     = str(row.get(_dsc_col, '')).strip().lower() in ('yes', 'y', 'true', '1') if _dsc_col else False
                blank      = _parse_blank(row.get(_blank_col, ''), _DEFAULT_BLANK_RATIO) if _blank_col else _DEFAULT_BLANK_RATIO

                mp      = round(w * h / 1e6, 2)                         if w and h              else None
                ppi     = round((w**2 + h**2)**0.5 / diag, 2)           if w and h and diag     else None
                pclk    = round(w * h * fps * (1 + blank) / 1e6, 2)     if w and h and fps      else None
                raw_gbps= round(pclk * bpp / 1000, 2)                   if pclk and bpp         else None
                if raw_gbps and bpp:
                    ratio    = _DSC_RATIO.get(bpp) if dsc_on else None
                    eff_gbps = round(raw_gbps / ratio, 2) if ratio else raw_gbps
                else:
                    eff_gbps = None
                if w and h:
                    _g = math.gcd(w, h)
                    ar_str = f"{w // _g}:{h // _g}"
                else:
                    ar_str = "N/A"

                _rows.append({
                    **{c: row[c] for c in _df_raw.columns},
                    "Aspect Ratio":                   ar_str,
                    "Active Mega-Pixels (MP)":        _fmt(mp),
                    "PPI":                            _fmt(ppi),
                    "PCLK (MHz)":                     _fmt(pclk),
                    "Raw Video Payload (Gbps)":       _fmt(raw_gbps),
                    "Effective Video Payload (Gbps)": _fmt(eff_gbps),
                })

            _df_out = pd.DataFrame(_rows)

            # ── format Total Blanking Ratio (%) as a percentage number ────────────
            if _blank_col and _blank_col in _df_out.columns:
                def _fmt_blank(v):
                    try:
                        f = float(v)
                        return f"{f * 100:.2f}" if f <= 1 else f"{f:.2f}"
                    except (ValueError, TypeError):
                        return v
                _df_out[_blank_col] = _df_out[_blank_col].apply(_fmt_blank)

            # ── reorder: all non-calculated first, then calculated at the end ─────
            _calc_cols = [
                "Aspect Ratio", "Active Mega-Pixels (MP)", "PPI", "PCLK (MHz)",
                "Raw Video Payload (Gbps)", "Effective Video Payload (Gbps)",
            ]
            _base_cols = [c for c in _df_out.columns if c not in _calc_cols]
            _df_display = _df_out[_base_cols + _calc_cols].copy()
            _df_display["_mp_sort"] = pd.to_numeric(_df_display["Active Mega-Pixels (MP)"], errors="coerce")
            _df_display = _df_display.sort_values("_mp_sort", ascending=False, na_position="last") \
                                     .drop(columns=["_mp_sort"]).reset_index(drop=True)

            # ── colour-code calculated cells ──────────────────────────────────────
            def _style_calc(df):
                styles = pd.DataFrame("", index=df.index, columns=df.columns)
                for col in _calc_cols:
                    if col in df.columns:
                        styles[col] = df[col].apply(
                            lambda v: "background-color:#e0f2fe; color:#0369a1; font-weight:600"
                            if str(v) not in ("N/A", "nan", "") else "color:#94a3b8"
                        )
                return styles

            # ── legend + note ─────────────────────────────────────────────────────
            _lcol1, _lcol2, _lcol3 = st.columns(3)
            _lcol1.markdown(
                "<span style='display:inline-block;width:14px;height:14px;"
                "background:#1e3a5f;border-radius:2px;vertical-align:middle;margin-right:6px'></span>"
                "<small><b>Input columns</b></small>", unsafe_allow_html=True)
            _lcol2.markdown(
                "<span style='display:inline-block;width:14px;height:14px;"
                "background:#0369a1;border-radius:2px;vertical-align:middle;margin-right:6px'></span>"
                "<small><b>Calculated columns</b> (PCLK = H×V×FPS×(1+blank); "
                "DSC: 3.0:1 @24bpp, 3.75:1 @30bpp)</small>", unsafe_allow_html=True)
            _blank_src = "from file" if _blank_col else "default 15%"
            _lcol3.markdown(
                f"<small style='color:#64748b'>Blanking ratio: {_blank_src}</small>",
                unsafe_allow_html=True)

            # ── build HTML table ──────────────────────────────────────────────────
            _INPUT_COLS = [c for c in _df_display.columns if c not in _calc_cols]

            _th_input = "background:#1e3a5f;color:#ffffff;font-size:14px;padding:10px 14px;" \
                        "text-align:center;white-space:nowrap;border:1px solid #2d4a6e"
            _th_calc  = "background:#0369a1;color:#ffffff;font-size:14px;padding:10px 14px;" \
                        "text-align:center;white-space:nowrap;border:1px solid #1d4f7a;" \
                        "cursor:pointer;user-select:none"
            _td_base  = "font-size:14px;padding:9px 13px;border:1px solid #e2e8f0;" \
                        "white-space:nowrap;text-align:center"
            _td_calc  = _td_base + ";background:#eff6ff;color:#1e40af;font-weight:600"
            _td_na    = _td_base + ";color:#94a3b8"

            _SORTABLE_INPUT_COLS = ["OEM", "SOP"]
            _calc_idx = [i for i, c in enumerate(_df_display.columns) if c in _calc_cols]
            _sortable_input_idx = [i for i, c in enumerate(_df_display.columns) if c in _SORTABLE_INPUT_COLS]
            _mp_col_idx = next((i for i, c in enumerate(_df_display.columns) if c == "Active Mega-Pixels (MP)"), 0)

            # Column headers that should wrap onto two lines to save width
            _wrap_labels = {
                "Total Blanking Ratio (%)": "Total Blanking<br>Ratio (%)",
                "Raw Video Payload (Gbps)": "Raw Video<br>Payload (Gbps)",
                "Effective Video Payload (Gbps)": "Effective Video<br>Payload (Gbps)",
                "Active Mega-Pixels (MP)": "Active<br>Mega-Pixels (MP)",
            }
            _th_input_wrap = _th_input.replace("white-space:nowrap;", "")
            _th_calc_wrap  = _th_calc.replace("white-space:nowrap;", "")

            _html = ["<div style='overflow-x:auto'>",
                     "<table id='cust_tbl' style='border-collapse:collapse;width:100%;font-family:Arial,sans-serif'>",
                     "<thead><tr>"]
            _th_input_sortable = _th_input + ";cursor:pointer;user-select:none"
            _th_input_sortable_wrap = _th_input_wrap + ";cursor:pointer;user-select:none"
            for i, c in enumerate(_df_display.columns):
                _label = _wrap_labels.get(c, c)
                _wrap  = c in _wrap_labels
                if i in _calc_idx:
                    _arrow = "&#9660;" if c == "Active Mega-Pixels (MP)" else "&#9661;"  # ▼ vs ▽
                    _th_style = _th_calc_wrap if _wrap else _th_calc
                    _html.append(
                        f"<th data-col='{i}' "
                        f"style='{_th_style}' title='Click to sort'>{_label} {_arrow}</th>"
                    )
                elif i in _sortable_input_idx:
                    _th_style = _th_input_sortable_wrap if _wrap else _th_input_sortable
                    _html.append(
                        f"<th data-col='{i}' "
                        f"style='{_th_style}' title='Click to sort'>{_label} &#9661;</th>"
                    )
                else:
                    _th_style = _th_input_wrap if _wrap else _th_input
                    _html.append(f"<th style='{_th_style}'>{_label}</th>")
            _html.append("</tr></thead><tbody>")

            for i, (_, row) in enumerate(_df_display.iterrows()):
                _row_bg = "" if i % 2 == 0 else "background:#f8fafc"
                _html.append(f"<tr style='{_row_bg}'>")
                for c in _df_display.columns:
                    v = str(row[c]) if str(row[c]) not in ("nan", "None", "") else "—"
                    if c in _calc_cols:
                        _style = _td_na if v in ("N/A", "—") else _td_calc
                    else:
                        _style = _td_base + (";background:#f8fafc" if i % 2 != 0 else "")
                        if c == _dsc_col:
                            if v.lower() == "yes":
                                v = "<span style='background:#dcfce7;color:#166534;padding:2px 8px;" \
                                    "border-radius:10px;font-size:13px;font-weight:600'>Yes</span>"
                            elif v.lower() == "no":
                                v = "<span style='background:#fee2e2;color:#991b1b;padding:2px 8px;" \
                                    "border-radius:10px;font-size:13px;font-weight:600'>No</span>"
                        elif c in ("Serializer", "Deserializer"):
                            if v.lower() == "not used":
                                _style += ";color:#dc2626"
                            elif v.upper() == "FPDLINK":
                                _style += ";color:#dc2626;font-weight:600"
                            elif v.upper().startswith("MAX") or v.upper().startswith("CP"):
                                _style += ";color:#1d4ed8;font-weight:600"
                    _html.append(f"<td style='{_style}'>{v}</td>")
                _html.append("</tr>")

            _js_init = "{" + str(_mp_col_idx) + ": false}"
            _html.append("</tbody></table></div>")
            _html.append("<script>")
            _html.append("(function(){")
            _html.append(f"  var _sortState = {_js_init};")
            _html.append("""
      function sortTbl(th) {
        var col = parseInt(th.getAttribute('data-col'));
        var asc = !_sortState[col];
        _sortState = {};
        _sortState[col] = asc;
        var tbl = document.getElementById('cust_tbl');
        var tbody = tbl.querySelector('tbody');
        var rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort(function(a, b) {
          var av = a.cells[col] ? a.cells[col].innerText.trim() : '';
          var bv = b.cells[col] ? b.cells[col].innerText.trim() : '';
          if (av === 'N/A' || av === '—') return 1;
          if (bv === 'N/A' || bv === '—') return -1;
          var an = parseFloat(av), bn = parseFloat(bv);
          var cmp = (!isNaN(an) && !isNaN(bn)) ? (an - bn) : av.localeCompare(bv);
          return asc ? cmp : -cmp;
        });
        rows.forEach(function(r, i) {
          r.style.background = i % 2 === 0 ? '' : '#f8fafc';
          tbody.appendChild(r);
        });
        tbl.querySelectorAll('th[data-col]').forEach(function(h) {
          var c = parseInt(h.getAttribute('data-col'));
          h.innerHTML = h.innerHTML.replace(/ [▲▼▽]$/, '') +
                        (c === col ? (asc ? ' ▲' : ' ▼') : ' ▽');
        });
      }
      document.getElementById('cust_tbl').querySelectorAll('th[data-col]').forEach(function(th){
        th.addEventListener('click', function(){ sortTbl(this); });
      });
    })();
    """)
            _html.append("</script>")
            import streamlit.components.v1 as _components
            _components.html("\n".join(_html), height=max(400, 42 * (len(_df_display) + 2)), scrolling=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── download button ───────────────────────────────────────────────────
            import io as _io
            _buf = _io.BytesIO()
            with pd.ExcelWriter(_buf, engine="openpyxl") as _xw:
                _df_display.to_excel(_xw, index=False, sheet_name="Customer Projects")
            st.download_button(
                "⬇ Download as Excel",
                data=_buf.getvalue(),
                file_name="GMSL_IVI_Customer_Projects_calculated.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # ── Resolution / Size / Raw Video Payload relationship charts ──────────
            st.markdown("---")
            st.markdown("## 📈 Resolution, Size & Raw Video Payload")
            st.caption(
                "Relationships between each project's resolution (Active Megapixels), screen "
                "diagonal size, and raw video payload — parsed from 'Resolution & Size' and "
                "'FPS & BPP'. Projects with unparseable resolution or missing FPS/BPP are "
                "excluded from the relevant chart."
            )
            st.caption(
                "💡 **Legend tip:** click an OEM in the legend to show **only** that OEM "
                "(all others are hidden); click it again to restore all OEMs. Double-click "
                "toggles a single OEM on/off instead."
            )

            _oem_col = next((c for c in _df_raw.columns if c.strip().lower() == "oem"), None)
            _dtype_col = next((c for c in _df_raw.columns if c.strip().lower() == "display type"), None)
            _car_col = next((c for c in _df_raw.columns if c.strip().lower() == "car model"), None)

            _trend_rows = []
            for _, row in _df_raw.iterrows():
                w, h, diag = _parse_res(row.get(_res_col, "")) if _res_col else (None, None, None)
                if not (w and h):
                    continue
                fps, bpp = _parse_fps_bpp(row.get(_fps_col, "")) if _fps_col else (None, None)
                blank = _parse_blank(row.get(_blank_col, ""), _DEFAULT_BLANK_RATIO) if _blank_col else _DEFAULT_BLANK_RATIO
                pclk = w * h * fps * (1 + blank) / 1e6 if fps else None
                raw_gbps = pclk * bpp / 1000 if pclk and bpp else None
                _trend_rows.append({
                    "OEM": row.get(_oem_col, "Unknown") or "Unknown",
                    "Display Type": row.get(_dtype_col, "") or "",
                    "Car Model": row.get(_car_col, "") or "",
                    "Resolution": f"{w}×{h}",
                    "MP": round(w * h / 1e6, 2),
                    "Diagonal (in)": diag if diag else None,
                    "Raw Video Payload (Gbps)": round(raw_gbps, 2) if raw_gbps else None,
                    "FPS": fps if fps else None,
                    "Color Depth (bpp)": bpp if bpp else None,
                })

            _trend_df = pd.DataFrame(_trend_rows)

            if len(_trend_df) < 2:
                st.info("Not enough projects with a parseable resolution to plot relationships.")
            else:
                _payload_df = _trend_df.dropna(subset=["Raw Video Payload (Gbps)"]).copy()
                if len(_payload_df) >= 2:
                    # Alternate label position by MP rank so points close together on the
                    # x-axis don't get their text drawn on top of each other.
                    _rank = _payload_df["MP"].rank(method="first").astype(int) - 1
                    _POS_CYCLE = ["top center", "bottom center", "middle right", "middle left",
                                 "top right", "bottom left", "top left", "bottom right"]
                    _payload_df["_textpos"] = [_POS_CYCLE[i % len(_POS_CYCLE)] for i in _rank]

                    _fig_pay = go.Figure()
                    for oem in _payload_df["OEM"].unique():
                        _sub = _payload_df[_payload_df["OEM"] == oem]
                        _sizes = _sub["Diagonal (in)"].fillna(10.0)
                        _fig_pay.add_trace(go.Scatter(
                            x=_sub["MP"], y=_sub["Raw Video Payload (Gbps)"], mode="markers+text", name=oem,
                            marker=dict(size=_sizes * 1.6, sizemin=8, opacity=0.8,
                                       line=dict(width=1, color="#1e293b")),
                            text=[f"[{mp:.1f} MP, {pay:.1f} Gbps]" for mp, pay in
                                 zip(_sub["MP"], _sub["Raw Video Payload (Gbps)"])],
                            textposition=_sub["_textpos"].tolist(),
                            textfont=dict(size=14, color="#0f172a"),
                            customdata=_sub[["Resolution", "Display Type", "Car Model", "Diagonal (in)",
                                            "FPS", "Color Depth (bpp)"]],
                            hovertemplate=(
                                "<b>%{customdata[0]}</b><br>Active MP: %{x}<br>Raw Payload: %{y} Gbps<br>"
                                "Display Type: %{customdata[1]}<br>Car Model: %{customdata[2]}<br>"
                                "Screen Size: %{customdata[3]}\"<br>FPS: %{customdata[4]} Hz<br>"
                                "Color Depth: %{customdata[5]} bpp<extra>%{fullData.name}</extra>"
                            ),
                        ))
                    # eDP HBR3 (4-lane) effective bandwidth: 4 x 8.1 Gbps x 80% (8b/10b) = 25.92 Gbps.
                    # Shade the region AT OR BELOW it in light green -- these are the projects we
                    # can support on a single 4-lane eDP HBR3 link, uncompressed.
                    _edp_4l_gbps = 4 * 8.1 * 0.8
                    # GMSL3 (1 link, 9.7 Gbps) carrying DSC-compressed video at 3.75:1 (30bpp):
                    # equivalent uncompressed payload = 9.7 x 3.75 = 36.375 Gbps.
                    _gmsl3_dsc_gbps = 9.7 * 3.75
                    _ymax = max(_payload_df["Raw Video Payload (Gbps)"].max(),
                               _edp_4l_gbps, _gmsl3_dsc_gbps) * 1.15
                    _fig_pay.add_shape(
                        type="rect", xref="paper", x0=0, x1=1, yref="y",
                        y0=0, y1=_gmsl3_dsc_gbps,
                        fillcolor="rgba(37,99,235,0.08)", line=dict(width=0), layer="below",
                    )
                    _fig_pay.add_shape(
                        type="rect", xref="paper", x0=0, x1=1, yref="y",
                        y0=0, y1=_edp_4l_gbps,
                        fillcolor="rgba(22,163,74,0.10)", line=dict(width=0), layer="below",
                    )
                    _fig_pay.add_hline(
                        y=_edp_4l_gbps, line_dash="dash", line_color="#16a34a", line_width=2.5,
                        annotation_text=f"eDP HBR3 (4-lane) Max: {_edp_4l_gbps:.2f} Gbps",
                        annotation_position="top left",
                        annotation_font=dict(size=14, color="#16a34a"),
                    )
                    _fig_pay.add_hline(
                        y=_gmsl3_dsc_gbps, line_dash="dash", line_color="#2563eb", line_width=2.5,
                        annotation_text=(
                            "GMSL3 (1 link) + DSC Pass-through (3.75:1 for 30bpp), "
                            f"Max: {_gmsl3_dsc_gbps:.3f} Gbps"
                        ),
                        annotation_position="top left",
                        annotation_font=dict(size=14, color="#2563eb"),
                    )
                    _fig_pay.update_layout(
                        title=dict(text="Active Resolution (MP) vs. Raw Video Payload (Gbps)",
                                  font=dict(size=24, color="#0f172a")),
                        xaxis=dict(title=dict(text="Active Megapixels (MP)", font=dict(size=20, color="#0f172a")),
                                  tickfont=dict(size=18, color="#0f172a"),
                                  showgrid=True, gridcolor="#e2e8f0",
                                  ticks="outside", ticklen=7, tickwidth=1.5, tickcolor="#334155",
                                  minor=dict(ticks="outside", ticklen=4, tickwidth=1,
                                            tickcolor="#94a3b8", showgrid=True, gridcolor="#f1f5f9")),
                        yaxis=dict(title=dict(text="Raw Video Payload (Gbps)", font=dict(size=20, color="#0f172a")),
                                  tickfont=dict(size=18, color="#0f172a"),
                                  showgrid=True, gridcolor="#e2e8f0",
                                  ticks="outside", ticklen=7, tickwidth=1.5, tickcolor="#334155",
                                  minor=dict(ticks="outside", ticklen=4, tickwidth=1,
                                            tickcolor="#94a3b8", showgrid=True, gridcolor="#f1f5f9")),
                        height=740, margin=dict(t=130, b=60, l=70, r=40),
                        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                        legend=dict(font=dict(size=15, color="#0f172a"),
                                   orientation="h", yanchor="bottom", y=1.02,
                                   xanchor="center", x=0.5,
                                   itemclick="toggleothers", itemdoubleclick="toggle"),
                        font=dict(size=18, color="#0f172a"),
                    )
                    st.plotly_chart(_fig_pay, use_container_width=True)
                    st.caption(
                        "Marker size is proportional to screen diagonal. Spread around a "
                        "straight-line relationship reflects differing frame rate, bpp, "
                        "blanking ratio, and DSC compression across projects."
                    )
                    st.caption(
                        "🟢 **Light green region (at or below the green line)** = projects we can "
                        "support on a single 4-lane eDP HBR3 link, uncompressed — **25.92 Gbps** "
                        "max (4 × 8.1 Gbps × 80% 8b/10b efficiency).  \n"
                        "🔵 **Light blue region (at or below the blue line)** = projects we can "
                        "support on a single GMSL3 link using DSC 3.75:1 compression (30bpp) — "
                        "**36.38 Gbps** max equivalent payload (9.7 Gbps × 3.75).  \n"
                        "Projects above *both* lines need additional lanes/links, a different "
                        "DSC ratio, or a different interface entirely to fit."
                    )

                _size_df = _trend_df.dropna(subset=["Diagonal (in)"])
                if len(_size_df) >= 2:
                    _fig_sz = go.Figure()
                    for oem in _size_df["OEM"].unique():
                        _sub = _size_df[_size_df["OEM"] == oem]
                        _fig_sz.add_trace(go.Scatter(
                            x=_sub["Diagonal (in)"], y=_sub["MP"], mode="markers", name=oem,
                            marker=dict(size=12, opacity=0.8, line=dict(width=1, color="#1e293b")),
                            customdata=_sub[["Resolution", "Display Type", "Car Model"]],
                            hovertemplate=(
                                "<b>%{customdata[0]}</b><br>Screen Size: %{x}\"<br>Active MP: %{y}<br>"
                                "Display Type: %{customdata[1]}<br>Car Model: %{customdata[2]}"
                                "<extra>%{fullData.name}</extra>"
                            ),
                        ))
                    _fig_sz.update_layout(
                        title=dict(text="Screen Diagonal Size vs. Active Resolution (MP)",
                                  font=dict(size=24, color="#0f172a")),
                        xaxis=dict(title=dict(text="Diagonal Size (inches)", font=dict(size=20, color="#0f172a")),
                                  tickfont=dict(size=18, color="#0f172a"),
                                  showgrid=True, gridcolor="#e2e8f0",
                                  ticks="outside", ticklen=7, tickwidth=1.5, tickcolor="#334155",
                                  minor=dict(ticks="outside", ticklen=4, tickwidth=1,
                                            tickcolor="#94a3b8", showgrid=True, gridcolor="#f1f5f9")),
                        yaxis=dict(title=dict(text="Active Megapixels (MP)", font=dict(size=20, color="#0f172a")),
                                  tickfont=dict(size=18, color="#0f172a"),
                                  showgrid=True, gridcolor="#e2e8f0",
                                  ticks="outside", ticklen=7, tickwidth=1.5, tickcolor="#334155",
                                  minor=dict(ticks="outside", ticklen=4, tickwidth=1,
                                            tickcolor="#94a3b8", showgrid=True, gridcolor="#f1f5f9")),
                        height=540, margin=dict(t=130, b=60, l=70, r=40),
                        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                        legend=dict(font=dict(size=15, color="#0f172a"),
                                   orientation="h", yanchor="bottom", y=1.02,
                                   xanchor="center", x=0.5,
                                   itemclick="toggleothers", itemdoubleclick="toggle"),
                        font=dict(size=18, color="#0f172a"),
                    )
                    st.plotly_chart(_fig_sz, use_container_width=True)
                    st.caption(
                        "Higher points at the same screen size indicate a higher-PPI (sharper) "
                        "display for that diagonal."
                    )

                _bar_df = _payload_df.copy()
                if len(_bar_df) >= 2:
                    _bar_df["Label"] = _bar_df["Car Model"].where(_bar_df["Car Model"] != "", _bar_df["Resolution"])
                    _bar_df = _bar_df.sort_values("Raw Video Payload (Gbps)", ascending=True)
                    _fig_bar = go.Figure(go.Bar(
                        x=_bar_df["Raw Video Payload (Gbps)"], y=_bar_df["Label"], orientation="h",
                        marker_color="#2563eb",
                        text=[f"{v:.2f}" for v in _bar_df["Raw Video Payload (Gbps)"]],
                        textposition="outside",
                        customdata=_bar_df[["Resolution", "OEM"]],
                        hovertemplate="<b>%{y}</b><br>OEM: %{customdata[1]}<br>Resolution: %{customdata[0]}<br>"
                                     "Raw Payload: %{x} Gbps<extra></extra>",
                    ))
                    _fig_bar.update_layout(
                        title=dict(text="Raw Video Payload by Project (Gbps)",
                                  font=dict(size=24, color="#0f172a")),
                        xaxis=dict(title=dict(text="Raw Video Payload (Gbps)", font=dict(size=20, color="#0f172a")),
                                  tickfont=dict(size=18, color="#0f172a"),
                                  showgrid=True, gridcolor="#e2e8f0",
                                  ticks="outside", ticklen=7, tickwidth=1.5, tickcolor="#334155",
                                  minor=dict(ticks="outside", ticklen=4, tickwidth=1,
                                            tickcolor="#94a3b8", showgrid=True, gridcolor="#f1f5f9")),
                        yaxis=dict(tickfont=dict(size=17, color="#0f172a")),
                        height=max(420, 42 * len(_bar_df)), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                        font=dict(size=18, color="#0f172a"), margin=dict(l=10, r=80),
                    )
                    _fig_bar.update_traces(textfont=dict(size=16, color="#0f172a"))
                    st.plotly_chart(_fig_bar, use_container_width=True)

    with sub_shipment:
        st.markdown("## China Car OEM Shipment (2025) & Display Panel Maker Shipments")
        st.caption(
            "2025 full-year China OEM vehicle shipment ranking, and global automotive "
            "display panel maker shipment ranking (2024 data, latest available), for "
            "context on which panel makers likely supply the highest-volume OEMs."
        )

        import pandas as pd
        import plotly.graph_objects as go

        # ── 2025 China OEM shipment data ────────────────────────────────────
        _oem_ship_df = pd.DataFrame([
            {"OEM": "BYD",            "Shipments (units)": 4602436, "Category": "Group (ICE + NEV)"},
            {"OEM": "SAIC Group",     "Shipments (units)": 4507000, "Category": "Group (ICE + NEV)"},
            {"OEM": "FAW",            "Shipments (units)": 3302000, "Category": "Group (ICE + NEV)"},
            {"OEM": "Geely Auto",     "Shipments (units)": 3025000, "Category": "Group (ICE + NEV)"},
            {"OEM": "Changan Auto",   "Shipments (units)": 2913000, "Category": "Group (ICE + NEV)"},
            {"OEM": "Chery",          "Shipments (units)": 2806000, "Category": "Group (ICE + NEV)"},
            {"OEM": "GAC Group",      "Shipments (units)": 2500000, "Category": "Group (ICE + NEV)"},
            {"OEM": "Great Wall Motor","Shipments (units)": 1323700, "Category": "Group (ICE + NEV)"},
            {"OEM": "Leapmotor",      "Shipments (units)": 596600,  "Category": "New Force (NEV-only)"},
            {"OEM": "Xpeng",          "Shipments (units)": 429400,  "Category": "New Force (NEV-only)"},
            {"OEM": "Li Auto",        "Shipments (units)": 406300,  "Category": "New Force (NEV-only)"},
            {"OEM": "Xiaomi",         "Shipments (units)": 350000,  "Category": "New Force (NEV-only)"},
            {"OEM": "NIO",            "Shipments (units)": 326000,  "Category": "New Force (NEV-only)"},
            {"OEM": "Zeekr",          "Shipments (units)": 224100,  "Category": "New Force (NEV-only)"},
        ]).sort_values("Shipments (units)", ascending=True)

        _color_map = {"Group (ICE + NEV)": "#2563eb", "New Force (NEV-only)": "#16a34a"}
        _fig_oem = go.Figure()
        for _cat in ["Group (ICE + NEV)", "New Force (NEV-only)"]:
            _sub = _oem_ship_df[_oem_ship_df["Category"] == _cat]
            _fig_oem.add_trace(go.Bar(
                x=_sub["Shipments (units)"],
                y=_sub["OEM"],
                orientation="h",
                name=_cat,
                marker_color=_color_map[_cat],
                text=[f"{v:,.0f}" for v in _sub["Shipments (units)"]],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Shipments: %{x:,.0f} units<br>Category: " + _cat + "<extra></extra>",
            ))
        _fig_oem.update_layout(
            title=dict(text="2025 China Car OEM Shipment Ranking", font=dict(size=24, color="#0f172a")),
            xaxis=dict(title=dict(text="Shipments (units)", font=dict(size=20, color="#0f172a")),
                      tickfont=dict(size=16, color="#0f172a"), showgrid=True, gridcolor="#e2e8f0"),
            yaxis=dict(tickfont=dict(size=16, color="#0f172a"),
                      categoryorder="array", categoryarray=_oem_ship_df["OEM"].tolist()),
            height=max(480, 42 * len(_oem_ship_df)), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font=dict(size=16, color="#0f172a"), margin=dict(l=10, r=110, t=90, b=60),
            legend=dict(font=dict(size=14, color="#0f172a"),
                       orientation="h", yanchor="bottom", y=1.02,
                       xanchor="center", x=0.5),
            showlegend=True,
        )
        st.plotly_chart(_fig_oem, use_container_width=True)
        _oem_total = _oem_ship_df["Shipments (units)"].sum()
        _oem_group_total = _oem_ship_df.loc[_oem_ship_df["Category"] == "Group (ICE + NEV)", "Shipments (units)"].sum()
        _oem_nf_total = _oem_ship_df.loc[_oem_ship_df["Category"] == "New Force (NEV-only)", "Shipments (units)"].sum()
        st.caption(
            f"**Grand total (13 OEMs shown): {_oem_total:,.0f} units** "
            f"— Groups: {_oem_group_total:,.0f}, New Force: {_oem_nf_total:,.0f}.  \n"
            "**ICE** = Internal Combustion Engine (gas/diesel vehicles). "
            "**NEV** = New Energy Vehicle (China's term for battery-EV, plug-in hybrid, and fuel-cell vehicles).  \n"
            "\U0001F535 Blue = large established auto groups — shipments include **both ICE and NEV** vehicles. "
            "\U0001F7E2 Green = NEV-focused \"new force\" brands — shipments are **NEV-only** (these brands sell no ICE vehicles). "
            "Note: Group figures include ICE + NEV; New Force figures are NEV-only — not directly comparable 1:1."
        )
        st.caption(
            "SGM (SAIC-GM) is a joint-venture subsidiary "
            "**rolled into the SAIC Group total** shown above, not a separately-ranked group. "
            "SAIC Group's 4,507,000 units include all of its JVs/brands combined:  \n"
            "• **SAIC-GM (SGM)** — Buick, Chevrolet, Cadillac (the JV with General Motors)  \n"
            "• **SAIC-GM-Wuling** — a separate JV, also rolled into SAIC Group's total  \n"
            "• **SAIC Volkswagen** — the JV with VW  \n"
            "• **SAIC Motor's own brands** — Roewe, MG, etc."
        )
        st.caption(
            "**GAC Group (广汽集团)** total includes both JV and domestic brands. "
            "GAC's own China domestic brands are:  \n"
            "• **Trumpchi (传祺)** — ICE + PHEV; key models: GS4, GS8, M8, E8, S7  \n"
            "• **Aion (埃安)** — NEV-only (BEV); key models: Aion S, Aion Y, Aion LX, Hyper GT, Hyper HT (~480K units in 2025)  \n"
            "GAC's JV brands (not domestic) include **GAC-Toyota** and **GAC-Honda**."
        )

        st.markdown("---")

        # ── Global automotive display panel maker shipment ranking (2025e) ─
        _panel_df = pd.DataFrame([
            {"Ranking": 1,  "Panel Maker": "BOE",           "Shipments (K units)": 46029, "Share (%)": 18, "YoY (%)": 6,   "Change": 0},
            {"Ranking": 2,  "Panel Maker": "Tianma",        "Shipments (K units)": 42123, "Share (%)": 17, "YoY (%)": 13,  "Change": 0},
            {"Ranking": 3,  "Panel Maker": "AUO",           "Shipments (K units)": 25821, "Share (%)": 10, "YoY (%)": 14,  "Change": 0},
            {"Ranking": 4,  "Panel Maker": "LG Display",    "Shipments (K units)": 18470, "Share (%)": 7,  "YoY (%)": -10, "Change": 0},
            {"Ranking": 5,  "Panel Maker": "China Star",    "Shipments (K units)": 18019, "Share (%)": 7,  "YoY (%)": 54,  "Change": 6},
            {"Ranking": 6,  "Panel Maker": "Japan Display", "Shipments (K units)": 17560, "Share (%)": 7,  "YoY (%)": -12, "Change": -1},
            {"Ranking": 7,  "Panel Maker": "IVO",           "Shipments (K units)": 16141, "Share (%)": 6,  "YoY (%)": 8,   "Change": -1},
            {"Ranking": 8,  "Panel Maker": "HannStar",      "Shipments (K units)": 15691, "Share (%)": 6,  "YoY (%)": 20,  "Change": -1},
            {"Ranking": 9,  "Panel Maker": "Innolux Corp.", "Shipments (K units)": 12847, "Share (%)": 5,  "YoY (%)": -1,  "Change": 0},
            {"Ranking": 10, "Panel Maker": "Sharp",         "Shipments (K units)": 11770, "Share (%)": 5,  "YoY (%)": 0,   "Change": 0},
            {"Ranking": 11, "Panel Maker": "Truly",         "Shipments (K units)": 11673, "Share (%)": 5,  "YoY (%)": -6,  "Change": -2},
            {"Ranking": 12, "Panel Maker": "Century",       "Shipments (K units)": 5457,  "Share (%)": 2,  "YoY (%)": 75,  "Change": 2},
            {"Ranking": 13, "Panel Maker": "Kyocera",       "Shipments (K units)": 3375,  "Share (%)": 1,  "YoY (%)": -15, "Change": -1},
            {"Ranking": 14, "Panel Maker": "GiantPlus",     "Shipments (K units)": 2763,  "Share (%)": 1,  "YoY (%)": 35,  "Change": 1},
            {"Ranking": 15, "Panel Maker": "Samsung",       "Shipments (K units)": 2180,  "Share (%)": 1,  "YoY (%)": 32,  "Change": 1},
            {"Ranking": 16, "Panel Maker": "HKC Display",   "Shipments (K units)": 986,   "Share (%)": 0,  "YoY (%)": -70, "Change": -3},
            {"Ranking": 17, "Panel Maker": "Everdisplay",   "Shipments (K units)": 88,    "Share (%)": 0,  "YoY (%)": -11, "Change": 1},
            {"Ranking": 18, "Panel Maker": "Toppan",        "Shipments (K units)": 36,    "Share (%)": 0,  "YoY (%)": -97, "Change": -1},
        ]).sort_values("Shipments (K units)", ascending=True)

        _fig_panel = go.Figure(go.Bar(
            x=_panel_df["Shipments (K units)"],
            y=_panel_df["Panel Maker"],
            orientation="h",
            marker_color="#7c3aed",
            text=[f"{v:,.0f}K ({s:.0f}%)" for v, s in zip(_panel_df["Shipments (K units)"], _panel_df["Share (%)"])],
            textposition="outside",
            customdata=_panel_df[["Ranking", "YoY (%)", "Change"]],
            hovertemplate="<b>%{y}</b><br>Rank: #%{customdata[0]}<br>Shipments: %{x:,.0f}K units<br>"
                         "YoY: %{customdata[1]:+.0f}%<br>Rank change: %{customdata[2]:+d}<extra></extra>",
        ))
        _fig_panel.update_layout(
            title=dict(text="2025 Global Automotive Display Panel Maker Shipment Ranking (Estimate)",
                      font=dict(size=24, color="#0f172a")),
            xaxis=dict(title=dict(text="Shipments (Thousand units)", font=dict(size=20, color="#0f172a")),
                      tickfont=dict(size=16, color="#0f172a"), showgrid=True, gridcolor="#e2e8f0"),
            yaxis=dict(tickfont=dict(size=15, color="#0f172a")),
            height=max(560, 34 * len(_panel_df)), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            font=dict(size=16, color="#0f172a"), margin=dict(l=10, r=130, t=90, b=60),
        )
        st.plotly_chart(_fig_panel, use_container_width=True)
        st.caption(
            f"Grand total 2025e: **{_panel_df['Shipments (K units)'].sum():,.0f}K units**. "
            "BOE and Tianma are confirmed display suppliers for BYD, Geely/Zeekr, Xpeng, "
            "Li Auto, NIO, and Leapmotor — making them the most likely top suppliers by "
            "volume to the highest-shipping China OEMs above. Exact per-OEM panel volumes "
            "are not publicly disclosed; this is directional context, not a verified "
            "cross-tabulation."
        )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<small style='color:#64748b'>**Notes:** "
    "Pixel clock = H×V×FPS×(1+blank_ratio).  "
    "OLDI: 4D/port @24bpp, 5D/port @30bpp, +1 clock pair always.  "
    "eDP 8b/10b efficiency = 80 %.  "
    "DSC: 3.0:1 @24bpp, 3.75:1 @30bpp — reduces effective bpp.  "
    "MSO N×M: N streams, M lanes/stream (total lanes = N×M); "
    "BW check = M × link_rate × 0.8 ≥ (total_px/N) × eff_bpp × fps.  "
    "PPI = √(H²+V²) / diagonal_in.</small>",
    unsafe_allow_html=True)

# ── DP AE Demo Tab ─────────────────────────────────────────────────────────────
with tab_dpae:
    import hashlib

    st.markdown("## 🚗 DP Automotive Extension (DP AE) — Interactive Demo")
    st.info(
        "**DP AE v1.0** (VESA, Dec 2023) layers **Functional Safety (FuSa)** and **Security** "
        "services on top of standard DP 2.1a / eDP 1.5 — without changing the core DisplayPort "
        "protocol. Select a profile and parameters below to explore the AE_SDP structure, "
        "FuSa timeline, and escalation state machine."
    )

    dpae_sub1, dpae_sub2, dpae_sub3, dpae_sub4, dpae_sub5 = st.tabs([
        "📋 Profile Explorer", "📦 AE_SDP Packet Builder",
        "⏱️ FuSa Frame Timeline", "🚨 Escalation State Machine",
        "🎬 Frozen Frame Detection Demo"
    ])

    # ── helpers ───────────────────────────────────────────────────────────────
    _AE_PROFILES = {
        0: "Profile 0 — Basic FuSa",
        1: "Profile 1 — Basic FuSa + Basic Control Plane Security",
        2: "Profile 2 — Advanced FuSa",
        3: "Profile 3 — FuSa with Enhanced Security",
    }

    _PROFILE_FEATURES = {
        "Pixel Frame CRC (CRC_PIXELS)":              [True,  True,  True,  True ],
        "CRC on MSA (CRC_MSA_DATA)":                 [True,  True,  True,  True ],
        "CRC on SDPs (CRC_SDP_DATA)":                [True,  True,  True,  True ],
        "Frame Drop / Timeout Monitoring":            [True,  True,  True,  True ],
        "Regions-of-Interest (ROI) — min count":     ["0",   "4",   "4",   "4"  ],
        "DP_AUX Messaging + DPCD Access":            [False, True,  True,  True ],
        "Basic Safety App (Get_Measure via VAL)":    [False, True,  True,  True ],
        "VESA Secure Transport Layer (VSTL)":        [False, False, True,  True ],
        "Data Plane Security (Auth + Integrity)":    [False, False, False, True ],
        "MAC on Pixels / MSA (MAC_MSA_AF_DATA)":     [False, False, False, True ],
        "MAC on AE_SDP (MAC_AE_SDP)":               [False, False, False, True ],
        "Full Integrity on AE_SDP Data":             [False, False, False, True ],
        "Data Plane Confidentiality":                [False, False, False, False],
        "Superframe Support":                        ["Opt", "Opt", "Opt", "Opt"],
    }

    # ── Tab 1 : Profile Explorer ──────────────────────────────────────────────
    with dpae_sub1:
        st.markdown("### AE Sink Profile Feature Matrix")
        st.caption("Source: VESA DP AE v1.0 Table 2-2 and Table 2-3")

        feat_rows = []
        for feat, vals in _PROFILE_FEATURES.items():
            row = {"Feature": feat}
            for p, v in enumerate(vals):
                if isinstance(v, bool):
                    row[f"Profile {p}"] = "✅ Normative" if v else "❌ Not supported"
                elif v == "Opt":
                    row[f"Profile {p}"] = "🔵 Optional"
                else:
                    row[f"Profile {p}"] = f"Min {v} ROI"
            feat_rows.append(row)

        df_feat = pd.DataFrame(feat_rows)

        def _style_profile(v):
            if "Normative" in str(v):   return "background-color:#dcfce7;color:#166534;font-weight:600"
            if "Not supported" in str(v): return "background-color:#fee2e2;color:#991b1b"
            if "Optional" in str(v):    return "background-color:#eff6ff;color:#1e40af"
            if "Min" in str(v):         return "background-color:#fef9c3;color:#854d0e"
            return ""

        styled = df_feat.style.map(_style_profile, subset=["Profile 0","Profile 1","Profile 2","Profile 3"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### Cross-Profile Compatibility")
        st.caption("Source: VESA DP AE v1.0 Table 2-3 — Higher RX profiles are fully backwards compatible")

        compat_data = {
            "AE TX \\ AE RX":  ["Profile 0", "Profile 1", "Profile 2", "Profile 3"],
            "Profile 0 TX": ["⭐ Optimal",      "🔽 Reduced Function", "🔽 Reduced Function", "🔽 Reduced Function"],
            "Profile 1 TX": ["✅ Full P0",      "⭐ Optimal",          "🔽 Reduced Function", "🔽 Reduced Function"],
            "Profile 2 TX": ["✅ Full P0",      "✅ Full P1",          "⭐ Optimal",          "🔽 Reduced Function"],
            "Profile 3 TX": ["✅ Full P0",      "✅ Full P1",          "✅ Full P2",          "⭐ Optimal"         ],
        }
        df_compat = pd.DataFrame(compat_data).set_index("AE TX \\ AE RX")

        def _style_compat(v):
            if "Optimal" in str(v):  return "background-color:#dcfce7;color:#166534;font-weight:700"
            if "Full" in str(v):     return "background-color:#eff6ff;color:#1e40af"
            if "Reduced" in str(v):  return "background-color:#fef9c3;color:#854d0e"
            return ""

        st.dataframe(df_compat.style.map(_style_compat), use_container_width=True)

        st.markdown("---")
        st.markdown("### DPCD Profile Negotiation Flow")
        st.markdown(
            "1. **AE TX reads** `CAP_AE_PROFILE` from AE RX DPCD → learns max RX capability  \n"
            "2. **AE TX writes** `AE_OPERATIONAL_PROFILE_CONFIG` → sets negotiated profile  \n"
            "3. **Constraint**: `AE_OPERATIONAL_PROFILE_CONFIG` ≤ `CAP_AE_PROFILE`  \n"
            "4. Both sides operate with full feature set of the negotiated profile"
        )

    # ── Tab 2 : AE_SDP Packet Builder ─────────────────────────────────────────
    with dpae_sub2:
        st.markdown("### AE_SDP Packet Structure Builder")
        st.caption("Constructs a simulated AE_SDP based on your profile and DSC/ROI configuration")

        bc1, bc2, bc3, bc4 = st.columns(4)
        ae_profile   = bc1.selectbox("Profile", [0, 1, 2, 3],
                                     format_func=lambda x: f"Profile {x}", key="ae_profile")
        ae_n_slices  = bc2.number_input("DSC Slice Columns (N)", min_value=1, max_value=24,
                                        value=1, step=1, key="ae_n")
        ae_r_roi     = bc3.number_input("ROI Count (R)", min_value=0, max_value=16,
                                        value=0 if ae_profile == 0 else 4, step=1, key="ae_r")
        ae_frame_id  = bc4.number_input("FRAME_ID (simulated)", min_value=0, max_value=0xFFFFFFFF,
                                        value=42, step=1, key="ae_frame_id")

        dsc_enabled = ae_n_slices > 1

        # Size calculation
        if ae_profile <= 2:
            ae_sdp_size = 36 + 4 * ae_n_slices * (1 + ae_r_roi)
        else:
            ae_sdp_size = 75 + 4 * ae_n_slices * (1 + ae_r_roi)

        st.markdown(f"#### AE_SDP Size: **{ae_sdp_size} bytes** "
                    f"({'Profile 3' if ae_profile == 3 else 'Profile 0-2'} formula: "
                    f"{'75' if ae_profile == 3 else '36'} + 4×{ae_n_slices}×(1+{ae_r_roi}))")

        # Simulate CRC values (deterministic hash for demo)
        def _sim_crc(label, frame_id):
            h = hashlib.md5(f"{label}{frame_id}".encode()).hexdigest()
            return f"0x{h[:8].upper()}"

        # Build packet field table
        hb_rows = [
            {"Section": "Header", "Field": "HB0 — Packet ID",              "Value": "0x00",   "Notes": "Secondary-data Packet ID"},
            {"Section": "Header", "Field": "HB1 — Packet Type",            "Value": "0x20",   "Notes": "VESA VSC_EXT_VESA"},
            {"Section": "Header", "Field": "HB2[1:0] — Framework Version", "Value": "0b01",   "Notes": "VSC_EXT v1 — mandatory for DP AE"},
            {"Section": "Header", "Field": "HB2[5] — Disregard Indicator", "Value": "0",      "Notes": "Fixed 0 — payload always handled"},
            {"Section": "Header", "Field": "HB2[6] — Variable Seq#",       "Value": "1",      "Notes": "Fixed 1 — chained packets"},
            {"Section": "Header", "Field": "HB2[7] — Middle of Chaining",  "Value": "1",      "Notes": "1 = more packets follow"},
            {"Section": "Header", "Field": "HB3[4:0] — Packet Sequence",   "Value": "0→31",   "Notes": "Increments per chained packet"},
            {"Section": "Header", "Field": "HB3[7:6] — New Payload Ind.",  "Value": "0",      "Notes": "Fixed 0 — AE_SDP always changes"},
            {"Section": "Payload", "Field": "DB1–3 — IEEE OUI/CID",        "Value": "3A 02 92h", "Notes": "VESA identifier"},
            {"Section": "Payload", "Field": "DB4–5 — Extended SDP Type",   "Value": "01 00h", "Notes": "AE_SDP Packet Type 1"},
            {"Section": "Payload", "Field": "DB8 — SUBFRAME_ID",           "Value": "0",      "Notes": "0 unless Superframe enabled"},
            {"Section": "Payload", "Field": "DB9 — FUSA_COMPARE",          "Value": "1",      "Notes": "1 = Sink compares FRAME_ID + CRCs"},
            {"Section": "FuSa",    "Field": "DB10–13 — FRAME_ID",          "Value": f"0x{int(ae_frame_id):08X}", "Notes": "Monotonic counter; detects frame drops"},
            {"Section": "FuSa",    "Field": "DB14–17 — CRC_MSA_DATA",      "Value": _sim_crc("MSA", ae_frame_id),   "Notes": "CRC over MSA bytes of prev frame"},
            {"Section": "FuSa",    "Field": "DB18–21 — CRC_SDP_DATA",      "Value": _sim_crc("SDP", ae_frame_id),   "Notes": "CRC over all SDPs of prev frame"},
            {"Section": "FuSa",    "Field": "DB22–25 — CRC_COMP_BYTES",    "Value": _sim_crc("COMP", ae_frame_id) if dsc_enabled else "0x00000000", "Notes": "CRC over compressed bytes (DSC only)"},
            {"Section": "FuSa",    "Field": "DB26–27 — ROI_MASK",          "Value": f"0x{(1 << ae_r_roi) - 1:04X}" if ae_r_roi > 0 else "0x0000", "Notes": f"{ae_r_roi} ROIs active"},
        ]

        # Add per-slice CRC_PIXELS rows (show up to 4 for brevity)
        for i in range(min(ae_n_slices, 4)):
            hb_rows.append({
                "Section": "FuSa",
                "Field": f"CRC_PIXELS[{i}]",
                "Value": _sim_crc(f"PIX{i}", ae_frame_id),
                "Notes": f"Pixel CRC for DSC slice column {i}"
            })
        if ae_n_slices > 4:
            hb_rows.append({"Section": "FuSa", "Field": f"CRC_PIXELS[4..{ae_n_slices-1}]",
                            "Value": "...", "Notes": f"{ae_n_slices-4} more slice CRCs"})

        # Add ROI CRCs
        for i in range(min(ae_r_roi, 4)):
            hb_rows.append({
                "Section": "FuSa",
                "Field": f"CRC_ROI[{i}]",
                "Value": _sim_crc(f"ROI{i}", ae_frame_id),
                "Notes": f"Pixel CRC for ROI {i}"
            })
        if ae_r_roi > 4:
            hb_rows.append({"Section": "FuSa", "Field": f"CRC_ROI[4..{ae_r_roi-1}]",
                            "Value": "...", "Notes": f"{ae_r_roi-4} more ROI CRCs"})

        hb_rows.append({
            "Section": "FuSa",
            "Field": "CRC_AE_SDP",
            "Value": _sim_crc("AE_SDP", ae_frame_id),
            "Notes": "CRC of entire AE_SDP payload"
        })

        # Profile 3 security fields
        if ae_profile == 3:
            hb_rows += [
                {"Section": "Security", "Field": "SECURITY_PROT",          "Value": "1",   "Notes": "Frame is security protected"},
                {"Section": "Security", "Field": "KEY_SEL",                "Value": "0",   "Notes": "Toggles per key switch"},
                {"Section": "Security", "Field": "MAC_MSA_AF_DATA [127:0]","Value": _sim_crc("MAC_MSA", ae_frame_id) + "...", "Notes": "128-bit MAC over MSA + pixels"},
                {"Section": "Security", "Field": "SECURITY_CTR [31:0]",    "Value": f"0x{int(ae_frame_id):08X}", "Notes": "Monotonic security counter"},
                {"Section": "Security", "Field": "MAC_AE_SDP [127:0]",     "Value": _sim_crc("MAC_AE", ae_frame_id) + "...", "Notes": "128-bit MAC over AE_SDP payload"},
            ]

        df_pkt = pd.DataFrame(hb_rows)

        def _style_section(v):
            colors = {"Header": "#f1f5f9", "Payload": "#fef9c3",
                      "FuSa": "#dcfce7", "Security": "#ede9fe"}
            bg = colors.get(v, "")
            return f"background-color:{bg}" if bg else ""

        st.dataframe(
            df_pkt.style.map(_style_section, subset=["Section"]),
            use_container_width=True, hide_index=True
        )
        st.caption(
            "⚠️ CRC and MAC values above are **simulated** using MD5 hashing for illustration. "
            "Real DP AE uses CRC-32 for FuSa fields and AES-128-GCM for MAC (Profile 3). "
            "FRAME_ID increments monotonically starting 2 frames after FUSA_COMPARE=1."
        )

    # ── Tab 3 : FuSa Frame Timeline ────────────────────────────────────────────
    with dpae_sub3:
        st.markdown("### Functional Safety Frame Timeline")

        st.info(
            "**Frozen Frame Detection**: The AE_SDP carries a monotonic **FRAME_ID** counter. "
            "If the Sink receives the same FRAME_ID on consecutive AE_SDPs, it knows the source "
            "is repeating (frozen) the same frame — this triggers a FuSa fault. Additionally, "
            "identical **CRC_PIXELS** values across frames confirm a frozen pixel buffer."
        )

        tc1, tc2, tc3, tc4 = st.columns(4)
        ae_fps_sim    = tc1.number_input("FPS", min_value=30, max_value=120, value=60, step=1, key="ae_fps")
        ae_num_frames = tc2.number_input("Frames to simulate", min_value=4, max_value=20, value=8, step=1, key="ae_nf")
        ae_fault_frame = tc3.number_input("Inject CRC fault at frame #", min_value=0,
                                          max_value=int(ae_num_frames), value=0,
                                          step=1, help="0 = no fault", key="ae_fault")
        ae_frozen_frame = tc4.number_input("Inject frozen frame at #", min_value=0,
                                           max_value=int(ae_num_frames), value=0,
                                           step=1, help="0 = no frozen frame", key="ae_frozen")

        frame_ms  = 1000.0 / ae_fps_sim
        vblank_pct = 0.05
        vblank_ms = frame_ms * vblank_pct
        active_ms = frame_ms - vblank_ms
        total_ms  = int(ae_num_frames) * frame_ms

        fig_ft, ax_ft = plt.subplots(figsize=(14, 5))
        fig_ft.patch.set_facecolor("white")
        ax_ft.set_facecolor("white")

        LANE_ACTIVE = 2.0
        LANE_SDP    = 1.0
        LANE_FUSA   = 0.0
        COLORS = {"active": "#3b82f6", "vblank": "#475569",
                  "sdp": "#9333ea", "fusa_ok": "#16a34a",
                  "fusa_fail": "#dc2626", "frozen": "#f59e0b"}

        frame_ids = []
        fusa_ok_list = []
        prev_frame_id = None

        for f in range(int(ae_num_frames)):
            t_start  = f * frame_ms
            t_vblank = t_start + active_ms
            is_frozen = (ae_frozen_frame > 0 and f == int(ae_frozen_frame))
            is_crc_fault = (ae_fault_frame > 0 and f == int(ae_fault_frame))

            # Active bar color — orange if frozen
            bar_color = COLORS["frozen"] if is_frozen else COLORS["active"]
            ax_ft.barh(LANE_ACTIVE, active_ms, left=t_start,
                       color=bar_color, height=0.55, zorder=2)
            # Vblank bar
            ax_ft.barh(LANE_ACTIVE, vblank_ms, left=t_vblank,
                       color=COLORS["vblank"], height=0.55, zorder=2)
            label_txt = f"Frame {f}" + (" ❄ FROZEN" if is_frozen else "")
            ax_ft.text(t_start + active_ms / 2, LANE_ACTIVE,
                       label_txt, ha="center", va="center",
                       fontsize=8, color="white", fontweight="bold")

            # FRAME_ID: frozen frame repeats previous ID
            fid = (prev_frame_id if is_frozen else f)
            frame_ids.append(fid)
            prev_frame_id = fid

            # AE_SDP marker
            sdp_t = t_vblank + vblank_ms * 0.3
            sdp_color = COLORS["frozen"] if is_frozen else COLORS["sdp"]
            ax_ft.plot(sdp_t, LANE_SDP, "s", color=sdp_color, markersize=11, zorder=3)
            ax_ft.plot([sdp_t, sdp_t], [LANE_SDP - 0.27, LANE_ACTIVE - 0.27],
                       color=sdp_color, linewidth=0.9, linestyle=":", alpha=0.7)
            ax_ft.text(sdp_t, LANE_SDP + 0.35, f"ID={fid}",
                       ha="center", fontsize=7.5, color=sdp_color, fontweight="bold")

            # FuSa compare (active from frame 2 onward)
            if f >= 2:
                # Frozen = repeated FRAME_ID detected
                id_repeat = (len(frame_ids) >= 2 and frame_ids[-1] == frame_ids[-2])
                is_fail = is_crc_fault or id_repeat
                result_color  = COLORS["fusa_fail"] if is_fail else COLORS["fusa_ok"]
                result_marker = "X" if is_fail else "o"
                result_label  = ("❄ FROZEN!" if id_repeat else "CRC FAIL!") if is_fail else "OK"
                result_t = sdp_t + vblank_ms * 0.4

                ax_ft.plot(result_t, LANE_FUSA, result_marker,
                           color=result_color, markersize=12, zorder=3,
                           markeredgecolor="white", markeredgewidth=1)
                ax_ft.text(result_t, LANE_FUSA - 0.36, result_label,
                           ha="center", fontsize=7.5, color=result_color, fontweight="bold")
                fusa_ok_list.append(not is_fail)

                if is_fail:
                    ax_ft.annotate("→ Safe State!", xy=(result_t + 1, LANE_FUSA + 0.1),
                                   fontsize=9, color=result_color, fontweight="bold", va="center")

        # ── Axes & ticks ─────────────────────────────────────────────────────
        ax_ft.set_yticks([LANE_FUSA, LANE_SDP, LANE_ACTIVE])
        ax_ft.set_yticklabels(["FuSa Compare\nResult", "AE_SDP\n(Vblank)",
                                "Video Frame\n(Active + Vblank)"], fontsize=10)

        ax_ft.set_xlabel("Time (ms)", fontsize=11)
        x_max = total_ms + frame_ms * 0.3
        ax_ft.set_xlim(0, x_max)
        ax_ft.set_ylim(-0.85, 2.85)

        # Major ticks every frame_ms, minor ticks every vblank_ms (finer grid)
        import matplotlib.ticker as ticker
        major_step = round(frame_ms)
        minor_step = max(1, round(frame_ms / 4))
        ax_ft.xaxis.set_major_locator(ticker.MultipleLocator(major_step))
        ax_ft.xaxis.set_minor_locator(ticker.MultipleLocator(minor_step))
        ax_ft.tick_params(axis="x", which="major", length=6, width=1.2, labelsize=9)
        ax_ft.tick_params(axis="x", which="minor", length=3, width=0.8)
        ax_ft.grid(axis="x", which="major", color="#d1d5db", linewidth=0.8, zorder=0)
        ax_ft.grid(axis="x", which="minor", color="#f1f5f9", linewidth=0.5, zorder=0)

        fault_info = ""
        if ae_fault_frame > 0:  fault_info += f" | ⚠ CRC fault @ Frame {int(ae_fault_frame)}"
        if ae_frozen_frame > 0: fault_info += f" | ❄ Frozen @ Frame {int(ae_frozen_frame)}"
        ax_ft.set_title(
            f"DP AE FuSa Timeline — {int(ae_fps_sim)} fps  |  frame = {frame_ms:.2f} ms  |  "
            f"Vblank = {vblank_ms:.3f} ms" + fault_info,
            fontsize=11, pad=12, fontweight="bold"
        )
        for spine in ["top", "right"]:
            ax_ft.spines[spine].set_visible(False)

        from matplotlib.lines import Line2D
        legend_elems = [
            Line2D([0],[0], color=COLORS["active"],     lw=10, label="Active Video"),
            Line2D([0],[0], color=COLORS["vblank"],     lw=10, label="Vblank"),
            Line2D([0],[0], color=COLORS["frozen"],     lw=10, label="Frozen Frame"),
            Line2D([0],[0], marker="s", color=COLORS["sdp"],      lw=0, markersize=9, label="AE_SDP (normal)"),
            Line2D([0],[0], marker="s", color=COLORS["frozen"],   lw=0, markersize=9, label="AE_SDP (frozen ID)"),
            Line2D([0],[0], marker="o", color=COLORS["fusa_ok"],  lw=0, markersize=9, label="FuSa OK"),
            Line2D([0],[0], marker="X", color=COLORS["fusa_fail"],lw=0, markersize=9, label="FuSa FAIL"),
        ]
        ax_ft.legend(handles=legend_elems, loc="upper right", fontsize=8,
                     framealpha=0.92, edgecolor="#e2e8f0")

        fig_ft.tight_layout()
        st.pyplot(fig_ft)
        st.caption(
            "**AE_SDP** is sent once per frame during Vblank, carrying CRCs from the **previous frame**. "
            "FuSa compare activates 2 frames after FUSA_COMPARE=1. "
            "**Frozen frame** is detected when FRAME_ID repeats on consecutive AE_SDPs — "
            "the Sink expects FRAME_ID to increment by 1 every frame. Identical CRC_PIXELS confirms a frozen pixel buffer."
        )

        # Per-frame table
        if fusa_ok_list:
            st.markdown("#### Per-Frame FuSa Summary")
            sim_rows = []
            for f in range(int(ae_num_frames)):
                t_sdp = f * frame_ms + active_ms + vblank_ms * 0.3
                is_frozen  = (ae_frozen_frame > 0 and f == int(ae_frozen_frame))
                is_crc_fault = (ae_fault_frame > 0 and f == int(ae_fault_frame))
                id_repeat  = (f > 0 and frame_ids[f] == frame_ids[f-1])
                is_fail    = (is_crc_fault or id_repeat) and f >= 2
                compare_active = f >= 2
                fault_type = ("Frozen / repeated FRAME_ID" if id_repeat else
                              "CRC mismatch" if is_crc_fault else "—")
                sim_rows.append({
                    "Frame #": f,
                    "AE_SDP sent at (ms)": round(t_sdp, 2),
                    "FRAME_ID": frame_ids[f],
                    "Frozen Frame": "❄ Yes" if is_frozen else "No",
                    "Fault Type": fault_type,
                    "FUSA_COMPARE active": "Yes" if compare_active else "No (startup)",
                    "FuSa Result": ("❌ FAIL → Safe State" if is_fail else "✅ PASS") if compare_active else "—",
                })
            st.dataframe(pd.DataFrame(sim_rows), use_container_width=True, hide_index=True)

    # ── Tab 4 : Escalation State Machine ──────────────────────────────────────
    with dpae_sub4:
        st.markdown("### DP AE Escalation State Machine")
        st.caption("Source: VESA DP AE v1.0 Section 5 — Automotive Extension States")

        import plotly.graph_objects as go_ae

        # State boxes: (x, y, label, color)
        fig_sm, ax_sm = plt.subplots(figsize=(10, 9))
        fig_sm.patch.set_facecolor("white")
        ax_sm.set_facecolor("white")
        ax_sm.set_xlim(0, 10)
        ax_sm.set_ylim(0, 10)
        ax_sm.axis("off")
        ax_sm.set_title("DP AE Escalation State Machine", fontsize=15, fontweight="bold", pad=16)

        # State boxes: (cx, cy, title, subtitle, fill, text_color)
        sm_states = [
            (5.0, 9.0, "INIT",           "Link Training + DP AE Init",              "#64748b", "white"),
            (5.0, 7.2, "NORMAL",         "FuSa Active — AE_SDP running",            "#16a34a", "white"),
            (5.0, 5.4, "FAULT DETECTED", "CRC mismatch / Timeout / Frame drop",     "#f59e0b", "white"),
            (5.0, 3.6, "SAFE STATE",     "Display blanked or frozen last good frame","#dc2626", "white"),
            (5.0, 1.8, "RECOVERY",       "Re-init DP AE, re-verify link",           "#2563eb", "white"),
        ]
        BOX_W, BOX_H = 4.4, 0.72

        from matplotlib.patches import FancyBboxPatch
        for (cx, cy, title, sub, fc, tc) in sm_states:
            box = FancyBboxPatch((cx - BOX_W/2, cy - BOX_H/2), BOX_W, BOX_H,
                                 boxstyle="round,pad=0.08", facecolor=fc,
                                 edgecolor="white", linewidth=2, zorder=3)
            ax_sm.add_patch(box)
            ax_sm.text(cx, cy + 0.13, title, ha="center", va="center",
                       fontsize=13, fontweight="bold", color=tc, zorder=4)
            ax_sm.text(cx, cy - 0.16, sub, ha="center", va="center",
                       fontsize=10, color=tc, alpha=0.92, zorder=4)

        # Downward arrows between states
        arrowprops = dict(arrowstyle="-|>", lw=2.0, color="#334155")
        arrow_labels = [
            (5.0, 8.64, 5.0, 7.56, "Link training complete + AE_SDP started",    "#475569"),
            (5.0, 6.84, 5.0, 5.76, "CRC fail / timeout / frame drop detected",   "#92400e"),
            (5.0, 5.04, 5.0, 3.96, "Fault confirmed — escalate to Safe State",   "#991b1b"),
            (5.0, 3.24, 5.0, 2.16, "System reset / re-init requested",           "#1e40af"),
        ]
        for (x0, y0, x1, y1, lbl, lc) in arrow_labels:
            ax_sm.annotate("", xy=(x1, y1), xytext=(x0, y0),
                           arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#334155"),
                           zorder=2)
            ax_sm.text(5.0 + BOX_W/2 + 0.18, (y0+y1)/2, lbl,
                       fontsize=9.5, color=lc, va="center", ha="left",
                       bbox=dict(boxstyle="round,pad=0.2", facecolor="#f8fafc",
                                 edgecolor=lc, linewidth=0.8, alpha=0.9))

        # Recovery → Normal loop on left side
        loop_x = 5.0 - BOX_W/2 - 0.5
        ax_sm.annotate("", xy=(5.0 - BOX_W/2, 7.2), xytext=(loop_x, 7.2),
                       arrowprops=dict(arrowstyle="-|>", lw=2.0, color="#16a34a"), zorder=2)
        ax_sm.plot([loop_x, loop_x], [1.8, 7.2], color="#16a34a", lw=2.0, ls="--", zorder=2)
        ax_sm.plot([5.0 - BOX_W/2, loop_x], [1.8, 1.8], color="#16a34a", lw=2.0, ls="--", zorder=2)
        ax_sm.text(loop_x - 0.12, 4.5, "Recovery\n→ Normal\n(re-verified)",
                   fontsize=9.5, color="#16a34a", va="center", ha="right", fontweight="bold",
                   bbox=dict(boxstyle="round,pad=0.25", facecolor="#f0fdf4",
                             edgecolor="#16a34a", linewidth=0.9))

        fig_sm.tight_layout()
        st.pyplot(fig_sm)

        st.markdown("#### State Descriptions")
        state_rows = [
            {"State": "INIT",           "Color": "⬜ Gray",   "Trigger In": "System power-on",                      "Trigger Out": "Link training + AE init complete"},
            {"State": "NORMAL",         "Color": "🟩 Green",  "Trigger In": "AE_SDP running, FUSA_COMPARE=1",        "Trigger Out": "CRC mismatch / timeout / frame drop"},
            {"State": "FAULT DETECTED", "Color": "🟨 Amber",  "Trigger In": "First failure event detected",          "Trigger Out": "Confirmed fault → escalate to Safe State"},
            {"State": "SAFE STATE",     "Color": "🟥 Red",    "Trigger In": "Fault confirmed by AE Sink",            "Trigger Out": "System reset / recovery request"},
            {"State": "RECOVERY",       "Color": "🟦 Blue",   "Trigger In": "System re-init after Safe State exit",  "Trigger Out": "Re-verification complete → back to Normal"},
        ]
        st.dataframe(pd.DataFrame(state_rows), use_container_width=True, hide_index=True)

        st.markdown("#### Key DPCD Registers for Safe State Monitoring")
        dpcd_rows = [
            {"DPCD Address": "0xA00xx", "Field": "AE_VERSION_MAJOR / MINOR",         "Description": "DP AE version supported by Sink"},
            {"DPCD Address": "0xA00xx", "Field": "CAP_AE_PROFILE",                   "Description": "Maximum profile (0–3) supported by Sink"},
            {"DPCD Address": "0xA00xx", "Field": "AE_OPERATIONAL_PROFILE_CONFIG",    "Description": "Negotiated profile written by Source"},
            {"DPCD Address": "0xA00xx", "Field": "AE_FUNCTIONAL_STATE_STATUS",       "Description": "Current FuSa state reported by Sink"},
            {"DPCD Address": "0xA00xx", "Field": "ROI_EN / ROI_COUNT_SET",           "Description": "Enable and count of active Regions-of-Interest"},
            {"DPCD Address": "0xA00xx", "Field": "COMP_CRC_EN",                      "Description": "Enable CRC on compressed bytes (DSC)"},
            {"DPCD Address": "0xA00xx", "Field": "SLICE_COLUMNS_COUNT_SET",          "Description": "DSC slice column count (sets N in AE_SDP size)"},
        ]
        st.dataframe(pd.DataFrame(dpcd_rows), use_container_width=True, hide_index=True)
        st.caption("⚠️ Exact DPCD addresses are defined in VESA DP AE v1.0 Chapter 6. Shown as 0xA00xx for reference.")

    # ── Tab 5 : Frozen Frame Detection Demo ───────────────────────────────────
    with dpae_sub5:
        import io, hashlib
        from matplotlib.animation import FuncAnimation
        import imageio
        import matplotlib.patches as mpatches
        import matplotlib.gridspec as gridspec
        _np_ae = np

        st.markdown("### 🎬 Frozen Frame Detection Demo")
        st.markdown(
            "This demo simulates a **DP AE display link** with a moving video source. "
            "Enable **Frozen Frame** to freeze the pixel content mid-stream and watch "
            "the DP AE FuSa mechanism detect it via **FRAME_ID** and **CRC_PIXELS**."
        )

        fd1, fd2, fd3 = st.columns(3)
        fd_fps     = fd1.selectbox("FPS", [10, 15, 20, 30, 60], index=4, key="fd_fps")
        fd_total   = fd2.number_input("Total frames", min_value=8, max_value=600, value=300, step=10, key="fd_total")
        fd_content = fd3.selectbox("Video content", ["Rear View Camera", "Speedometer", "Bouncing Ball", "Rotating Gauge", "Counter"], key="fd_content")

        fe1, fe2 = st.columns([1, 3])
        fd_freeze_enable = fe1.toggle("❄ Enable Frozen Frame", value=True, key="fd_freeze_en")
        fd_freeze_at = fe2.slider(
            "Freeze at frame #", min_value=2, max_value=int(fd_total) - 1,
            value=min(10, int(fd_total) - 1), step=1,
            disabled=not fd_freeze_enable, key="fd_freeze"
        )

        if st.button("▶ Generate Demo GIF", key="fd_gen"):
            with st.spinner("Generating animated demo..."):

                N = int(fd_total)
                do_freeze = fd_freeze_enable
                freeze_at = int(fd_freeze_at) if do_freeze else 0

                # ── per-frame data (270×360 high-resolution, vectorized) ──────
                IH, IW = 540, 720   # height × width (720p quality)
                CY, CX = IH // 2, IW // 2
                _rows, _cols = _np_ae.mgrid[0:IH, 0:IW]  # pixel coordinate grids

                def _frame_pixels(t):
                    """Return an IH×IW RGB array for the simulated video content."""
                    img = _np_ae.zeros((IH, IW, 3), dtype=_np_ae.uint8)

                    if fd_content == "Bouncing Ball":
                        bg = _np_ae.array([20, 40, 80], dtype=_np_ae.uint8)
                        img[:] = bg
                        cx = int(IW * (0.5 + 0.45 * _np_ae.sin(t * 0.6)))
                        cy = int(IH * (0.5 + 0.37 * _np_ae.sin(t * 0.9 + 1.0)))
                        r_ball = IH // 8
                        mask = (_cols - cx)**2 + (_rows - cy)**2 < r_ball**2
                        # Shaded ball: bright centre to dark edge
                        dist = _np_ae.sqrt((_cols - cx)**2 + (_rows - cy)**2).clip(0, r_ball)
                        shade = (1.0 - dist / r_ball)
                        img[mask, 0] = (255 * shade[mask]).astype(_np_ae.uint8)
                        img[mask, 1] = (80  * shade[mask]).astype(_np_ae.uint8)
                        img[mask, 2] = (80  * shade[mask]).astype(_np_ae.uint8)
                        # Shadow
                        sx, sy, sr = cx, IH - 18, r_ball // 2
                        smask = (_cols - sx)**2 + (_rows - sy)**2 < sr**2
                        img[smask] = (img[smask] * 0.5).astype(_np_ae.uint8)

                    elif fd_content == "Rotating Gauge":
                        img[:] = [15, 30, 60]
                        angle = t * 0.4
                        r_g = int(IH * 0.38)
                        ex = int(CX + r_g * _np_ae.cos(angle))
                        ey = int(CY - r_g * _np_ae.sin(angle))
                        # Thick needle using linspace
                        ss = _np_ae.linspace(0, 1, IH * 3)
                        pxs = (CX + ss * (ex - CX)).astype(int).clip(0, IW-1)
                        pys = (CY + ss * (ey - CY)).astype(int).clip(0, IH-1)
                        for pxi, pyi in zip(pxs, pys):
                            img[max(0,pyi-2):pyi+3, max(0,pxi-2):pxi+3] = [80, 220, 120]
                        # Dial circle
                        ring = (_np_ae.abs(_np_ae.sqrt((_cols-CX)**2+(_rows-CY)**2) - r_g) < 5)
                        img[ring] = [60, 80, 100]
                        # Centre hub
                        hub = (_cols-CX)**2 + (_rows-CY)**2 < (IH//16)**2
                        img[hub] = [200, 200, 200]

                    elif fd_content == "Speedometer":
                        img[:] = [10, 10, 25]
                        cx_s, cy_s = int(IW * 0.5), int(IH * 0.58)
                        r_outer, r_inner = int(IH * 0.42), int(IH * 0.30)
                        r_tick_o, r_tick_i = int(IH * 0.41), int(IH * 0.36)
                        speed = (t * 8) % 260
                        # Arc: starts at -220° (left-bottom) sweeps 260° to -320° (right-bottom)
                        # In math coords: 220° = upper-left, going clockwise to -40°
                        ARC_START = 220.0   # degrees (math convention, CCW from +x)
                        ARC_SPAN  = 260.0

                        dr = _np_ae.sqrt((_cols - cx_s)**2 + (_rows - cy_s)**2)
                        # arctan2 gives CCW angle from +x axis in degrees
                        ang = _np_ae.degrees(_np_ae.arctan2(-(_rows - cy_s), _cols - cx_s))
                        ang = _np_ae.where(ang < 0, ang + 360, ang)

                        # Relative angle from ARC_START going clockwise (decreasing math angle)
                        rel = (ARC_START - ang) % 360

                        arc_mask = (dr >= r_inner) & (dr <= r_outer) & (rel <= ARC_SPAN)

                        # Background arc — dark grey
                        img[arc_mask] = [55, 55, 75]

                        # Colour arc up to current speed (green→yellow→red)
                        speed_rel = (speed / 260.0) * ARC_SPAN
                        active = arc_mask & (rel <= speed_rel)
                        ratio = (rel[active] / ARC_SPAN).clip(0, 1)
                        img[active, 0] = (ratio * 255).astype(_np_ae.uint8)
                        img[active, 1] = ((1 - ratio * 0.85) * 220).astype(_np_ae.uint8)
                        img[active, 2] = (50 * (1 - ratio)).astype(_np_ae.uint8)

                        # Tick marks every 20 km/h
                        for spd_tick in range(0, 261, 20):
                            tick_deg = ARC_START - (spd_tick / 260.0) * ARC_SPAN
                            tick_rad = _np_ae.radians(tick_deg)
                            for rr in _np_ae.linspace(r_tick_i, r_tick_o, 12):
                                px = int(cx_s + rr * _np_ae.cos(tick_rad))
                                py = int(cy_s - rr * _np_ae.sin(tick_rad))
                                if 0 <= px < IW and 0 <= py < IH:
                                    img[max(0,py-1):py+2, max(0,px-1):px+2] = [200, 200, 200]

                        # Needle
                        needle_deg = ARC_START - (speed / 260.0) * ARC_SPAN
                        n_rad = _np_ae.radians(needle_deg)
                        for rr in _np_ae.linspace(r_inner * 0.05, r_outer * 0.80, IH * 3):
                            px = int(cx_s + rr * _np_ae.cos(n_rad))
                            py = int(cy_s - rr * _np_ae.sin(n_rad))
                            if 0 <= px < IW and 0 <= py < IH:
                                img[max(0,py-2):py+3, max(0,px-2):px+3] = [255, 255, 255]

                        # Centre hub
                        hub = (_cols-cx_s)**2 + (_rows-cy_s)**2 < (IH//18)**2
                        img[hub] = [180, 180, 200]

                        # Speed bar at bottom
                        bar_y1, bar_y2 = IH - 35, IH - 20
                        bar_x1, bar_x2 = int(IW * 0.1), int(IW * 0.9)
                        bar_fill = int(bar_x1 + (speed / 260.0) * (bar_x2 - bar_x1))
                        img[bar_y1:bar_y2, bar_x1:bar_x2] = [40, 40, 60]
                        img[bar_y1:bar_y2, bar_x1:bar_fill] = [80, 200, 255]

                    elif fd_content == "Rear View Camera":
                        horizon_y = int(IH * 0.35)
                        # Sky gradient
                        sky_rows = _np_ae.arange(horizon_y)
                        sky_blue = (100 + sky_rows * 3).clip(0, 255).astype(_np_ae.uint8)
                        img[:horizon_y, :, 0] = 40
                        img[:horizon_y, :, 1] = 70
                        img[:horizon_y, :, 2] = sky_blue[:, None]

                        # Road surface gradient
                        road_rows = _np_ae.arange(horizon_y, IH)
                        grey_v = (55 + (road_rows - horizon_y) * 1.2).clip(0, 200).astype(_np_ae.uint8)
                        img[horizon_y:, :, 0] = grey_v[:, None]
                        img[horizon_y:, :, 1] = grey_v[:, None]
                        img[horizon_y:, :, 2] = (grey_v * 0.9).astype(_np_ae.uint8)[:, None]

                        # Perspective lane lines
                        for row in range(horizon_y, IH):
                            depth = (row - horizon_y) / float(IH - horizon_y)
                            lx = int(CX - depth * IW * 0.47)
                            rx = int(CX + depth * IW * 0.47)
                            lw = max(2, int(depth * 8))
                            img[row, max(0,lx-lw):lx+lw] = [255, 255, 255]
                            img[row, max(0,rx-lw):rx+lw] = [255, 255, 255]
                            dash_phase = int(t * 4) % 20
                            if (row + dash_phase) % 20 < 10:
                                img[row, max(0,CX-lw):CX+lw] = [255, 220, 0]

                        # Moving car ahead
                        car_y = int(horizon_y + 10 + ((t * 3) % (IH - horizon_y - 40)))
                        car_depth = (car_y - horizon_y) / float(IH - horizon_y)
                        car_w = max(12, int(car_depth * IW * 0.38))
                        car_h = max(8,  int(car_depth * IH * 0.22))
                        car_x = CX - car_w // 2
                        if car_y + car_h < IH - 5:
                            img[car_y:car_y+car_h, max(0,car_x):min(IW,car_x+car_w)] = [160, 30, 30]
                            tw = max(3, car_w // 6)
                            img[car_y:car_y+max(3,car_h//4), max(0,car_x):max(0,car_x)+tw] = [255, 60, 60]
                            img[car_y:car_y+max(3,car_h//4), min(IW-tw,car_x+car_w-tw):min(IW,car_x+car_w)] = [255, 60, 60]
                            # Windshield
                            ws = tw
                            img[car_y+max(3,car_h//4):car_y+car_h-2, max(0,car_x+ws):min(IW,car_x+car_w-ws)] = [100, 160, 200]

                        # Green guide lines
                        for row in range(int(IH * 0.6), IH - 5):
                            depth2 = (row - IH * 0.6) / (IH * 0.4)
                            gl = int(CX - depth2 * IW * 0.18)
                            gr = int(CX + depth2 * IW * 0.18)
                            lw2 = max(2, int(depth2 * 5))
                            img[row, max(0,gl-lw2):gl+lw2] = [0, 220, 80]
                            img[row, max(0,gr-lw2):gr+lw2] = [0, 220, 80]

                    else:  # Counter
                        img[:] = [20, 20, 50]
                        v = t % 256
                        bar_h_s = int(IH * 0.15)
                        bar_y_s = IH // 2 - bar_h_s // 2
                        bar_w_s = int(v / 255.0 * IW * 0.85)
                        img[bar_y_s:bar_y_s+bar_h_s, int(IW*0.07):int(IW*0.07)+bar_w_s] = [80, 180, 255]
                    return img

                # Pre-compute frames (freeze pixel content after freeze_at)
                frames_pixels = []
                for f in range(N):
                    eff_t = f if (not do_freeze or f < freeze_at) else freeze_at
                    frames_pixels.append(_frame_pixels(eff_t))

                # FRAME_ID always increments (source keeps sending)
                frame_ids_demo = list(range(N))

                # CRC_PIXELS: hash of pixel content
                def _crc(img): return int(hashlib.md5(img.tobytes()).hexdigest()[:8], 16)
                crcs = [_crc(p) for p in frames_pixels]

                # FuSa detection: compare current vs previous CRC_PIXELS + FRAME_ID
                fusa_status = []
                for f in range(N):
                    if f < 2:
                        fusa_status.append("startup")
                    else:
                        crc_ok = (crcs[f] != crcs[f-1])  # pixels must change
                        id_ok  = (frame_ids_demo[f] == frame_ids_demo[f-1] + 1)
                        if not crc_ok:
                            fusa_status.append("FROZEN")
                        elif not id_ok:
                            fusa_status.append("FAIL")
                        else:
                            fusa_status.append("OK")

                # ── build animation ──────────────────────────────────────────
                fig_anim = plt.figure(figsize=(16, 7.5), dpi=130, facecolor="#0f172a")
                gs = gridspec.GridSpec(2, 3, figure=fig_anim,
                                       left=0.03, right=0.98, top=0.90, bottom=0.08,
                                       wspace=0.30, hspace=0.45)

                ax_vid   = fig_anim.add_subplot(gs[:, 0])   # video panel (tall)
                ax_fid   = fig_anim.add_subplot(gs[0, 1])   # FRAME_ID bar
                ax_crc   = fig_anim.add_subplot(gs[0, 2])   # CRC_PIXELS bar
                ax_fusa  = fig_anim.add_subplot(gs[1, 1:])  # FuSa status (wide)

                for ax in [ax_vid, ax_fid, ax_crc, ax_fusa]:
                    ax.set_facecolor("#1e293b")
                    for s in ax.spines.values(): s.set_color("#334155")

                fig_anim.suptitle("DP AE — Frozen Frame Detection Demo",
                                  color="white", fontsize=13, fontweight="bold", y=0.97)

                # Static: video frame label
                ax_vid.set_title("Display Output", color="#94a3b8", fontsize=9, pad=4)
                ax_vid.axis("off")
                img_disp = ax_vid.imshow(frames_pixels[0], aspect="auto", interpolation="nearest")
                freeze_label = ax_vid.text(40, 4, "", color="#f59e0b", fontsize=10,
                                           fontweight="bold", ha="center",
                                           bbox=dict(facecolor="#1e293b", edgecolor="#f59e0b",
                                                     boxstyle="round,pad=0.3"))
                frame_label = ax_vid.text(40, 57, "Frame 0", color="white", fontsize=8,
                                          ha="center")

                # FRAME_ID bar chart
                ax_fid.set_title("FRAME_ID", color="#94a3b8", fontsize=9, pad=4)
                ax_fid.set_xlim(-0.5, 1.5)
                ax_fid.set_ylim(0, N + 1)
                ax_fid.tick_params(colors="#64748b")
                ax_fid.yaxis.label.set_color("#64748b")
                bar_fid = ax_fid.bar([0], [0], color="#3b82f6", width=0.6)
                txt_fid = ax_fid.text(0, 1, "0", color="white", ha="center",
                                      va="bottom", fontsize=11, fontweight="bold")
                ax_fid.set_xticks([])

                # CRC_PIXELS bar chart
                ax_crc.set_title("CRC_PIXELS (low 16-bit)", color="#94a3b8", fontsize=9, pad=4)
                ax_crc.set_xlim(-0.5, 1.5)
                ax_crc.set_ylim(0, 0xFFFF + 0x1000)
                ax_crc.tick_params(colors="#64748b")
                bar_crc = ax_crc.bar([0], [crcs[0] & 0xFFFF], color="#6366f1", width=0.6)
                txt_crc = ax_crc.text(0, crcs[0] & 0xFFFF, f"0x{crcs[0]&0xFFFF:04X}",
                                      color="white", ha="center", va="bottom",
                                      fontsize=9, fontweight="bold")
                ax_crc.set_xticks([])

                # FuSa status timeline
                ax_fusa.set_title("FuSa Detection Status", color="#94a3b8", fontsize=9, pad=4)
                ax_fusa.set_xlim(-0.5, N - 0.5)
                ax_fusa.set_ylim(-0.5, 1.5)
                ax_fusa.set_yticks([0, 1])
                ax_fusa.set_yticklabels(["FAIL/FROZEN", "OK"], color="#94a3b8", fontsize=8)
                ax_fusa.tick_params(colors="#64748b")
                ax_fusa.set_xlabel("Frame #", color="#64748b", fontsize=8)
                fusa_dots = []
                fusa_txt  = ax_fusa.text(N/2, -0.4, "", color="#f59e0b",
                                         ha="center", fontsize=10, fontweight="bold")

                STATUS_COLOR = {"OK": "#16a34a", "FAIL": "#dc2626",
                                "FROZEN": "#f59e0b", "startup": "#475569"}

                def _update(f):
                    # Video display
                    img_disp.set_data(frames_pixels[f])
                    frame_label.set_text(f"Frame {f}")
                    is_frozen_frame = do_freeze and f >= freeze_at
                    freeze_label.set_text("❄ FROZEN" if is_frozen_frame else "")

                    # FRAME_ID
                    fid = frame_ids_demo[f]
                    bar_fid[0].set_height(fid + 1)
                    txt_fid.set_text(str(fid))
                    txt_fid.set_position((0, fid + 1.1))

                    # CRC bar — highlight if same as previous
                    crc_val = crcs[f] & 0xFFFF
                    crc_changed = (f == 0 or crcs[f] != crcs[f-1])
                    bar_crc[0].set_height(crc_val)
                    bar_crc[0].set_color("#f59e0b" if not crc_changed and f > 0 else "#6366f1")
                    txt_crc.set_text(f"0x{crc_val:04X}")
                    txt_crc.set_position((0, crc_val + 500))
                    txt_crc.set_color("#f59e0b" if not crc_changed and f > 0 else "white")

                    # FuSa dots
                    for dot in fusa_dots: dot.remove()
                    fusa_dots.clear()
                    for i in range(f + 1):
                        st_i = fusa_status[i]
                        col = STATUS_COLOR[st_i]
                        y_i = 1 if st_i == "OK" else (0.5 if st_i == "startup" else 0)
                        mk  = "o" if st_i in ("OK", "startup") else "X"
                        dot, = ax_fusa.plot(i, y_i, mk, color=col,
                                            markersize=10, markeredgecolor="white",
                                            markeredgewidth=0.8, zorder=3)
                        fusa_dots.append(dot)

                    st_f = fusa_status[f]
                    if st_f in ("FROZEN", "FAIL"):
                        fusa_txt.set_text(f"⚠ {st_f} detected at Frame {f} → Safe State!")
                        fusa_txt.set_color(STATUS_COLOR[st_f])
                    elif st_f == "startup":
                        fusa_txt.set_text("FuSa compare inactive (startup period)")
                        fusa_txt.set_color("#475569")
                    else:
                        fusa_txt.set_text("")

                    return [img_disp, bar_fid[0], bar_crc[0], txt_fid, txt_crc,
                            freeze_label, frame_label, fusa_txt] + fusa_dots

                import tempfile, os
                # Render frames and encode as MP4 via imageio-ffmpeg
                frames_mp4 = []
                for fi in range(N):
                    _update(fi)
                    fig_anim.canvas.draw()
                    buf = fig_anim.canvas.buffer_rgba()
                    frame_arr = _np_ae.frombuffer(buf, dtype=_np_ae.uint8).copy()
                    frame_arr = frame_arr.reshape(fig_anim.canvas.get_width_height()[::-1] + (4,))
                    frames_mp4.append(frame_arr[:, :, :3])
                plt.close(fig_anim)
                tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                tmp.close()
                with imageio.get_writer(tmp.name, format="FFMPEG", fps=fd_fps,
                                        codec="libx264", pixelformat="yuv420p",
                                        output_params=["-r", str(fd_fps)]) as _w:
                    for _fr in frames_mp4: _w.append_data(_fr)
                with open(tmp.name, "rb") as _f:
                    video_bytes = _f.read()
                os.unlink(tmp.name)

            caption_txt = (f"{fd_content} | {N} frames @ {fd_fps} fps"
                           + (f" | ❄ Frozen at frame {freeze_at}" if do_freeze else " | No freeze"))
            st.video(video_bytes, format="video/mp4")
            st.caption(caption_txt)

            st.markdown("#### How DP AE Detects a Frozen Frame")
            detect_rows = [
                {"Mechanism": "FRAME_ID monotonic counter",
                 "Normal":    "Increments by 1 every frame",
                 "Frozen":    "Repeats same value → Sink detects repeated ID"},
                {"Mechanism": "CRC_PIXELS",
                 "Normal":    "Changes every frame (new pixel content)",
                 "Frozen":    "Same CRC two frames in a row → pixel buffer unchanged"},
                {"Mechanism": "FuSa Timeout",
                 "Normal":    "AE_SDP arrives every Vblank",
                 "Frozen":    "If AE_SDP stops → timeout fault (link failure)"},
                {"Mechanism": "Action on detection",
                 "Normal":    "—",
                 "Frozen":    "Sink escalates to Safe State, blanks or holds display"},
            ]
            st.dataframe(pd.DataFrame(detect_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Configure parameters above and click **▶ Generate Demo GIF** to run the simulation.")

        st.markdown("---")
        st.markdown("### 🆚 Side-by-Side Comparison: Normal vs Frozen")
        st.caption("Generates one animated GIF with both conditions rendered in parallel for direct comparison.")

        if st.button("▶ Generate Side-by-Side Comparison GIF", key="fd_sbs"):
            with st.spinner("Generating side-by-side comparison..."):
                import tempfile as _tmp_sbs, os as _os_sbs
                from matplotlib.animation import FuncAnimation as _FuncAnim
                import imageio as _imageio
                import matplotlib.gridspec as _gs_sbs

                N_sbs   = int(fd_total)
                fz_at   = int(fd_freeze_at) if fd_freeze_enable else N_sbs  # no freeze = never

                IH_s, IW_s = 540, 720
                CY_s, CX_s = IH_s // 2, IW_s // 2
                _rows_s, _cols_s = _np_ae.mgrid[0:IH_s, 0:IW_s]

                def _fpx_sbs(t):
                    """Same pixel generator as main demo."""
                    img = _np_ae.zeros((IH_s, IW_s, 3), dtype=_np_ae.uint8)
                    if fd_content == "Rear View Camera":
                        horizon_y = int(IH_s * 0.35)
                        sky_rows = _np_ae.arange(horizon_y)
                        sky_blue = (100 + sky_rows * 3).clip(0, 255).astype(_np_ae.uint8)
                        img[:horizon_y, :, 0] = 40
                        img[:horizon_y, :, 1] = 70
                        img[:horizon_y, :, 2] = sky_blue[:, None]
                        road_rows = _np_ae.arange(horizon_y, IH_s)
                        grey_v = (55 + (road_rows - horizon_y) * 1.2).clip(0, 200).astype(_np_ae.uint8)
                        img[horizon_y:, :, 0] = grey_v[:, None]
                        img[horizon_y:, :, 1] = grey_v[:, None]
                        img[horizon_y:, :, 2] = (grey_v * 0.9).astype(_np_ae.uint8)[:, None]
                        for row in range(horizon_y, IH_s):
                            depth = (row - horizon_y) / float(IH_s - horizon_y)
                            lx = int(CX_s - depth * IW_s * 0.47)
                            rx = int(CX_s + depth * IW_s * 0.47)
                            lw = max(2, int(depth * 8))
                            img[row, max(0,lx-lw):lx+lw] = [255, 255, 255]
                            img[row, max(0,rx-lw):rx+lw] = [255, 255, 255]
                            dash_phase = int(t * 4) % 20
                            if (row + dash_phase) % 20 < 10:
                                img[row, max(0,CX_s-lw):CX_s+lw] = [255, 220, 0]
                        car_y = int(horizon_y + 10 + ((t * 3) % (IH_s - horizon_y - 40)))
                        car_depth = (car_y - horizon_y) / float(IH_s - horizon_y)
                        car_w = max(12, int(car_depth * IW_s * 0.38))
                        car_h = max(8,  int(car_depth * IH_s * 0.22))
                        car_x = CX_s - car_w // 2
                        if car_y + car_h < IH_s - 5:
                            img[car_y:car_y+car_h, max(0,car_x):min(IW_s,car_x+car_w)] = [160, 30, 30]
                            tw = max(3, car_w // 6)
                            img[car_y:car_y+max(3,car_h//4), max(0,car_x):max(0,car_x)+tw] = [255, 60, 60]
                            img[car_y:car_y+max(3,car_h//4), min(IW_s-tw,car_x+car_w-tw):min(IW_s,car_x+car_w)] = [255, 60, 60]
                            ws = tw
                            img[car_y+max(3,car_h//4):car_y+car_h-2, max(0,car_x+ws):min(IW_s,car_x+car_w-ws)] = [100, 160, 200]
                        for row in range(int(IH_s*0.6), IH_s-5):
                            depth2 = (row - IH_s*0.6) / (IH_s*0.4)
                            gl = int(CX_s - depth2 * IW_s * 0.18)
                            gr = int(CX_s + depth2 * IW_s * 0.18)
                            lw2 = max(2, int(depth2 * 5))
                            img[row, max(0,gl-lw2):gl+lw2] = [0, 220, 80]
                            img[row, max(0,gr-lw2):gr+lw2] = [0, 220, 80]
                    elif fd_content == "Speedometer":
                        img[:] = [10, 10, 25]
                        cx_s2, cy_s2 = int(IW_s*0.5), int(IH_s*0.58)
                        r_outer2, r_inner2 = int(IH_s*0.42), int(IH_s*0.30)
                        r_tick_o2, r_tick_i2 = int(IH_s*0.41), int(IH_s*0.36)
                        speed2 = (t * 8) % 260
                        ARC_START2, ARC_SPAN2 = 220.0, 260.0
                        needle_deg2 = ARC_START2 - (speed2/260.0)*ARC_SPAN2
                        dr2 = _np_ae.sqrt((_cols_s-cx_s2)**2+(_rows_s-cy_s2)**2)
                        ang2 = _np_ae.degrees(_np_ae.arctan2(-(_rows_s-cy_s2), _cols_s-cx_s2))
                        ang2 = _np_ae.where(ang2<0, ang2+360, ang2)
                        rel2 = (ARC_START2-ang2)%360
                        arc2 = (dr2>=r_inner2)&(dr2<=r_outer2)&(rel2<=ARC_SPAN2)
                        img[arc2] = [55,55,75]
                        sp2 = (speed2/260.0)*ARC_SPAN2
                        act2 = arc2&(rel2<=sp2)
                        rat2 = (rel2[act2]/ARC_SPAN2).clip(0,1)
                        img[act2,0]=(rat2*255).astype(_np_ae.uint8)
                        img[act2,1]=((1-rat2*0.85)*220).astype(_np_ae.uint8)
                        img[act2,2]=(50*(1-rat2)).astype(_np_ae.uint8)
                        for st2 in range(0,261,20):
                            td2=ARC_START2-(st2/260.0)*ARC_SPAN2
                            tr2=_np_ae.radians(td2)
                            for rr2 in _np_ae.linspace(r_tick_i2,r_tick_o2,12):
                                px2=int(cx_s2+rr2*_np_ae.cos(tr2)); py2=int(cy_s2-rr2*_np_ae.sin(tr2))
                                if 0<=px2<IW_s and 0<=py2<IH_s:
                                    img[max(0,py2-1):py2+2,max(0,px2-1):px2+2]=[200,200,200]
                        n_rad2=_np_ae.radians(needle_deg2)
                        for rr2 in _np_ae.linspace(r_inner2*0.05,r_outer2*0.80,IH_s*3):
                            px2=int(cx_s2+rr2*_np_ae.cos(n_rad2)); py2=int(cy_s2-rr2*_np_ae.sin(n_rad2))
                            if 0<=px2<IW_s and 0<=py2<IH_s:
                                img[max(0,py2-2):py2+3,max(0,px2-2):px2+3]=[255,255,255]
                        hub2=(_cols_s-cx_s2)**2+(_rows_s-cy_s2)**2<(IH_s//18)**2
                        img[hub2]=[180,180,200]
                        _bx1=int(IW_s*0.1); _bx2=int(IW_s*0.9)
                        img[IH_s-35:IH_s-20,_bx1:_bx2]=[40,40,60]
                        img[IH_s-35:IH_s-20,_bx1:_bx1+int(speed2/260.0*(_bx2-_bx1))]=[80,200,255]
                    else:
                        img[:] = [20, 20, 50]
                        v = t % 256
                        img[IH_s//2-20:IH_s//2+20, int(IW_s*0.07):int(IW_s*0.07+v/255.0*IW_s*0.85)] = [80,180,255]
                    return img

                # Pre-compute frames for both sides
                frames_normal = [_fpx_sbs(f) for f in range(N_sbs)]
                frames_frozen = [_fpx_sbs(f if f < fz_at else fz_at) for f in range(N_sbs)]

                def _crc_sbs(img): return int(hashlib.md5(img.tobytes()).hexdigest()[:8], 16)
                crcs_n = [_crc_sbs(p) for p in frames_normal]
                crcs_f = [_crc_sbs(p) for p in frames_frozen]

                def _fusa(crcs_list):
                    out = []
                    for f in range(N_sbs):
                        if f < 2: out.append("startup")
                        elif crcs_list[f] == crcs_list[f-1]: out.append("FROZEN")
                        else: out.append("OK")
                    return out

                fusa_n = _fusa(crcs_n)
                fusa_f = _fusa(crcs_f)
                SC = {"OK":"#16a34a","FROZEN":"#f59e0b","FAIL":"#dc2626","startup":"#475569"}

                # ── Build side-by-side figure ────────────────────────────────
                fig_sbs = plt.figure(figsize=(20, 9), dpi=110, facecolor="#0f172a")
                gs_sbs = _gs_sbs.GridSpec(3, 4, figure=fig_sbs,
                                          left=0.03, right=0.97, top=0.91, bottom=0.07,
                                          wspace=0.28, hspace=0.55)

                # Video panels (tall, spanning 2 rows)
                ax_vn = fig_sbs.add_subplot(gs_sbs[:2, 0])   # normal video
                ax_vf = fig_sbs.add_subplot(gs_sbs[:2, 2])   # frozen video

                # Metrics: FRAME_ID + CRC side by side per column
                ax_fn  = fig_sbs.add_subplot(gs_sbs[0, 1])   # normal FRAME_ID
                ax_cn  = fig_sbs.add_subplot(gs_sbs[1, 1])   # normal CRC
                ax_ff  = fig_sbs.add_subplot(gs_sbs[0, 3])   # frozen FRAME_ID
                ax_cf  = fig_sbs.add_subplot(gs_sbs[1, 3])   # frozen CRC

                # FuSa status (full width bottom row)
                ax_fusa_n = fig_sbs.add_subplot(gs_sbs[2, :2])
                ax_fusa_f = fig_sbs.add_subplot(gs_sbs[2, 2:])

                for ax in [ax_vn, ax_vf, ax_fn, ax_cn, ax_ff, ax_cf, ax_fusa_n, ax_fusa_f]:
                    ax.set_facecolor("#1e293b")
                    for s in ax.spines.values(): s.set_color("#334155")

                # Titles
                fig_sbs.suptitle("DP AE — Frozen Frame Detection: Normal vs Frozen Comparison",
                                  color="white", fontsize=14, fontweight="bold", y=0.97)
                ax_vn.set_title("▶ NORMAL — No Freeze",      color="#4ade80", fontsize=11, fontweight="bold", pad=5)
                ax_vf.set_title("❄ FROZEN — Freeze Enabled", color="#fb923c", fontsize=11, fontweight="bold", pad=5)
                for ax in [ax_vn, ax_vf]: ax.axis("off")

                # Video images
                im_n = ax_vn.imshow(frames_normal[0], aspect="auto", interpolation="bilinear")
                im_f = ax_vf.imshow(frames_frozen[0], aspect="auto", interpolation="bilinear")
                lbl_n = ax_vn.text(IW_s//2, IH_s-25, "Frame 0", color="white", ha="center", fontsize=10, fontweight="bold")
                lbl_f = ax_vf.text(IW_s//2, IH_s-25, "Frame 0", color="white", ha="center", fontsize=10, fontweight="bold")
                freeze_badge = ax_vf.text(IW_s//2, 30, "", color="#fb923c", ha="center", fontsize=13,
                                          fontweight="bold",
                                          bbox=dict(facecolor="#1e293b", edgecolor="#fb923c",
                                                    boxstyle="round,pad=0.3", alpha=0.9))

                # FRAME_ID bars
                for ax, lbl in [(ax_fn, "FRAME_ID (Normal)"), (ax_ff, "FRAME_ID (Frozen)")]:
                    ax.set_title(lbl, color="#94a3b8", fontsize=9, pad=3)
                    ax.set_xlim(-0.5, 1.5); ax.set_ylim(0, N_sbs+1)
                    ax.set_xticks([]); ax.tick_params(colors="#64748b")
                bar_fn = ax_fn.bar([0],[0], color="#3b82f6", width=0.6)
                bar_ff = ax_ff.bar([0],[0], color="#3b82f6", width=0.6)
                txt_fn = ax_fn.text(0, 0.5, "0", color="white", ha="center", va="bottom", fontsize=12, fontweight="bold")
                txt_ff = ax_ff.text(0, 0.5, "0", color="white", ha="center", va="bottom", fontsize=12, fontweight="bold")

                # CRC bars
                max_crc = max(max(c & 0xFFFF for c in crcs_n), max(c & 0xFFFF for c in crcs_f), 1)
                for ax, lbl in [(ax_cn, "CRC_PIXELS (Normal)"), (ax_cf, "CRC_PIXELS (Frozen)")]:
                    ax.set_title(lbl, color="#94a3b8", fontsize=9, pad=3)
                    ax.set_xlim(-0.5, 1.5); ax.set_ylim(0, max_crc * 1.25)
                    ax.set_xticks([]); ax.tick_params(colors="#64748b")
                bar_cn = ax_cn.bar([0],[crcs_n[0]&0xFFFF], color="#6366f1", width=0.6)
                bar_cf = ax_cf.bar([0],[crcs_f[0]&0xFFFF], color="#6366f1", width=0.6)
                txt_cn = ax_cn.text(0, crcs_n[0]&0xFFFF, f"0x{crcs_n[0]&0xFFFF:04X}", color="white", ha="center", va="bottom", fontsize=9, fontweight="bold")
                txt_cf = ax_cf.text(0, crcs_f[0]&0xFFFF, f"0x{crcs_f[0]&0xFFFF:04X}", color="white", ha="center", va="bottom", fontsize=9, fontweight="bold")

                # FuSa timelines
                for ax, lbl in [(ax_fusa_n, "FuSa Status — Normal"), (ax_fusa_f, "FuSa Status — Frozen")]:
                    ax.set_title(lbl, color="#94a3b8", fontsize=9, pad=3)
                    ax.set_xlim(-0.5, N_sbs-0.5); ax.set_ylim(-0.6, 1.5)
                    ax.set_yticks([0,1]); ax.set_yticklabels(["FAIL/FROZEN","OK"], color="#94a3b8", fontsize=8)
                    ax.set_xlabel("Frame #", color="#64748b", fontsize=8)
                    ax.tick_params(colors="#64748b")
                fusa_dots_n, fusa_dots_f = [], []
                alert_n = ax_fusa_n.text(N_sbs/2, -0.45, "", color="white", ha="center", fontsize=9, fontweight="bold")
                alert_f = ax_fusa_f.text(N_sbs/2, -0.45, "", color="white", ha="center", fontsize=9, fontweight="bold")

                def _update_sbs(f):
                    # Normal side video
                    im_n.set_data(frames_normal[f])
                    lbl_n.set_text(f"Frame {f}")

                    # Frozen side video
                    im_f.set_data(frames_frozen[f])
                    lbl_f.set_text(f"Frame {f}")
                    is_fz = fd_freeze_enable and f >= fz_at
                    freeze_badge.set_text("❄ FROZEN" if is_fz else "")

                    # FRAME_ID bars (both sides same — source always increments)
                    for bar, txt, ax in [(bar_fn, txt_fn, ax_fn), (bar_ff, txt_ff, ax_ff)]:
                        bar[0].set_height(f + 1)
                        txt.set_text(str(f)); txt.set_position((0, f + 1.2))

                    # CRC bars
                    crc_n_val = crcs_n[f] & 0xFFFF
                    crc_f_val = crcs_f[f] & 0xFFFF
                    crc_n_changed = (f == 0 or crcs_n[f] != crcs_n[f-1])
                    crc_f_changed = (f == 0 or crcs_f[f] != crcs_f[f-1])

                    bar_cn[0].set_height(crc_n_val)
                    bar_cn[0].set_color("#6366f1")
                    txt_cn.set_text(f"0x{crc_n_val:04X}"); txt_cn.set_position((0, crc_n_val + max_crc*0.03))

                    bar_cf[0].set_height(crc_f_val)
                    bar_cf[0].set_color("#f59e0b" if not crc_f_changed and f > 0 else "#6366f1")
                    txt_cf.set_text(f"0x{crc_f_val:04X}"); txt_cf.set_position((0, crc_f_val + max_crc*0.03))
                    txt_cf.set_color("#f59e0b" if not crc_f_changed and f > 0 else "white")

                    # FuSa dots
                    for dots in [fusa_dots_n, fusa_dots_f]:
                        for d in dots: d.remove()
                    fusa_dots_n.clear(); fusa_dots_f.clear()

                    for i in range(f+1):
                        for dots_list, fusa_list, ax_f in [
                            (fusa_dots_n, fusa_n, ax_fusa_n),
                            (fusa_dots_f, fusa_f, ax_fusa_f)
                        ]:
                            st_i = fusa_list[i]
                            col = SC[st_i]
                            y_i = 1 if st_i=="OK" else (0.5 if st_i=="startup" else 0)
                            mk  = "o" if st_i in ("OK","startup") else "X"
                            dot, = ax_f.plot(i, y_i, mk, color=col, markersize=9,
                                             markeredgecolor="white", markeredgewidth=0.8, zorder=3)
                            dots_list.append(dot)

                    st_n = fusa_n[f]; st_f2 = fusa_f[f]
                    alert_n.set_text(f"⚠ {st_n} @ Frame {f} → Safe State!" if st_n in ("FROZEN","FAIL") else
                                     ("Startup — compare inactive" if st_n=="startup" else ""))
                    alert_n.set_color(SC[st_n])
                    alert_f.set_text(f"⚠ {st_f2} @ Frame {f} → Safe State!" if st_f2 in ("FROZEN","FAIL") else
                                     ("Startup — compare inactive" if st_f2=="startup" else ""))
                    alert_f.set_color(SC[st_f2])

                    return ([im_n, im_f, lbl_n, lbl_f, freeze_badge,
                             bar_fn[0], bar_ff[0], bar_cn[0], bar_cf[0],
                             txt_fn, txt_ff, txt_cn, txt_cf,
                             alert_n, alert_f] + fusa_dots_n + fusa_dots_f)

                # Render frames and encode as MP4
                sbs_frames = []
                for fi in range(N_sbs):
                    _update_sbs(fi)
                    fig_sbs.canvas.draw()
                    buf2 = fig_sbs.canvas.buffer_rgba()
                    fa2 = _np_ae.frombuffer(buf2, dtype=_np_ae.uint8).copy()
                    fa2 = fa2.reshape(fig_sbs.canvas.get_width_height()[::-1] + (4,))
                    sbs_frames.append(fa2[:, :, :3])
                plt.close(fig_sbs)
                tmp2 = _tmp_sbs.NamedTemporaryFile(suffix=".mp4", delete=False)
                tmp2.close()
                with _imageio.get_writer(tmp2.name, format="FFMPEG", fps=fd_fps,
                                         codec="libx264", pixelformat="yuv420p",
                                         output_params=["-r", str(fd_fps)]) as _w2:
                    for _fr2 in sbs_frames: _w2.append_data(_fr2)
                with open(tmp2.name, "rb") as _fh: sbs_bytes = _fh.read()
                _os_sbs.unlink(tmp2.name)

            st.video(sbs_bytes, format="video/mp4")
            st.caption(f"Side-by-side | {fd_content} | {N_sbs} frames @ {fd_fps} fps | "
                       f"Freeze at frame {fz_at if fd_freeze_enable else 'N/A (disabled)'}")

# ══════════════════════════════════════════════════════════════════════════
# TAB 10 – GMSL3 vs. eDP
# ══════════════════════════════════════════════════════════════════════════
with tab_gmsl3:
    st.markdown("## 🔗 GMSL3 (Input) vs. eDP HBR3 (Output) — Capacity Matrix")
    st.markdown(
        "Models an automotive serializer/bridge pipeline: video enters on **GMSL3**, "
        "either **DSC-compressed** (3:1 @24bpp or 3.75:1 @30bpp) or **decompressed (raw)**, "
        "and the bridge outputs fully decompressed/raw pixel data to the **eDP** port running at "
        "**HBR3 (8.1 Gbps/lane)** — eDP has no DSC of its own. The matrix sweeps GMSL3 link count "
        "and GMSL3 compression mode (frame rate and blanking ratio are selected below) to find the "
        "**maximum video payload, max PCLK, and max active pixels** the pipeline supports."
    )

    GMSL3_LINK_GBPS = 9.7      # raw payload per GMSL3 link, Gbps
    EDP_HBR3_GBPS   = 8.1      # eDP HBR3 link rate per lane, Gbps

    g1, g2, g3, g4 = st.columns(4)
    g_edp_lanes = g1.selectbox("eDP Lane Count (per port)", [1, 2, 4], index=2, key="g3_edp_lanes")
    g_fps       = g2.selectbox("Frame Rate (fps)", [60, 90], index=0, key="g3_fps")
    g_blank_pct = g3.selectbox("Total Blanking Ratio", ["5%", "10%"], index=0, key="g3_blank")
    g_show_bottleneck = g4.checkbox("Highlight bottleneck", value=True, key="g3_hl")
    g_blank = int(g_blank_pct.rstrip("%")) / 100.0

    # GMSL3 input compression modes: (label, nominal bpp, DSC ratio) — passed through unchanged to eDP
    GMSL3_MODES = [
        ("DSC compressed 24bpp (3:1)",    24, 3.0),
        ("DSC compressed 30bpp (3.75:1)", 30, 3.75),
        ("No compression",                24, 1.0),
    ]
    GMSL3_LINKS_OPTS = [1, 2]
    EDP_PORTS_OPTS   = [1, 2]

    # eDP has no DSC of its own — each port always carries the decompressed/raw bitstream at
    # its fixed HBR3 wire rate, regardless of how GMSL3 was compressed.
    edp_port_cap_gbps = g_edp_lanes * EDP_HBR3_GBPS * EDP_ENCODING

    rows = []
    for links in GMSL3_LINKS_OPTS:
        gmsl3_wire_gbps = links * GMSL3_LINK_GBPS                # physical GMSL3 link bit budget, Gbps
        for mode_lbl, nominal_bpp, dsc_ratio in GMSL3_MODES:
            # GMSL3 effective video capacity: a compressed wire carries dsc_ratio× more
            # equivalent raw video than its physical bit budget (1.0 for Decompressed).
            gmsl3_cap_gbps = gmsl3_wire_gbps * dsc_ratio
            for ports in EDP_PORTS_OPTS:
                edp_cap_gbps = ports * edp_port_cap_gbps
                bottleneck = "GMSL3" if gmsl3_cap_gbps < edp_cap_gbps else \
                             ("eDP" if edp_cap_gbps < gmsl3_cap_gbps else "Tied")
                max_payload_gbps = min(gmsl3_cap_gbps, edp_cap_gbps)
                max_pclk_mhz  = max_payload_gbps * 1e9 / nominal_bpp / 1e6
                max_pixels_mp = (max_pclk_mhz * 1e6) / g_fps / (1.0 + g_blank) / 1e6

                rows.append({
                    "GMSL3 Links":        f"{links} link{'s' if links > 1 else ''}",
                    "eDP Ports":          f"{ports} port{'s' if ports > 1 else ''}",
                    "GMSL3 Compression Mode": mode_lbl,
                    "GMSL3 Capacity (Gbps)": round(gmsl3_cap_gbps, 2),
                    "eDP Capacity (Gbps)": round(edp_cap_gbps, 2),
                    "Frame Rate (fps)":   g_fps,
                    "Blanking Ratio":     g_blank_pct,
                    "Bottleneck":         bottleneck,
                    "Max Video Payload (Gbps)": round(max_payload_gbps, 2),
                    "Max PCLK (MHz)":     round(max_pclk_mhz, 2),
                    "Max Active Pixels (MP)": round(max_pixels_mp, 2),
                })

    # Pass-through scenario: the deserializer does NOT decompress — it relays the same
    # DSC-compressed bitstream straight out the eDP port (a fixed-bandwidth physical link,
    # 25.92 Gbps for 4-lane HBR3), and a downstream TCON or bridge IC does the actual DSC
    # decode. Neither GMSL3's nor eDP's wire capacity is multiplied by the DSC ratio — both
    # are physical bit budgets (9.7/19.4 Gbps for GMSL3, lanes×8.1×0.8 per eDP port). The DSC
    # ratio instead reduces the effective bits/pixel that must cross the bottleneck link.
    PT_MODES = [
        ("DSC pass-through 24bpp (3:1)",    24, 3.0),
        ("DSC pass-through 30bpp (3.75:1)", 30, 3.75),
    ]
    rows_pt = []
    for links in GMSL3_LINKS_OPTS:
        gmsl3_wire_gbps = links * GMSL3_LINK_GBPS
        for mode_lbl, nominal_bpp, dsc_ratio in PT_MODES:
            eff_bpp = nominal_bpp / dsc_ratio   # compressed bits actually carried per pixel
            for ports in EDP_PORTS_OPTS:
                edp_wire_gbps = ports * edp_port_cap_gbps
                bottleneck = "GMSL3" if gmsl3_wire_gbps < edp_wire_gbps else \
                             ("eDP" if edp_wire_gbps < gmsl3_wire_gbps else "Tied")
                bottleneck_wire_gbps = min(gmsl3_wire_gbps, edp_wire_gbps)
                max_pclk_mhz  = bottleneck_wire_gbps * 1e9 / eff_bpp / 1e6
                max_pixels_mp = (max_pclk_mhz * 1e6) / g_fps / (1.0 + g_blank) / 1e6
                # Post-decode (by the downstream TCON/bridge IC) raw video payload —
                # the compressed wire rate scaled back up by the DSC ratio.
                max_payload_gbps = bottleneck_wire_gbps * dsc_ratio

                rows_pt.append({
                    "GMSL3 Links":        f"{links} link{'s' if links > 1 else ''}",
                    "eDP Ports":          f"{ports} port{'s' if ports > 1 else ''}",
                    "GMSL3 Compression Mode": mode_lbl,
                    "GMSL3 Capacity (Gbps)": round(gmsl3_wire_gbps, 2),
                    "eDP Capacity (Gbps)": round(edp_wire_gbps, 2),
                    "Frame Rate (fps)":   g_fps,
                    "Blanking Ratio":     g_blank_pct,
                    "Bottleneck":         bottleneck,
                    "Max Video Payload (Gbps)": round(max_payload_gbps, 2),
                    "Max PCLK (MHz)":     round(max_pclk_mhz, 2),
                    "Max Active Pixels (MP)": round(max_pixels_mp, 2),
                })

    gmsl3_df = pd.DataFrame(rows)
    df_dsc  = gmsl3_df[gmsl3_df["GMSL3 Compression Mode"].str.startswith("DSC")].reset_index(drop=True)
    df_raw  = gmsl3_df[gmsl3_df["GMSL3 Compression Mode"].str.startswith("No compression")].reset_index(drop=True)
    df_pt   = pd.DataFrame(rows_pt)

    st.markdown(
        f"**eDP HBR3 capacity per port (fixed, no DSC):** {g_edp_lanes} lane{'s' if g_edp_lanes>1 else ''} "
        f"× {EDP_HBR3_GBPS} Gbps × {EDP_ENCODING:.0%} (8b/10b) = **{edp_port_cap_gbps:.2f} Gbps/port** "
        f"→ 2 ports = **{2*edp_port_cap_gbps:.2f} Gbps**. eDP always carries decompressed/raw video, "
        f"so per-port capacity does not change with GMSL3's compression mode.  |  "
        f"**GMSL3 wire bit budget:** 1 link = {GMSL3_LINK_GBPS} Gbps, 2 links = {2*GMSL3_LINK_GBPS} Gbps "
        f"— *GMSL3 Capacity below = wire budget × DSC ratio.*"
    )

    _NUM_FMT_COLS = {"GMSL3 Capacity (Gbps)", "eDP Capacity (Gbps)",
                      "Max Video Payload (Gbps)", "Max PCLK (MHz)", "Max Active Pixels (MP)"}
    _BN_BG = {"GMSL3": "#ccfbf1", "eDP": "#dbeafe", "Tied": "#fef3c7"}
    _BN_LEGEND = "🟢 GMSL3-limited   🔵 eDP-limited   🟠 Tied (equal capacity)"

    def _render_html_table(df):
        cols = list(df.columns)
        html = ['<table style="width:100%;border-collapse:collapse;font-size:1.35rem;">']
        html.append('<thead><tr>')
        for c in cols:
            html.append(f'<th style="background:#1e3a5f;color:#fff;padding:12px 16px;'
                        f'text-align:left;border:1px solid #334155;">{c}</th>')
        html.append('</tr></thead><tbody>')
        for _, row in df.iterrows():
            bg = _BN_BG.get(row["Bottleneck"], "#ffffff") if g_show_bottleneck else "#ffffff"
            html.append(f'<tr style="background:{bg};">')
            for c in cols:
                val = row[c]
                if c in _NUM_FMT_COLS:
                    val = f"{val:.2f}"
                weight = "font-weight:700;" if c == "Bottleneck" else ""
                html.append(f'<td style="padding:11px 16px;border:1px solid #cbd5e1;'
                            f'color:#0f172a;{weight}">{val}</td>')
            html.append('</tr>')
        html.append('</tbody></table>')
        return "".join(html)

    # ── High-level comparison summary across all 3 scenarios ────────────────
    st.markdown("### 📋 High-Level Comparison Summary (1 eDP Port)")
    st.caption(
        "Compares **No Compression**, **DSC Decompressed by DES**, and "
        "**DSC Pass-through by DES** side by side, fixed at 1 eDP port, "
        f"using the current eDP lane count ({g_edp_lanes} lane{'s' if g_edp_lanes>1 else ''} → "
        f"{edp_port_cap_gbps:.2f} Gbps/port)."
    )

    SUMMARY_LINKS_OPTS = [1, 2]
    SUMMARY_FPS_OPTS   = [60, 90]
    SUMMARY_BPP_OPTS   = [24, 30]
    SUMMARY_BLANK_OPTS = [0.05, 0.10]
    edp_wire_1port = edp_port_cap_gbps   # 1 eDP port, fixed wire budget

    summary_rows = []
    for links in SUMMARY_LINKS_OPTS:
        gmsl3_wire = links * GMSL3_LINK_GBPS
        for fps in SUMMARY_FPS_OPTS:
            for bpp in SUMMARY_BPP_OPTS:
                ratio = DSC_RATIO.get(bpp, 3.0)
                for blank in SUMMARY_BLANK_OPTS:
                    # A) DSC compressed, decompressed by deserializer — eDP capacity fixed (no ratio)
                    gmsl3_cap_a = gmsl3_wire * ratio
                    payload_a = min(gmsl3_cap_a, edp_wire_1port)
                    pclk_a = payload_a * 1e9 / bpp / 1e6
                    mp_a = pclk_a * 1e6 / fps / (1.0 + blank) / 1e6

                    # B) No compression — both wires carry raw bits, ratio = 1
                    payload_b = min(gmsl3_wire, edp_wire_1port)
                    pclk_b = payload_b * 1e9 / bpp / 1e6
                    mp_b = pclk_b * 1e6 / fps / (1.0 + blank) / 1e6

                    # C) DSC pass-through, decoded downstream — wire budgets unscaled,
                    #    payload reported post-decode (wire x ratio)
                    eff_bpp_c = bpp / ratio
                    bottleneck_wire_c = min(gmsl3_wire, edp_wire_1port)
                    pclk_c = bottleneck_wire_c * 1e9 / eff_bpp_c / 1e6
                    payload_c = bottleneck_wire_c * ratio
                    mp_c = pclk_c * 1e6 / fps / (1.0 + blank) / 1e6

                    summary_rows.append({
                        "GMSL3 Links":          f"{links} link{'s' if links > 1 else ''}",
                        "Frame Rate (fps)":     fps,
                        "Color Depth (bpp)":    bpp,
                        "Blanking Ratio":       f"{int(blank*100)}%",
                        "No Compression — Payload (Gbps)": round(payload_b, 2),
                        "No Compression — PCLK (MHz)":     round(pclk_b, 2),
                        "No Compression — Active Px (MP)": round(mp_b, 2),
                        "DSC Decompressed by DES — Payload (Gbps)": round(payload_a, 2),
                        "DSC Decompressed by DES — PCLK (MHz)":     round(pclk_a, 2),
                        "DSC Decompressed by DES — Active Px (MP)": round(mp_a, 2),
                        "DSC Pass-through by DES — Payload (Gbps)": round(payload_c, 2),
                        "DSC Pass-through by DES — PCLK (MHz)":     round(pclk_c, 2),
                        "DSC Pass-through by DES — Active Px (MP)": round(mp_c, 2),
                    })

    summary_df = pd.DataFrame(summary_rows)
    _SUMMARY_NUM_COLS = {c for c in summary_df.columns if "(Gbps)" in c or "(MHz)" in c or "(MP)" in c}
    _SUMMARY_HEADER_BG = {"No Compression": "#2563eb", "DSC Decompressed by DES": "#0d9488",
                          "DSC Pass-through by DES": "#d97706"}

    def _summary_header_bg(col):
        for prefix, color in _SUMMARY_HEADER_BG.items():
            if col.startswith(prefix):
                return color
        return "#1e3a5f"

    def _render_summary_table(df):
        cols = list(df.columns)
        html = ['<table style="width:100%;border-collapse:collapse;font-size:1.2rem;">']
        html.append('<thead><tr>')
        for c in cols:
            html.append(f'<th style="background:{_summary_header_bg(c)};color:#fff;padding:10px 12px;'
                        f'text-align:left;border:1px solid #334155;">{c}</th>')
        html.append('</tr></thead><tbody>')
        for i, row in df.iterrows():
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            html.append(f'<tr style="background:{bg};">')
            for c in cols:
                val = row[c]
                if c in _SUMMARY_NUM_COLS:
                    val = f"{val:.2f}"
                html.append(f'<td style="padding:9px 12px;border:1px solid #cbd5e1;color:#0f172a;">{val}</td>')
            html.append('</tr>')
        html.append('</tbody></table>')
        return "".join(html)

    st.markdown(_render_summary_table(summary_df), unsafe_allow_html=True)
    st.download_button(
        "⬇ Download Summary (CSV)",
        summary_df.to_csv(index=False).encode("utf-8"),
        file_name="gmsl3_vs_edp_summary.csv",
        mime="text/csv",
        key="g3_csv_dl_summary",
    )

    st.markdown("##### 📊 Summary Chart")
    sc1, sc2, sc3 = st.columns(3)
    sum_fps   = sc1.selectbox("Frame Rate (fps)", SUMMARY_FPS_OPTS, index=0, key="g3_sum_fps")
    sum_bpp   = sc2.selectbox("Color Depth (bpp)", SUMMARY_BPP_OPTS, index=0, key="g3_sum_bpp")
    sum_blank_pct = sc3.selectbox("Total Blanking Ratio", ["5%", "10%"], index=0, key="g3_sum_blank")

    SUMMARY_SCENARIOS = ["No Compression", "DSC Decompressed by DES", "DSC Pass-through by DES"]
    SUMMARY_SCEN_COLORS = ["#2563eb", "#0d9488", "#d97706"]

    def _sum_chart_pair(links_label):
        sum_sel = summary_df[
            (summary_df["GMSL3 Links"] == links_label) &
            (summary_df["Frame Rate (fps)"] == sum_fps) &
            (summary_df["Color Depth (bpp)"] == sum_bpp) &
            (summary_df["Blanking Ratio"] == sum_blank_pct)
        ]
        if sum_sel.empty:
            return
        sum_row = sum_sel.iloc[0]
        pclk_vals = [sum_row[f"{s} — PCLK (MHz)"] for s in SUMMARY_SCENARIOS]
        mp_vals   = [sum_row[f"{s} — Active Px (MP)"] for s in SUMMARY_SCENARIOS]

        def _sum_bar(values, title, y_title, suffix=""):
            fig = go.Figure(go.Bar(
                x=SUMMARY_SCENARIOS, y=values, marker_color=SUMMARY_SCEN_COLORS,
                marker_line=dict(color="#0f172a", width=1),
                text=[f"{v:.2f}{suffix}" for v in values],
                textposition="outside",
                textfont=dict(size=20, color="#0f172a", family="Arial Black"),
                cliponaxis=False,
                width=0.55,
            ))
            fig.update_layout(
                title=dict(text=title, font=dict(size=22, color="#1e3a5f"), x=0.02),
                height=440,
                margin=dict(t=70, b=60, l=70, r=30),
                font=dict(size=16, color="#1e293b"),
                plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
                xaxis=dict(tickfont=dict(size=16, color="#1e293b")),
                yaxis=dict(title=dict(text=y_title, font=dict(size=19, color="#374151")),
                           showgrid=True, gridcolor="#e2e8f0",
                           tickfont=dict(size=17, color="#374151"),
                           range=[0, max(values) * 1.22], zeroline=False),
                bargap=0.4,
                showlegend=False,
            )
            fig.update_xaxes(showline=True, linewidth=1, linecolor="#cbd5e1")
            fig.update_yaxes(showline=True, linewidth=1, linecolor="#cbd5e1")
            return fig

        st.markdown(f"**{links_label.title()}**")
        sc_a, sc_b = st.columns(2)
        with sc_a:
            st.plotly_chart(_sum_bar(pclk_vals, f"Max PCLK (MHz) — {links_label}", "PCLK (MHz)"),
                             use_container_width=True)
        with sc_b:
            st.plotly_chart(_sum_bar(mp_vals, f"Max Active Pixels (MP) — {links_label}",
                                     "Active Pixels (MP)"),
                             use_container_width=True)

    _sum_chart_pair("1 link")
    _sum_chart_pair("2 links")

    st.markdown("---")
    st.markdown("#### 🗜 DSC Compressed (GMSL3 input) at Decompressed by Deserializer")
    st.markdown(_render_html_table(df_dsc), unsafe_allow_html=True)
    st.download_button(
        "⬇ Download DSC Table (CSV)",
        df_dsc.to_csv(index=False).encode("utf-8"),
        file_name="gmsl3_vs_edp_dsc.csv",
        mime="text/csv",
        key="g3_csv_dl_dsc",
    )

    st.markdown("#### 📦 (GMSL3 input) Without Compression")
    st.markdown(_render_html_table(df_raw), unsafe_allow_html=True)
    if g_show_bottleneck:
        st.caption(_BN_LEGEND)
    st.download_button(
        "⬇ Download Decompressed Table (CSV)",
        df_raw.to_csv(index=False).encode("utf-8"),
        file_name="gmsl3_vs_edp_decompressed.csv",
        mime="text/csv",
        key="g3_csv_dl_raw",
    )

    st.markdown("#### 🔁 DSC Compressed Pass-through (GMSL3 input), Decoded by Downstream TCON/Bridge IC")
    st.caption(
        "The deserializer does **not** decompress — it relays the same DSC-compressed bitstream "
        "straight out the eDP port (a fixed-bandwidth physical link), and a downstream TCON or "
        "bridge IC performs the decode. GMSL3 Capacity (9.7/19.4 Gbps) and eDP Capacity "
        "(lanes × 8.1 × 80%) are the links' actual **wire bit budgets** carrying compressed bits — "
        "neither is multiplied by the DSC ratio. **Max Video Payload**, however, is the **post-decode** "
        "raw video data rate the TCON/bridge IC reconstructs: the bottleneck wire's bit budget × "
        "DSC ratio (e.g. 1 GMSL3 link @ 3:1 DSC = 9.7 × 3 = **29.1 Gbps** after decode)."
    )
    st.markdown(_render_html_table(df_pt), unsafe_allow_html=True)
    if g_show_bottleneck:
        st.caption(_BN_LEGEND)

    st.download_button(
        "⬇ Download Pass-through Table (CSV)",
        df_pt.to_csv(index=False).encode("utf-8"),
        file_name="gmsl3_vs_edp_passthrough.csv",
        mime="text/csv",
        key="g3_csv_dl_pt",
    )

    # ── Charts ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📊 Visual Comparison")

    chart_df = pd.concat([gmsl3_df, df_pt], ignore_index=True)
    chart_df["Scenario"] = (chart_df["GMSL3 Links"] + "  ·  " + chart_df["GMSL3 Compression Mode"]
                             + "  ·  " + chart_df["eDP Ports"])
    chart_df = chart_df.iloc[::-1].reset_index(drop=True)   # top-to-bottom = table order
    BAR_COLORS = {"GMSL3": "#0d9488", "eDP": "#2563eb", "Tied": "#d97706"}
    bar_colors = [BAR_COLORS[b] for b in chart_df["Bottleneck"]]

    _chart_height = max(300, 48 * len(chart_df))

    def _hbar(col, title, suffix=""):
        fig = go.Figure(go.Bar(
            x=chart_df[col], y=chart_df["Scenario"], orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.2f}{suffix}" for v in chart_df[col]],
            textposition="outside",
            textfont=dict(size=16, color="#0f172a"),
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, color="#1e3a5f")),
            height=_chart_height,
            margin=dict(l=10, r=80, t=55, b=40),
            font=dict(size=15, color="#1e293b"),
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            xaxis=dict(title=dict(text=col, font=dict(size=15)),
                       showgrid=True, gridcolor="#e2e8f0", tickfont=dict(size=14),
                       zeroline=False),
            yaxis=dict(tickfont=dict(size=15), automargin=True),
            bargap=0.35,
        )
        return fig

    st.plotly_chart(_hbar("Max Video Payload (Gbps)", "Max Video Payload (Gbps)"),
                     use_container_width=True)
    st.caption(_BN_LEGEND)

    st.plotly_chart(_hbar("Max PCLK (MHz)", "Max PCLK (MHz)"),
                     use_container_width=True)
    st.caption(_BN_LEGEND)

    st.plotly_chart(_hbar("Max Active Pixels (MP)",
                          f"Max Active Pixels (MP) @ {g_fps} fps, {g_blank_pct} blanking"),
                     use_container_width=True)
    st.caption(_BN_LEGEND)

    st.markdown("---")
    st.markdown("#### How the numbers are derived")
    st.markdown(
        "- **GMSL3 Capacity (Gbps)** = GMSL3 links × 9.7 Gbps × DSC ratio. The compression decision is "
        "made at the **GMSL3 input**: a compressed wire carries *ratio*× more equivalent raw video "
        "than its physical bit budget (e.g. 1 link × 9.7 Gbps at 3:1 DSC represents **9.7 × 3 = 29.1 "
        "Gbps** of raw video payload). For Decompressed mode the ratio is 1, so capacity = "
        "9.7 Gbps directly.\n"
        "- **eDP Capacity (Gbps)** = eDP ports × eDP lanes × 8.1 Gbps (HBR3) × 80% (8b/10b encoding "
        "efficiency) — **fixed, with no DSC multiplier**, because eDP has no DSC encoder of its own. "
        "The bridge must hand each eDP port fully decompressed/raw pixel data, so eDP's capacity never "
        "changes with GMSL3's compression mode (e.g. a single 4-lane eDP HBR3 port is always "
        "8.1×0.8 = 6.48 Gbps/lane × 4 = 25.92 Gbps; 2 such ports = 51.84 Gbps).\n"
        "- **Max Video Payload** = `min(GMSL3 Capacity, eDP Capacity)` — e.g. with 1 GMSL3 link at "
        "3:1 DSC (29.1 Gbps) feeding a 4-lane eDP HBR3 port (25.92 Gbps), eDP becomes the bottleneck "
        "(25.92 < 29.1) because GMSL3's compression gain doesn't carry over to eDP's fixed raw budget.\n"
        "- **Max PCLK (MHz)** = Max Video Payload ÷ nominal bpp (24 or 30) — note this is **independent "
        "of frame rate and blanking ratio**, since PCLK is purely bandwidth ÷ bits-per-pixel-clock.\n"
        "- **Max Active Pixels (MP)** = Max PCLK ÷ (frame rate × (1 + blanking ratio)) — this is where "
        "frame rate and blanking ratio matter: for a fixed PCLK budget, higher fps or higher blanking "
        "leaves fewer clocks available for active pixels.\n"
        "- DSC-compressed modes assume GMSL3 carries the compressed bitstream and the bridge "
        "decompresses it before driving eDP (which has no DSC of its own). Decompressed mode "
        "assumes GMSL3 already carries raw, uncompressed 24bpp video, so no decompression step "
        "is needed before eDP."
    )

# ══════════════════════════════════════════════════════════════════════════
# TAB 11 – Display Timing
# ══════════════════════════════════════════════════════════════════════════
with tab_timing:
    st.markdown("## 📐 Display Timing")
    st.markdown(
        "Pick a video resolution/timing from the dropdown, or add your own, then view the "
        "classic horizontal/vertical timing diagram (Active, Front Porch, Sync, Back Porch) "
        "with the actual numbers labeled on it."
    )

    _DT_DEFAULT_PRESETS = {
        "2880×1620 @ 60Hz — Panel Datasheet (Typ.)": {
            "h_active": 2880, "h_fp": 76, "h_sync": 24, "h_bp": 60,
            "v_active": 1620, "v_fp": 20, "v_sync": 4,  "v_bp": 16,
            "pixel_clock_mhz": 302.78,
        },
    }

    if "dt_presets" not in st.session_state:
        st.session_state["dt_presets"] = dict(_DT_DEFAULT_PRESETS)

    dt_presets = st.session_state["dt_presets"]

    dt_sel_name = st.selectbox("Video Resolution / Timing", list(dt_presets.keys()), key="dt_sel")
    dt_t = dt_presets[dt_sel_name]

    with st.expander("➕ Add New Timing"):
        st.caption("Enter a new resolution's timing parameters and click Add — it will appear in the dropdown above.")
        dtc1, dtc2, dtc3, dtc4 = st.columns(4)
        new_name   = dtc1.text_input("Name", value="", key="dt_new_name",
                                     placeholder="e.g. 1920x1080 @ 60Hz")
        new_h_act  = dtc2.number_input("H Active (px)", min_value=64, max_value=15360, value=1920, step=8, key="dt_new_hact")
        new_v_act  = dtc3.number_input("V Active (lines)", min_value=64, max_value=8640, value=1080, step=2, key="dt_new_vact")
        new_refresh = dtc4.number_input("Refresh (Hz)", min_value=24.0, max_value=240.0, value=60.0, step=1.0, key="dt_new_refresh")

        dtc5, dtc6, dtc7 = st.columns(3)
        new_h_fp   = dtc5.number_input("H Front Porch (px)", min_value=0, max_value=2000, value=48, step=1, key="dt_new_hfp")
        new_h_sync = dtc6.number_input("H Sync (px)", min_value=0, max_value=2000, value=32, step=1, key="dt_new_hsync")
        new_h_bp   = dtc7.number_input("H Back Porch (px)", min_value=0, max_value=2000, value=80, step=1, key="dt_new_hbp")

        dtc8, dtc9, dtc10 = st.columns(3)
        new_v_fp   = dtc8.number_input("V Front Porch (lines)", min_value=0, max_value=500, value=3, step=1, key="dt_new_vfp")
        new_v_sync = dtc9.number_input("V Sync (lines)", min_value=0, max_value=500, value=5, step=1, key="dt_new_vsync")
        new_v_bp   = dtc10.number_input("V Back Porch (lines)", min_value=0, max_value=500, value=38, step=1, key="dt_new_vbp")

        if st.button("Add Timing", key="dt_add_btn"):
            if not new_name.strip():
                st.warning("Please enter a name for this timing before adding it.")
            else:
                _h_total = new_h_act + new_h_fp + new_h_sync + new_h_bp
                _v_total = new_v_act + new_v_fp + new_v_sync + new_v_bp
                _pclk = _h_total * _v_total * new_refresh / 1e6
                st.session_state["dt_presets"][new_name.strip()] = {
                    "h_active": int(new_h_act), "h_fp": int(new_h_fp),
                    "h_sync": int(new_h_sync), "h_bp": int(new_h_bp),
                    "v_active": int(new_v_act), "v_fp": int(new_v_fp),
                    "v_sync": int(new_v_sync), "v_bp": int(new_v_bp),
                    "pixel_clock_mhz": round(_pclk, 2),
                }
                st.success(f"Added **{new_name.strip()}** — select it from the dropdown above.")
                st.rerun()

    # ── derived totals ──────────────────────────────────────────────────────
    dt_h_total = dt_t["h_active"] + dt_t["h_fp"] + dt_t["h_sync"] + dt_t["h_bp"]
    dt_v_total = dt_t["v_active"] + dt_t["v_fp"] + dt_t["v_sync"] + dt_t["v_bp"]
    dt_pclk    = dt_t.get("pixel_clock_mhz", dt_h_total * dt_v_total * 60 / 1e6)
    dt_refresh = dt_pclk * 1e6 / (dt_h_total * dt_v_total)
    dt_line_time_us = dt_h_total / dt_pclk   # H_total (px) / pixel clock (MHz) = µs per line

    st.markdown("#### Timing Summary")
    dtm1, dtm2, dtm3, dtm4, dtm5 = st.columns(5)
    dtm1.metric("Active", f"{dt_t['h_active']} × {dt_t['v_active']}")
    dtm2.metric("Total", f"{dt_h_total} × {dt_v_total}")
    dtm3.metric("Pixel Clock", f"{dt_pclk:.2f} MHz")
    dtm4.metric("Refresh Rate", f"{dt_refresh:.2f} Hz")
    dtm5.metric("Line Time", f"{dt_line_time_us:.3f} µs")

    _dt_summary_cols = [
        ("H Active", dt_t["h_active"]), ("H Front Porch", dt_t["h_fp"]), ("H Sync", dt_t["h_sync"]),
        ("H Back Porch", dt_t["h_bp"]), ("H Total", dt_h_total),
        ("V Active", dt_t["v_active"]), ("V Front Porch", dt_t["v_fp"]), ("V Sync", dt_t["v_sync"]),
        ("V Back Porch", dt_t["v_bp"]), ("V Total", dt_v_total),
        ("Pixel Clock (MHz)", round(dt_pclk, 2)),
        ("Line Time (µs)", round(dt_line_time_us, 3)),
    ]
    _dt_html = ['<table style="width:100%;border-collapse:collapse;font-size:1.3rem;">',
                '<thead><tr>']
    for _label, _ in _dt_summary_cols:
        _dt_html.append(f'<th style="background:#1e3a5f;color:#fff;padding:12px 16px;'
                        f'text-align:center;border:1px solid #334155;">{_label}</th>')
    _dt_html.append('</tr></thead><tbody><tr>')
    for _i, (_, _val) in enumerate(_dt_summary_cols):
        _bg = "#eff6ff" if _i % 2 == 0 else "#ffffff"
        _dt_html.append(f'<td style="padding:11px 16px;text-align:center;border:1px solid #cbd5e1;'
                        f'background:{_bg};color:#0f172a;font-weight:600;">{_val}</td>')
    _dt_html.append('</tr></tbody></table>')
    st.markdown("".join(_dt_html), unsafe_allow_html=True)

    # ── timing diagram (nested-rectangle style, matching reference) ────────
    st.markdown("#### Timing Diagram")

    def _draw_timing_diagram(t):
        h_bp, h_act, h_fp, h_sync = t["h_bp"], t["h_active"], t["h_fp"], t["h_sync"]
        v_bp, v_act, v_fp, v_sync = t["v_bp"], t["v_active"], t["v_fp"], t["v_sync"]

        NAVY, SLATE, TEAL, INDIGO = "#1e3a5f", "#334155", "#0d9488", "#4338ca"

        # Schematic (not-to-scale) proportions — porch/sync slots widened relative to
        # earlier version so their (short) labels have room and never collide.
        hbp_w, act_w, hfp_w, hs_w = 1.7, 6.0, 1.7, 1.7
        vbp_h, act_h, vfp_h, vs_h = 1.0, 4.4, 0.9, 0.9

        x0 = 0.0
        x1 = x0 + hbp_w
        x2 = x1 + act_w
        x3 = x2 + hfp_w
        x4 = x3 + hs_w

        y0 = 0.0
        y1 = y0 + vbp_h
        y2 = y1 + act_h
        y3 = y2 + vfp_h
        y4 = y3 + vs_h

        fig, ax = plt.subplots(figsize=(8.6, 5.2), dpi=130)
        ax.set_xlim(-2.6, x4 + 3.6)
        ax.set_ylim(y4 + 1.6, -1.6)   # inverted so y increases downward
        ax.axis("off")
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        ax.set_title("Display Timing Diagram", fontsize=12, fontweight="bold",
                     color=NAVY, pad=14)

        # outer rectangle (Total Horizontal Line Length x V Total) — light wash fill
        ax.add_patch(plt.Rectangle((x0, y0), x4 - x0, y4 - y0,
                                    fill=True, facecolor="#f8fafc",
                                    edgecolor=SLATE, linewidth=1.2, zorder=1))
        # inner rectangle (excludes H Back Porch on left, H Sync on right, V Sync on bottom)
        ax.add_patch(plt.Rectangle((x1, y0), x3 - x1, y3 - y0,
                                    fill=True, facecolor="#eef2f7",
                                    edgecolor=SLATE, linewidth=1.2, zorder=2))
        # active video box
        ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                    fill=True, facecolor="#bfdbfe", edgecolor=NAVY,
                                    linewidth=1.4, zorder=3))
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 0.40, "ACTIVE\nVIDEO",
                ha="center", va="center", fontsize=10.5, fontweight="bold", color=NAVY, zorder=4)

        ARROW_H = dict(arrowstyle="<->", color=TEAL, linewidth=1.1, shrinkA=0, shrinkB=0)
        ARROW_V = dict(arrowstyle="<->", color=INDIGO, linewidth=1.1, shrinkA=0, shrinkB=0)
        FS = 7.8   # base label font size — short abbreviations, kept small & consistent

        def _harrow(x_a, x_b, y, label, num, va="bottom"):
            ax.annotate("", xy=(x_b, y), xytext=(x_a, y), arrowprops=ARROW_H, zorder=5)
            ax.text((x_a + x_b) / 2, y + (-0.16 if va == "bottom" else 0.28),
                    f"{label}\n{num}", ha="center", va=va, fontsize=FS,
                    fontweight="600", color="#1e293b", zorder=6)

        def _varrow(y_a, y_b, x, label, num, ha="left"):
            ax.annotate("", xy=(x, y_b), xytext=(x, y_a), arrowprops=ARROW_V, zorder=5)
            off = 0.18 if ha == "left" else -0.18
            ax.text(x + off, (y_a + y_b) / 2, f"{label}\n{num}",
                    ha=ha, va="center", fontsize=FS, fontweight="600",
                    color="#1e293b", zorder=6)

        # Total Horizontal Line Length (top, above outer box)
        _y_top = y0 - 0.9
        ax.annotate("", xy=(x4, _y_top), xytext=(x0, _y_top), arrowprops=ARROW_H, zorder=5)
        ax.text((x0 + x4) / 2, _y_top - 0.30,
                f"H_total = {h_bp+h_act+h_fp+h_sync} px",
                ha="center", va="bottom", fontsize=8.8, fontweight="bold", color=NAVY)

        # Total Vertical Frame Length (right, beside outer box)
        _x_right = x4 + 0.7
        ax.annotate("", xy=(_x_right, y4), xytext=(_x_right, y0), arrowprops=ARROW_V, zorder=5)
        ax.text(_x_right + 0.18, (y0 + y4) / 2,
                f"V_total =\n{v_bp+v_act+v_fp+v_sync} ln",
                ha="left", va="center", fontsize=8.8, fontweight="bold", color=NAVY)

        # Vertical Back Porch (top strip, near x1)
        _varrow(y0, y1, x1 - 0.08, "V_bp", f"{v_bp} ln", ha="right")

        # Horizontal Back Porch / Front Porch / Sync sit in the UPPER part of the
        # active box height; Vertical Active Pixels label sits in the LOWER part,
        # so the two label groups never share the same vertical band.
        _y_mid = y1 + (y2 - y1) * 0.28
        ax.annotate("", xy=(x1, _y_mid), xytext=(x0, _y_mid), arrowprops=ARROW_H, zorder=5)
        ax.text((x0 + x1) / 2, _y_mid - 0.32, f"H_bp\n{h_bp} px",
                ha="center", va="bottom", fontsize=FS, fontweight="600", color="#1e293b")

        # Horizontal Active Pixels (inside active box, lower portion)
        _harrow(x1, x2, y2 - 0.55, "H_active", f"{h_act} px", va="bottom")

        # Vertical Active Pixels (inside active box, right side, label lower-half)
        ax.annotate("", xy=(x2 - 0.55, y2), xytext=(x2 - 0.55, y1), arrowprops=ARROW_V, zorder=5)
        ax.text(x2 - 0.36, y1 + (y2 - y1) * 0.72, f"V_active\n{v_act} ln",
                ha="left", va="center", fontsize=FS, fontweight="600", color="#1e293b", zorder=6)

        # Vertical Front Porch (below active box)
        _varrow(y2, y3, x1 - 0.08, "V_fp", f"{v_fp} ln", ha="right")

        # Horizontal Front Porch (between inner box right edge and active box right edge)
        ax.annotate("", xy=(x3, _y_mid), xytext=(x2, _y_mid), arrowprops=ARROW_H, zorder=5)
        ax.text((x2 + x3) / 2, _y_mid - 0.32, f"H_fp\n{h_fp} px",
                ha="center", va="bottom", fontsize=FS, fontweight="600", color="#1e293b")

        # Horizontal Sync (rightmost slice, between inner and outer box)
        ax.annotate("", xy=(x4, _y_mid), xytext=(x3, _y_mid), arrowprops=ARROW_H, zorder=5)
        ax.text((x3 + x4) / 2, _y_mid - 0.32, f"H_sync\n{h_sync} px",
                ha="center", va="bottom", fontsize=FS, fontweight="600", color="#1e293b")

        # Vertical Sync (bottom strip)
        _varrow(y3, y4, x2 + 0.08, "V_sync", f"{v_sync} ln", ha="left")

        plt.tight_layout()
        return fig

    _dt_fig = _draw_timing_diagram(dt_t)
    _dt_col, _ = st.columns([2, 1])
    with _dt_col:
        st.pyplot(_dt_fig, use_container_width=True)

    import io as _dt_io
    _dt_buf = _dt_io.BytesIO()
    _dt_fig.savefig(_dt_buf, format="png", dpi=150, bbox_inches="tight")
    st.download_button(
        "⬇ Download Timing Diagram (PNG)",
        data=_dt_buf.getvalue(),
        file_name=f"timing_diagram_{dt_sel_name.replace(' ', '_').replace('/', '-')}.png",
        mime="image/png",
        key="dt_dl_diagram",
    )
    plt.close(_dt_fig)

    # ── to-scale Gantt-bar timing diagram (line + frame) — interactive Plotly ──
    st.markdown("#### Line & Frame Timing (To Scale)")
    st.caption(
        "Each bar is drawn **proportionally to the real pixel/line counts** — Sync, Back "
        "Porch, and Front Porch are genuinely tiny slivers next to Active, which is why a "
        "zoomed inset of just the blanking region is shown next to each bar. This chart is "
        "**interactive (Plotly)** — drag to zoom, double-click to reset, and use the camera "
        "icon in the toolbar to save as PNG."
    )

    def _build_timing_bars_plotly(t):
        from plotly.subplots import make_subplots

        h_bp, h_act, h_fp, h_sync = t["h_bp"], t["h_active"], t["h_fp"], t["h_sync"]
        v_bp, v_act, v_fp, v_sync = t["v_bp"], t["v_active"], t["v_fp"], t["v_sync"]
        h_tot = h_bp + h_act + h_fp + h_sync
        v_tot = v_bp + v_act + v_fp + v_sync
        h_blank = h_sync + h_bp + h_fp
        v_blank = v_sync + v_bp + v_fp

        C_SYNC, C_BP, C_ACT, C_FP = "#dc2626", "#f59e0b", "#2563eb", "#10b981"

        fig = make_subplots(
            rows=2, cols=2,
            column_widths=[0.72, 0.28],
            row_heights=[0.5, 0.5],
            subplot_titles=(f"Horizontal Line — H_total = {h_tot} px", "Zoom: H Blanking",
                            f"Vertical Frame — V_total = {v_tot} lines", "Zoom: V Blanking"),
            horizontal_spacing=0.08, vertical_spacing=0.18,
        )

        # H-line subplots use horizontal bars (left-to-right = the order pixels are
        # clocked out). V-frame subplots use VERTICAL bars with a top-down y-axis
        # (V_sync first, V_fp last) so the bar visually scans the same direction
        # the frame actually scans on screen — not sideways.
        def _add_bar(row, col, segs, showlegend, orientation):
            pos = 0.0
            for label, val, color in segs:
                if orientation == "h":
                    trace = go.Bar(x=[val], y=[""], orientation="h", base=pos, marker_color=color,
                                   name=label, legendgroup=label, showlegend=showlegend,
                                   hovertemplate=f"{label}: {val}<extra></extra>")
                else:
                    trace = go.Bar(x=[""], y=[val], orientation="v", base=pos, marker_color=color,
                                   name=label, legendgroup=label, showlegend=showlegend,
                                   hovertemplate=f"{label}: {val}<extra></extra>")
                fig.add_trace(trace, row=row, col=col)
                pos += val

        def _add_zoom_bar(row, col, segs, orientation):
            pos = 0.0
            for label, val, color in segs:
                if orientation == "h":
                    trace = go.Bar(x=[val], y=[""], orientation="h", base=pos, marker_color=color,
                                   name=label, legendgroup=label, showlegend=False,
                                   text=f"{label}: {val}", textposition="inside",
                                   insidetextanchor="middle",
                                   textfont=dict(size=15, color="white", family="Arial Black"),
                                   hovertemplate=f"{label}: {val}<extra></extra>")
                else:
                    trace = go.Bar(x=[""], y=[val], orientation="v", base=pos, marker_color=color,
                                   name=label, legendgroup=label, showlegend=False,
                                   text=f"{label}: {val}", textposition="inside",
                                   insidetextanchor="middle",
                                   textfont=dict(size=15, color="white", family="Arial Black"),
                                   hovertemplate=f"{label}: {val}<extra></extra>")
                fig.add_trace(trace, row=row, col=col)
                pos += val

        h_segs = [("H_sync", h_sync, C_SYNC), ("H_bp", h_bp, C_BP),
                  ("H_active", h_act, C_ACT), ("H_fp", h_fp, C_FP)]
        _add_bar(1, 1, h_segs, showlegend=True, orientation="h")
        _add_zoom_bar(1, 2, [("H_sync", h_sync, C_SYNC), ("H_bp", h_bp, C_BP), ("H_fp", h_fp, C_FP)],
                      orientation="h")

        v_segs = [("V_sync", v_sync, C_SYNC), ("V_bp", v_bp, C_BP),
                  ("V_active", v_act, C_ACT), ("V_fp", v_fp, C_FP)]
        _add_bar(2, 1, v_segs, showlegend=False, orientation="v")
        _add_zoom_bar(2, 2, [("V_sync", v_sync, C_SYNC), ("V_bp", v_bp, C_BP), ("V_fp", v_fp, C_FP)],
                      orientation="v")

        # No fig-level title here — the Streamlit markdown header above the chart
        # already serves that role, and a second title was colliding with the
        # subplot titles. Just give the subplot titles room and bigger fonts.
        fig.update_layout(
            barmode="stack",
            height=560, margin=dict(t=70, b=70, l=60, r=30),
            plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
            legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5,
                        font=dict(size=15)),
            font=dict(size=14),
        )
        fig.update_annotations(font_size=16, font_color="#1e3a5f")  # subplot titles

        # Shared major+minor tick styling for every x-axis (bigger fonts, ticks
        # drawn outside the axis, minor ticks/gridlines at half the major spacing).
        def _axis_style(total):
            return dict(
                title_font=dict(size=16), tickfont=dict(size=15),
                ticks="outside", ticklen=7, tickwidth=1.5, tickcolor="#334155",
                showgrid=True, gridcolor="#e2e8f0", dtick=total / 6,
                minor=dict(ticks="outside", ticklen=4, tickwidth=1, tickcolor="#94a3b8",
                           showgrid=True, gridcolor="#f1f5f9", dtick=total / 12),
            )
        fig.update_xaxes(range=[0, h_tot], row=1, col=1, title_text="px", **_axis_style(h_tot))
        fig.update_xaxes(range=[0, h_blank], row=1, col=2, title_text="px", **_axis_style(h_blank))
        # V-frame subplots are vertical bars, so their scale lives on the y-axis
        # (reversed so V_sync/V_bp at the top, V_fp at the bottom — top-down scan
        # order, matching how a frame is actually drawn on screen).
        fig.update_yaxes(range=[v_tot, 0], row=2, col=1, title_text="lines", **_axis_style(v_tot))
        fig.update_yaxes(range=[v_blank, 0], row=2, col=2, title_text="lines", **_axis_style(v_blank))
        fig.update_xaxes(showticklabels=False, row=2, col=1)
        fig.update_xaxes(showticklabels=False, row=2, col=2)
        fig.update_yaxes(showticklabels=False, row=1, col=1)
        fig.update_yaxes(showticklabels=False, row=1, col=2)
        return fig

    _dt_fig2 = _build_timing_bars_plotly(dt_t)
    st.plotly_chart(_dt_fig2, use_container_width=True,
                     config={"displaylogo": False,
                             "modeBarButtonsToAdd": ["toImage"],
                             "toImageButtonOptions": {
                                 "filename": f"timing_bars_{dt_sel_name.replace(' ', '_').replace('/', '-')}"
                             }})

# ══════════════════════════════════════════════════════════════════════════
# TAB 12 – Multi-View Design Tool (GMSL3 IVI User Guide, pages 89-104)
# ══════════════════════════════════════════════════════════════════════════
with tab_multiview:
    st.markdown("## 🖼️ Multi-View Design Tool")
    st.caption("Based on GMSL3_IVI_User_Guide_v5.pdf, \"Multi-View\" section (pages 89-104).")

    def _mv_html_table(rows, cols=None, font_size="1.25rem"):
        """Render a list-of-dicts as a large-font HTML table."""
        if not rows:
            return ""
        cols = cols or list(rows[0].keys())
        html = [f'<table style="width:100%;border-collapse:collapse;font-size:{font_size};">',
                "<thead><tr>"]
        for c in cols:
            html.append(f'<th style="background:#1e3a5f;color:#fff;padding:11px 15px;'
                        f'text-align:center;border:1px solid #334155;">{c}</th>')
        html.append("</tr></thead><tbody>")
        for i, row in enumerate(rows):
            bg = "#eff6ff" if i % 2 == 0 else "#ffffff"
            html.append(f'<tr style="background:{bg};">')
            for c in cols:
                html.append(f'<td style="padding:10px 15px;text-align:center;'
                            f'border:1px solid #cbd5e1;color:#0f172a;font-weight:600;">{row.get(c, "")}</td>')
            html.append("</tr>")
        html.append("</tbody></table>")
        return "".join(html)

    def _hex24(v):
        v = int(v) & 0xFFFFFF
        return v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF

    def _hex16(v):
        v = int(v) & 0xFFFF
        return v & 0xFF, (v >> 8) & 0xFF

    # Register byte addresses for the asymmetric splitter bitfields, per
    # GMSL3_IVI_User_Guide_v5.pdf worked examples (Tables 28-33). Address
    # increments by 0x100 per pipe (X->Y->Z->U); several bitfields share the
    # same register byte (different bit positions within it).
    _MV_REG_BASE_ADDR = {
        "ASYM_WR_B_MUX": 0x4CE,
        "ASYM_WAIT_LINE_FOR_READ": 0x4D1,
        "ASYM_VID_EN_W_VS": 0x4CF,
        "ASYM_FR2FR_CTRL_EN": 0x4D1,
        "ALT_VTG_EN": 0x4CE,
        "AUTO_VTG_CFG": 0x4CE,
    }
    _MV_PIPE_OFFSET = {"PIPE X": 0x000, "PIPE Y": 0x100, "PIPE Z": 0x200, "PIPE U": 0x300}

    def _mv_reg_addr(bitfield, pipe):
        addr = _MV_REG_BASE_ADDR[bitfield] + _MV_PIPE_OFFSET[pipe]
        note = "" if pipe in ("PIPE X", "PIPE Y", "PIPE Z") else " (inferred from address pattern)"
        return f"0x{addr:04X}{note}"

    st.markdown(
        '<div style="font-size:1.2rem">A GMSL3 <b>serializer</b> can split one incoming '
        '<b>superframe</b> into up to <b>4 video streams</b> (output onto independent GMSL '
        'stream IDs). Multi-view modes are either <b>Symmetric</b> (sub-frames share identical '
        'timing, split via pixel-interleaving) or <b>Asymmetric</b> (sub-frames have different '
        'resolutions, padded with dummy lines to a common height). Advanced DP Serializers '
        'support up to 4 asymmetric streams; VESA DSC-compliant serializers support up to 2; '
        'multi-view is only available on serializers (not deserializers).</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    mv_mode = st.radio("Multi-View Mode", ["Symmetric (Side-by-Side)", "Asymmetric"],
                       horizontal=True, key="mv_mode")
    st.markdown('<div style="font-size:1.3rem;font-weight:700;color:#1e3a5f;margin-top:10px;">'
               f'📋 Step-by-Step Configuration — {mv_mode}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # SYMMETRIC MODE
    # ════════════════════════════════════════════════════════════════════
    if mv_mode == "Symmetric (Side-by-Side)":

        step1, step2, step3, step4, step5, step6 = st.tabs([
            "Step 1: Pre-Check", "Step 2: Sub-frame Timing Input",
            "Step 3: Computed Superframe Timing", "Step 4: Pixel Interleave",
            "Step 5: Register Configuration", "Step 6: Enable Video",
        ])

        with step1:
            st.markdown(
                '<div style="font-size:1.2rem">'
                "<b>Before configuring multi-view:</b><br>"
                "1️⃣ Ensure there is <b>no active video throughput</b> through the serializer "
                "(disable video on both the GMSL device and the upstream video source).<br>"
                "2️⃣ Confirm both Video A and Video B will share <b>identical timing</b> "
                "(active resolution, blanking, and frame rate) — this is required for "
                "Symmetric mode.</div>", unsafe_allow_html=True)

        with step2:
            st.markdown('<div style="font-size:1.2rem">Enter the timing shared by '
                       '<b>both</b> sub-frames (Video A and Video B):</div>',
                       unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns(3)
            sym_hact = sc1.number_input("Sub-frame H Active (px)", min_value=64, max_value=3840,
                                        value=1920, step=8, key="mv_sym_hact")
            sym_vact = sc2.number_input("Sub-frame V Active (lines)", min_value=64, max_value=2160,
                                        value=1080, step=2, key="mv_sym_vact")
            sym_fps  = sc3.number_input("Frame Rate (fps)", min_value=24.0, max_value=120.0,
                                        value=60.0, step=1.0, key="mv_sym_fps")
            sc4, sc5, sc6 = st.columns(3)
            sym_hfp   = sc4.number_input("Sub-frame H Front Porch (px)", min_value=0, value=88, step=1, key="mv_sym_hfp")
            sym_hsync = sc5.number_input("Sub-frame H Sync (px)", min_value=0, value=44, step=1, key="mv_sym_hsync")
            sym_hbp   = sc6.number_input("Sub-frame H Back Porch (px)", min_value=0, value=148, step=1, key="mv_sym_hbp")
            sc7, sc8, sc9 = st.columns(3)
            sym_vfp   = sc7.number_input("Sub-frame V Front Porch (lines)", min_value=0, value=4, step=1, key="mv_sym_vfp")
            sym_vsync = sc8.number_input("Sub-frame V Sync (lines)", min_value=0, value=5, step=1, key="mv_sym_vsync")
            sym_vbp   = sc9.number_input("Sub-frame V Back Porch (lines)", min_value=0, value=36, step=1, key="mv_sym_vbp")

        sub_htotal = sym_hact + sym_hfp + sym_hsync + sym_hbp
        sub_vtotal = sym_vact + sym_vfp + sym_vsync + sym_vbp
        sub_pclk   = sub_htotal * sub_vtotal * sym_fps / 1e6
        super_hact   = 2 * sym_hact
        super_hblank = 2 * (sym_hfp + sym_hsync + sym_hbp)
        super_htotal = super_hact + super_hblank
        super_vtotal = sub_vtotal
        super_pclk   = 2 * sub_pclk

        with step3:
            st.markdown(
                '<div style="font-size:1.2rem">Horizontal blanking is split symmetrically '
                "between the two streams; <b>vertical timing is unchanged</b> from superframe "
                "to sub-frame; the <b>sub-frame PCLK is half the superframe PCLK</b>.</div>",
                unsafe_allow_html=True)
            sym_rows = [
                {"Parameter": "H Active (px)", "Superframe": super_hact, "Video A": sym_hact, "Video B": sym_hact},
                {"Parameter": "H Total (px)", "Superframe": super_htotal, "Video A": sub_htotal, "Video B": sub_htotal},
                {"Parameter": "V Active (lines)", "Superframe": sym_vact, "Video A": sym_vact, "Video B": sym_vact},
                {"Parameter": "V Total (lines)", "Superframe": super_vtotal, "Video A": sub_vtotal, "Video B": sub_vtotal},
                {"Parameter": "Frame Rate (fps)", "Superframe": sym_fps, "Video A": sym_fps, "Video B": sym_fps},
                {"Parameter": "PCLK (MHz)", "Superframe": round(super_pclk, 2),
                 "Video A": round(sub_pclk, 2), "Video B": round(sub_pclk, 2)},
            ]
            st.markdown(_mv_html_table(sym_rows), unsafe_allow_html=True)

            fig_sym, ax_sym = plt.subplots(figsize=(7.5, 3.4), dpi=120)
            ax_sym.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="#bfdbfe", edgecolor="#1e3a5f", linewidth=2))
            ax_sym.add_patch(plt.Rectangle((1, 0), 1, 1, facecolor="#fecaca", edgecolor="#7f1d1d", linewidth=2))
            ax_sym.text(0.5, 0.5, f"Video A\n{sym_hact}×{sym_vact}", ha="center", va="center", fontsize=15, fontweight="bold", color="#1e3a5f")
            ax_sym.text(1.5, 0.5, f"Video B\n{sym_hact}×{sym_vact}", ha="center", va="center", fontsize=15, fontweight="bold", color="#7f1d1d")
            ax_sym.set_xlim(0, 2); ax_sym.set_ylim(0, 1); ax_sym.axis("off")
            ax_sym.set_title(f"Superframe {super_hact}×{sym_vact} (Symmetric Side-by-Side)", fontsize=14, fontweight="bold", color="#1e3a5f")
            plt.tight_layout()
            st.pyplot(fig_sym, use_container_width=False)
            plt.close(fig_sym)

        with step4:
            N = sym_hact
            example_seq = []
            for i in range(min(4, N)):
                example_seq += [i, N + i]
            st.markdown(
                '<div style="font-size:1.2rem">The superframe line (length = 2N, '
                f'N = {N}) is pixel-interleaved before splitting: every odd pixel goes to '
                'one stream, every even pixel to the other:</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-size:1.3rem;font-family:monospace;background:#f1f5f9;'
                f'padding:14px;border-radius:6px;border:1px solid #cbd5e1;">'
                f'{", ".join(str(v) for v in example_seq)}, ... , {N-2}, {2*N-2}, {N-1}, {2*N-1}'
                f'</div>', unsafe_allow_html=True)

        with step5:
            if st.button("🖼️ Generate Symmetric Demo Picture", key="mv_sym_demo_btn"):
                with st.spinner("Rendering demo superframe..."):
                    _sym_demo = np.zeros((sym_vact, super_hact, 3), dtype=np.uint8)
                    _draw_nav_panel(_sym_demo, 0, 0, sym_hact, sym_vact)
                    _draw_camera_panel(_sym_demo, sym_hact, 0, sym_hact, sym_vact)
                    _sym_demo_img = Image.fromarray(_sym_demo)
                    _dd_sym = ImageDraw.Draw(_sym_demo_img)
                    _dd_sym.line([(sym_hact, 0), (sym_hact, sym_vact)], fill=(255, 255, 0), width=4)
                    _sym_demo_arr = np.array(_sym_demo_img)
                st.image(_sym_demo_arr, caption=f"Demo Superframe — {super_hact}×{sym_vact} "
                                               f"(Video A | Video B)", use_container_width=True)
                import io as _mv_io
                _sym_buf = _mv_io.BytesIO()
                Image.fromarray(_sym_demo_arr).save(_sym_buf, format="PNG")
                st.download_button("⬇ Download Demo Picture (PNG)", data=_sym_buf.getvalue(),
                                   file_name=f"multiview_symmetric_demo_{super_hact}x{sym_vact}.png",
                                   mime="image/png", key="mv_sym_demo_dl")

            if st.button("🎬 Generate 5-Second Demo Video", key="mv_sym_video_btn"):
                with st.spinner("Rendering 5-second demo video..."):
                    import imageio as _mv_imageio

                    _VID_FPS = 24
                    _VID_SEC = 5
                    _N_FRAMES = _VID_FPS * _VID_SEC

                    # Static base content (nav + camera panels) drawn once and reused —
                    # only a small animated overlay changes per frame to show real motion
                    # while keeping render time reasonable.
                    _base_demo = np.zeros((sym_vact, super_hact, 3), dtype=np.uint8)
                    _draw_nav_panel(_base_demo, 0, 0, sym_hact, sym_vact)
                    _draw_camera_panel(_base_demo, sym_hact, 0, sym_hact, sym_vact)

                    _frames_sym = []
                    for _fi in range(_N_FRAMES):
                        _t = _fi / _N_FRAMES
                        _frame_img = Image.fromarray(_base_demo.copy())
                        _fd = ImageDraw.Draw(_frame_img)

                        # Video A: a marker travels along a simple route line (top-left to
                        # bottom-right diagonal) to simulate live navigation movement.
                        _mx = int(sym_hact * 0.15 + (sym_hact * 0.7) * _t)
                        _my = int(sym_vact * 0.25 + (sym_vact * 0.5) * _t)
                        _r = max(6, sym_vact // 60)
                        _fd.ellipse([_mx - _r, _my - _r, _mx + _r, _my + _r],
                                   fill=(220, 40, 40), outline=(255, 255, 255), width=2)

                        # Video B: a horizontal scan line sweeps top-to-bottom to simulate
                        # a live camera feed refreshing.
                        _scan_y = int((sym_vact - 1) * _t)
                        _fd.line([(sym_hact, _scan_y), (2 * sym_hact, _scan_y)],
                                fill=(80, 220, 255), width=3)

                        # Frame divider + frame counter
                        _fd.line([(sym_hact, 0), (sym_hact, sym_vact)], fill=(255, 255, 0), width=4)
                        _fd.text((10, 10), f"Frame {_fi+1}/{_N_FRAMES}  t={_t*_VID_SEC:.2f}s",
                                fill=(255, 255, 0))

                        _frames_sym.append(np.array(_frame_img))

                    import tempfile as _mv_tempfile, os as _mv_os
                    _tmp_vid = _mv_tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
                    _tmp_vid.close()
                    with _mv_imageio.get_writer(_tmp_vid.name, format="FFMPEG", fps=_VID_FPS,
                                                codec="libx264", pixelformat="yuv420p") as _w_sym:
                        for _fr_sym in _frames_sym:
                            _w_sym.append_data(_fr_sym)
                    with open(_tmp_vid.name, "rb") as _f_sym:
                        _sym_video_bytes = _f_sym.read()
                    _mv_os.unlink(_tmp_vid.name)

                st.video(_sym_video_bytes, format="video/mp4")
                st.caption(f"Symmetric multi-view demo — {super_hact}×{sym_vact} superframe, "
                          f"{_VID_SEC}s @ {_VID_FPS}fps (Video A: nav route marker | "
                          f"Video B: camera scan line)")
                st.download_button("⬇ Download Demo Video (MP4)", data=_sym_video_bytes,
                                   file_name=f"multiview_symmetric_demo_{super_hact}x{sym_vact}_5s.mp4",
                                   mime="video/mp4", key="mv_sym_video_dl")
            st.markdown("---")

            st.markdown(
                '<div style="font-size:1.2rem">Per-pipe video timing registers (used by the '
                "fractional M/N clock generator). <b>M</b> = H_total × V_total of that pipe's "
                "timing; <b>N</b> is a fixed reference value (461000 in the reference design) "
                "used in the M/N ratio calculation.</div>", unsafe_allow_html=True)
            M_val = sub_htotal * sub_vtotal
            N_val = 461000
            m_l, m_m, m_h = _hex24(M_val)
            n_l, n_m, n_h = _hex24(N_val)
            reg_rows = []
            for pipe, label in [("PIPE X", "Video A"), ("PIPE Y", "Video B")]:
                reg_rows.append({"Pipe": pipe, "Stream": label, "Register": "M_h / M_m / M_l",
                                 "Decimal": M_val, "Hex (h, m, l)": f"0x{m_h:02X}, 0x{m_m:02X}, 0x{m_l:02X}"})
                reg_rows.append({"Pipe": pipe, "Stream": label, "Register": "N_h / N_m / N_l",
                                 "Decimal": N_val, "Hex (h, m, l)": f"0x{n_h:02X}, 0x{n_m:02X}, 0x{n_l:02X}"})
            st.markdown(_mv_html_table(reg_rows), unsafe_allow_html=True)
            st.caption(
                "Note: pixel-level interleaving (Symmetric mode) does not use the spatial "
                "X_OFFSET / X_MAX window registers — those apply to Asymmetric mode's "
                "side-by-side spatial split (see Asymmetric → Step 5)."
            )
            split_rows = []
            for pipe, label in [("PIPE X", "Video A"), ("PIPE Y", "Video B")]:
                for bf, val in [
                    ("ASYM_WR_B_MUX", "0 (Enable video split)"),
                    ("ASYM_WAIT_LINE_FOR_READ", "1 (Start FIFO read after 1 full line written)"),
                    ("ASYM_VID_EN_W_VS", "1 (Wait 4 Vsync cycles before enabling video Tx)"),
                    ("ASYM_FR2FR_CTRL_EN", "1 (Enable frame-to-frame FIFO control, auto M/N calc)"),
                    ("ALT_VTG_EN", "0 (Disable alternative VTG generator)"),
                    ("AUTO_VTG_CFG", "0 (Disable — use values programmed above, not DP-RX auto-detect)"),
                ]:
                    split_rows.append({
                        "Pipe": pipe, "Stream": label, "Bitfield": f"{bf}_{pipe[-1]}",
                        "Register Address": _mv_reg_addr(bf, pipe), "Recommended Value": val,
                    })
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(_mv_html_table(split_rows,
                                       cols=["Pipe", "Stream", "Bitfield", "Register Address", "Recommended Value"]),
                       unsafe_allow_html=True)
            st.caption(
                "Bitfield names, register addresses, and recommended values per "
                "GMSL3_IVI_User_Guide_v5.pdf, Tables 28-33. Address pattern increments by "
                "0x100 per pipe; verify against your part's exact register map."
            )

        with step6:
            st.markdown(
                '<div style="font-size:1.2rem">Once Steps 2-5 are written:<br>'
                "1️⃣ Verify FIFO and split-enable bits are set as configured in Step 5.<br>"
                "2️⃣ Re-enable video on the upstream source (SoC) to start streaming the "
                "superframe.<br>"
                "3️⃣ Re-enable video Tx on the serializer — it will begin outputting "
                "Video A and Video B on their independent GMSL stream IDs.</div>",
                unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # ASYMMETRIC MODE
    # ════════════════════════════════════════════════════════════════════
    else:
        n_sub = st.radio("Number of Sub-frames", [2, 3, 4], horizontal=True, key="mv_asym_n")
        st.markdown("---")

        step1, step2, step3, step4, step5, step6 = st.tabs([
            "Step 1: Pre-Check", "Step 2: Port Duplication",
            "Step 3: FIFO & Split Enable", "Step 4: Sub-frame Inputs",
            "Step 5: Timing Registers & LUT", "Step 6: Enable Video",
        ])

        with step1:
            st.markdown(
                '<div style="font-size:1.2rem">'
                "<b>Before configuring multi-view:</b><br>"
                "1️⃣ Ensure there is <b>no active video throughput</b> through the serializer "
                "(disable video on both the GMSL device and the upstream video source).<br>"
                "2️⃣ Confirm sub-frame resolutions/timings are known — Asymmetric mode allows "
                "<b>different</b> resolutions per sub-frame, each padded with dummy lines to "
                "match the tallest sub-frame.</div>", unsafe_allow_html=True)

        with step2:
            if n_sub > 2:
                st.markdown(
                    '<div style="font-size:1.2rem">Stream count &gt; 2, so the video '
                    "received on DPRX Port 0 must be <b>duplicated to Port 2</b> to provide "
                    "a second DP port for splitting.</div>", unsafe_allow_html=True)
                dup_rows = [{"Bitfield": "DUP_0_TO_2", "Register Path": "PIPE X DUP_0_TO_2",
                            "Recommended Value": "0 (Enable asymmetric video split / duplication)",
                            "Example Write": "0x80, 0x6421, 0x2F"}]
                st.markdown(_mv_html_table(dup_rows), unsafe_allow_html=True)
            else:
                st.success("✅ Stream count ≤ 2 — Port duplication (DUP_0_TO_2) is not required.")

        with step3:
            st.markdown('<div style="font-size:1.2rem">Enable the asymmetric video '
                       "splitter and configure FIFO read timing:</div>", unsafe_allow_html=True)
            pipes_needed = ["PIPE X", "PIPE Y", "PIPE Z", "PIPE U"][:n_sub]
            fifo_rows = []
            for p in pipes_needed:
                for bf, val in [
                    ("ASYM_WR_B_MUX", "0 (Enable asymmetric video split)"),
                    ("ASYM_WAIT_LINE_FOR_READ", "1 (Read FIFO after 1 full line written)"),
                    ("ASYM_VID_EN_W_VS", "1 (Wait 4 Vsync cycles before enabling video Tx)"),
                    ("ASYM_FR2FR_CTRL_EN", "1 (Enable frame-to-frame FIFO control, auto M/N calc)"),
                    ("ALT_VTG_EN", "0 (Disable alternative VTG generator)"),
                    ("AUTO_VTG_CFG", "0 (Disable — use values programmed in Step 5)"),
                ]:
                    fifo_rows.append({
                        "Pipe": p, "Bitfield": f"{bf}_{p[-1]}",
                        "Register Address": _mv_reg_addr(bf, p), "Recommended Value": val,
                    })
            st.markdown(_mv_html_table(fifo_rows, cols=["Pipe", "Bitfield", "Register Address", "Recommended Value"]),
                       unsafe_allow_html=True)
            st.caption(
                "Bitfield names, register addresses, and recommended values per "
                "GMSL3_IVI_User_Guide_v5.pdf, Tables 28-33. Address pattern increments by "
                "0x100 per pipe; verify against your part's exact register map."
            )

        RATIO_OPTS = ["1:1", "2:1", "3:1", "3:2", "4:1", "4:3", "5:2", "5:3", "8:5",
                     "2:1 inverted", "Custom / LUT"]
        RATIO_VALUES = {"1:1": 1.0, "2:1": 2.0, "3:1": 3.0, "3:2": 1.5, "4:1": 4.0,
                        "4:3": 4/3, "5:2": 2.5, "5:3": 5/3, "8:5": 1.6, "2:1 inverted": 0.5}
        _default_asym = [(1920, 720, 100, 40, 40, 6, 5, 6),
                         (1280, 720, 100, 40, 40, 6, 5, 6),
                         (800, 480, 40, 40, 40, 6, 5, 6),
                         (640, 480, 40, 40, 40, 6, 5, 6)]

        with step4:
            st.markdown(
                '<div style="font-size:1.2rem"><b>Tip:</b> order sub-frames with the '
                "largest V Active <b>first / leftmost</b>, per the recommended subframe "
                "ordering rule.</div>", unsafe_allow_html=True)
            asym_specs = []
            cols = st.columns(n_sub)
            for i in range(n_sub):
                with cols[i]:
                    st.markdown(f"**Sub-frame {i+1}**")
                    hact = st.number_input("H Active", min_value=64, max_value=3840,
                                           value=_default_asym[i][0], step=8, key=f"mv_asym_hact_{i}")
                    vact = st.number_input("V Active", min_value=64, max_value=2160,
                                           value=_default_asym[i][1], step=2, key=f"mv_asym_vact_{i}")
                    hbp  = st.number_input("H Back Porch", min_value=0, value=_default_asym[i][2], step=1, key=f"mv_asym_hbp_{i}")
                    hfp  = st.number_input("H Front Porch", min_value=0, value=_default_asym[i][3], step=1, key=f"mv_asym_hfp_{i}")
                    hsync= st.number_input("H Sync", min_value=0, value=_default_asym[i][4], step=1, key=f"mv_asym_hsync_{i}")
                    vbp  = st.number_input("V Back Porch", min_value=0, value=_default_asym[i][5], step=1, key=f"mv_asym_vbp_{i}")
                    vfp  = st.number_input("V Front Porch", min_value=0, value=_default_asym[i][6], step=1, key=f"mv_asym_vfp_{i}")
                    vsync= st.number_input("V Sync", min_value=0, value=_default_asym[i][7], step=1, key=f"mv_asym_vsync_{i}")
                    asym_specs.append({"hact": hact, "vact": vact, "hbp": hbp, "hfp": hfp,
                                       "hsync": hsync, "vbp": vbp, "vfp": vfp, "vsync": vsync})
            asym_fps = st.number_input("Frame Rate (fps, shared by all sub-frames)",
                                       min_value=24.0, max_value=120.0, value=60.0, step=1.0, key="mv_asym_fps")

            v_acts = [s["vact"] for s in asym_specs]
            if v_acts != sorted(v_acts, reverse=True):
                st.warning(
                    "⚠️ Per the user guide, sub-frames should be ordered with the **largest "
                    "V Active on the left** (Sub-frame 1). Current order is not descending — "
                    f"V Active values: {v_acts}."
                )
            else:
                st.success("✅ Sub-frame ordering follows the recommended largest-V Active-left rule.")

        v_max = max(v_acts)
        rows = []
        for i, s in enumerate(asym_specs):
            pad_lines = v_max - s["vact"]
            v_total_i = s["vact"] + s["vbp"] + s["vfp"] + s["vsync"]
            h_total_i = s["hact"] + s["hbp"] + s["hfp"] + s["hsync"]
            pclk_i = h_total_i * v_total_i * asym_fps / 1e6
            achieved_ratio = (v_max / s["vact"]) if s["vact"] else None
            nearest = min(RATIO_VALUES, key=lambda k: abs(RATIO_VALUES[k] - achieved_ratio)) if achieved_ratio else "N/A"
            ratio_ok = achieved_ratio is not None and abs(RATIO_VALUES[nearest] - achieved_ratio) < 0.03
            rows.append({
                "Sub-frame": i + 1, "H Active": s["hact"], "V Active": s["vact"],
                "Padding Lines": pad_lines, "V Total (own)": v_total_i, "H Total (own)": h_total_i,
                "Native PCLK (MHz)": round(pclk_i, 2),
                "Achieved V Ratio": f"{achieved_ratio:.3f}" if achieved_ratio else "—",
                "Nearest Predefined Ratio": nearest if i > 0 else "—",
                "Ratio Match": ("✅" if ratio_ok else "⚠️ Use Custom LUT") if i > 0 else "—",
            })
        super_hact_total = sum(s["hact"] for s in asym_specs)
        largest = asym_specs[v_acts.index(v_max)]
        super_vtotal = v_max + largest["vbp"] + largest["vfp"] + largest["vsync"]
        blank_largest = largest["vbp"] + largest["vsync"] + largest["vfp"]

        with step5:
            if st.button("🖼️ Generate Asymmetric Demo Picture", key="mv_asym_demo_btn"):
                with st.spinner("Rendering demo superframe..."):
                    _asym_panels = [_draw_nav_panel, _draw_camera_panel, _draw_climate_panel, _draw_mm_panel]
                    _asym_demo = np.full((v_max, super_hact_total, 3), 60, dtype=np.uint8)
                    _agx = 0
                    for i, s in enumerate(asym_specs):
                        _asym_panels[i % len(_asym_panels)](_asym_demo, _agx, 0, s["hact"], s["vact"])
                        _agx += s["hact"]
                    _asym_demo_img = Image.fromarray(_asym_demo)
                    _dd_asym = ImageDraw.Draw(_asym_demo_img)
                    try:
                        _af_font = ImageFont.truetype("arialbd.ttf", max(14, v_max // 30))
                    except Exception:
                        _af_font = ImageFont.load_default()
                    _agx = 0
                    for i, s in enumerate(asym_specs):
                        if s["vact"] < v_max:
                            pad_h = v_max - s["vact"]
                            _dd_asym.rectangle([_agx, s["vact"], _agx + s["hact"] - 1, v_max - 1],
                                              fill=(60, 60, 60))
                            _dd_asym.text((_agx + s["hact"] / 2, s["vact"] + pad_h / 2),
                                        f"PADDING ({pad_h}px)", fill=(200, 200, 200),
                                        font=_af_font, anchor="mm")
                        if i > 0:
                            _dd_asym.line([(_agx, 0), (_agx, v_max)], fill=(255, 255, 0), width=4)
                        _agx += s["hact"]
                    _asym_demo_arr = np.array(_asym_demo_img)
                st.image(_asym_demo_arr,
                        caption=f"Demo Superframe — {super_hact_total}×{v_max} (Asymmetric)",
                        use_container_width=True)
                import io as _mv_io2
                _asym_buf = _mv_io2.BytesIO()
                Image.fromarray(_asym_demo_arr).save(_asym_buf, format="PNG")
                st.download_button("⬇ Download Demo Picture (PNG)", data=_asym_buf.getvalue(),
                                   file_name=f"multiview_asymmetric_demo_{super_hact_total}x{v_max}.png",
                                   mime="image/png", key="mv_asym_demo_dl")
            st.markdown("---")

            st.markdown('<div style="font-size:1.2rem">Computed padding, native timing, '
                       "and predefined-ratio matching for each sub-frame:</div>",
                       unsafe_allow_html=True)
            st.caption(
                "**Achieved V Ratio** = V_active_max ÷ V_active(this sub-frame) — e.g. "
                f"sub-frame 3 above: {v_max} ÷ {asym_specs[2]['vact'] if len(asym_specs) > 2 else '…'} "
                "= 1.500. **Nearest Predefined Ratio** finds the closest match in the spec's "
                "table (1:1, 2:1, 3:1, 3:2, 4:1, 4:3, 5:2, 5:3, 8:5, 2:1 inverted) — 1.500 = "
                "exactly **3:2**. **Ratio Match** is ✅ when the achieved ratio is within 0.03 "
                "of that predefined value (so the predefined padding circuitry can be used "
                "directly); otherwise it flags ⚠️ Use Custom LUT. The largest sub-frame "
                "(Sub-frame 1) shows '—' since it's the reference, not compared to itself."
            )
            st.markdown(_mv_html_table(rows, font_size="1.1rem"), unsafe_allow_html=True)

            st.markdown(
                f'<div style="font-size:1.25rem;margin-top:14px;"><b>Superframe size:</b> '
                f"{super_hact_total} × {super_vtotal} (H Active = sum of each sub-frame's "
                f"own width; V Total = the <b>largest</b> sub-frame's full V Total).</div>",
                unsafe_allow_html=True)

            st.markdown('<div style="font-size:1.25rem;font-weight:700;margin-top:18px;'
                       'color:#1e3a5f;">Blanking-Ratio Consistency Check</div>',
                       unsafe_allow_html=True)
            st.caption(
                "Per the user guide: V_active_max / V_active_i should equal "
                "Blank_i / Blank_max for the padding to align cleanly without LUT overrides."
            )
            chk_rows = []
            for i, s in enumerate(asym_specs):
                if s is largest:
                    continue
                lhs = v_max / s["vact"] if s["vact"] else 0
                blank_i = s["vbp"] + s["vsync"] + s["vfp"]
                rhs = blank_i / blank_largest if blank_largest else 0
                match = abs(lhs - rhs) < 0.05
                chk_rows.append({
                    "Sub-frame": i + 1, "V_active_max / V_active_i": round(lhs, 3),
                    "Blank_i / Blank_max": round(rhs, 3),
                    "Consistent": "✅" if match else "⚠️ Mismatch — review blanking",
                })
            st.markdown(_mv_html_table(chk_rows), unsafe_allow_html=True)

            st.markdown('<div style="font-size:1.25rem;font-weight:700;margin-top:18px;'
                       'color:#1e3a5f;">Per-Pipe Timing Registers</div>',
                       unsafe_allow_html=True)
            st.caption(
                "M = H_total × V_total (own timing); N = 461000 (fixed reference value); "
                "X_OFFSET = cumulative H Active of preceding pipes; X_MAX = this pipe's H Active."
            )
            N_val = 461000
            n_l, n_m, n_h = _hex24(N_val)
            reg_rows2 = []
            x_off = 0
            for i, (p, s) in enumerate(zip(pipes_needed, asym_specs)):
                h_total_i = s["hact"] + s["hbp"] + s["hfp"] + s["hsync"]
                v_total_i = s["vact"] + s["vbp"] + s["vfp"] + s["vsync"]
                M_val = h_total_i * v_total_i
                m_l, m_m, m_h = _hex24(M_val)
                xo_l, xo_h = _hex16(x_off)
                xm_l, xm_h = _hex16(s["hact"])
                reg_rows2.append({
                    "Pipe": p, "Sub-frame": i + 1,
                    "M (dec)": M_val, "M (h,m,l hex)": f"0x{m_h:02X},0x{m_m:02X},0x{m_l:02X}",
                    "N (h,m,l hex)": f"0x{n_h:02X},0x{n_m:02X},0x{n_l:02X}",
                    "X_OFFSET (dec)": x_off, "X_OFFSET (h,l hex)": f"0x{xo_h:02X},0x{xo_l:02X}",
                    "X_MAX (dec)": s["hact"], "X_MAX (h,l hex)": f"0x{xm_h:02X},0x{xm_l:02X}",
                })
                x_off += s["hact"]
            st.markdown(_mv_html_table(reg_rows2, font_size="1.05rem"), unsafe_allow_html=True)

            st.markdown('<div style="font-size:1.25rem;font-weight:700;margin-top:18px;'
                       'color:#1e3a5f;">LUT Selection</div>', unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:1.15rem">If a sub-frame\'s achieved ratio does not '
                "match a predefined ratio (see table above), program the "
                "<b>Asymmetric Look-Up Table (LUT)</b> registers to mark which lines to "
                "remove from the output video:</div>", unsafe_allow_html=True)
            lut_rows = [
                {"Register": "ASYM_LUT_X", "Bitfield": "ASYM_DV_LUT_0 ~ ASYM_DV_LUT_10D[7:0]"},
                {"Register": "ASYM_LUT_Y", "Bitfield": "ASYM_DV_LUT_0 ~ ASYM_DV_LUT_10D[7:0]"},
                {"Register": "ASYM_LUT_Z", "Bitfield": "ASYM_DV_LUT_0 ~ ASYM_DV_LUT_10D[7:0]"},
                {"Register": "ASYM_LUT_U", "Bitfield": "ASYM_DV_LUT_0 ~ ASYM_DV_LUT_10D[7:0]"},
            ]
            st.markdown(_mv_html_table(lut_rows, cols=["Register", "Bitfield"]), unsafe_allow_html=True)
            st.caption(
                "Note: VESA DSC-compliant serializers do not support LUT functionality with "
                "multi-view splitting — only the predefined ratios are available on that family."
            )

            st.markdown('<div style="font-size:1.25rem;font-weight:700;margin-top:18px;'
                       'color:#1e3a5f;">Layout Preview</div>', unsafe_allow_html=True)
            _palette_mv = ["#bfdbfe", "#fecaca", "#bbf7d0", "#fde68a"]
            fig_asym, ax_asym = plt.subplots(figsize=(8.5, 3.8), dpi=120)
            gx = 0.0
            scale = 1.0 / max(super_hact_total, 1)
            for i, s in enumerate(asym_specs):
                w = s["hact"] * scale
                h = s["vact"] / v_max
                ax_asym.add_patch(plt.Rectangle((gx, 1 - h), w, h, facecolor=_palette_mv[i % 4],
                                                edgecolor="#1e293b", linewidth=1.5))
                if h < 1.0:
                    ax_asym.add_patch(plt.Rectangle((gx, 0), w, 1 - h, facecolor="#cbd5e1",
                                                    edgecolor="#1e293b", linewidth=1.2, hatch="//"))
                    ax_asym.text(gx + w / 2, (1 - h) / 2, "PAD", ha="center", va="center",
                                fontsize=11, color="#475569", fontweight="bold")
                ax_asym.text(gx + w / 2, 1 - h / 2, f"Sub {i+1}\n{s['hact']}×{s['vact']}",
                            ha="center", va="center", fontsize=12, fontweight="bold", color="#1e293b")
                gx += w
            ax_asym.set_xlim(0, 1); ax_asym.set_ylim(0, 1); ax_asym.axis("off")
            ax_asym.set_title(f"Superframe {super_hact_total}×{v_max} (Asymmetric)",
                              fontsize=15, fontweight="bold", color="#1e3a5f")
            plt.tight_layout()
            st.pyplot(fig_asym, use_container_width=False)
            plt.close(fig_asym)

        with step6:
            st.markdown(
                '<div style="font-size:1.2rem">Once Steps 2-5 are written:<br>'
                "1️⃣ Verify port duplication (if used), FIFO/split-enable bits, per-pipe "
                "M/N/X_OFFSET/X_MAX registers, and LUT settings (if used) are all correct.<br>"
                "2️⃣ Re-enable video on the upstream source (SoC) to start streaming the "
                "superframe.<br>"
                "3️⃣ Re-enable video Tx on the serializer — it will begin outputting each "
                "sub-frame, with padding lines removed and native resolution/timing restored, "
                "on its own GMSL stream ID.</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB – Display Driver IC (TDDI channel / bandwidth / touch sizing)
# ════════════════════════════════════════════════════════════════════════════
with tab_tddi:
    st.markdown('<h3 class="section-header">TDDI Display Driver IC — Count Calculator</h3>',
                unsafe_allow_html=True)
    st.caption(
        "Determines the number of TDDI driver ICs needed, checking three independent "
        "limits — source (display) channel count, LVDS P2P bandwidth, and touch sensor "
        "channel count — and recommends the worst-case (largest) requirement.")

    with st.form(key="tddi_form"):
        tddi_c1, tddi_c2, tddi_c3 = st.columns(3)
        with tddi_c1:
            st.markdown("#### Display")
            tddi_hres  = st.number_input("Horizontal res (px)", min_value=64, max_value=20000,
                                          value=7888, step=1, key="tddi_hres")
            tddi_vres  = st.number_input("Vertical res (px)", min_value=64, max_value=8000,
                                          value=1576, step=1, key="tddi_vres")
            tddi_dsize = st.number_input("Display size (in, diagonal)", min_value=1.0, max_value=200.0,
                                          value=40.2, step=0.1, key="tddi_dsize")
            tddi_blank = st.number_input("Total blanking (%)", min_value=0.0, max_value=30.0,
                                          value=5.0, step=0.1, key="tddi_blank")
            tddi_fps   = st.number_input("Frame rate (Hz)", min_value=24, max_value=240,
                                          value=60, step=1, key="tddi_fps")
            tddi_bpp   = st.number_input("Bits per pixel", min_value=8, max_value=48,
                                          value=24, step=1, key="tddi_bpp")
        with tddi_c2:
            st.markdown("#### Interface (per IC)")
            tddi_lvds_out = st.number_input("LVDS outputs / IC", min_value=1, max_value=8,
                                             value=2, step=1, key="tddi_lvds_out")
            tddi_mhz_out  = st.number_input("Max MHz per output (P2P)", min_value=10, max_value=600,
                                             value=140, step=1, key="tddi_mhz_out")
            tddi_disp_ch  = st.number_input("Display channels / IC", min_value=1, max_value=10000,
                                             value=1920, step=1, key="tddi_disp_ch")
            tddi_disp_mux = st.number_input("Display MUX ratio", min_value=1, max_value=8,
                                             value=4, step=1, key="tddi_disp_mux")
        with tddi_c3:
            st.markdown("#### Touch")
            tddi_touch_ch  = st.number_input("Touch channels / IC", min_value=1, max_value=10000,
                                              value=960, step=1, key="tddi_touch_ch")
            tddi_touch_mux = st.number_input("Touch MUX ratio", min_value=1, max_value=8,
                                              value=2, step=1, key="tddi_touch_mux")
            tddi_pitch     = st.number_input("Touch sensor pitch (mm)", min_value=0.5, max_value=50.0,
                                              value=6.0, step=0.1, key="tddi_pitch")

        st.markdown("")
        tddi_calc_clicked = st.form_submit_button("🧮 Calculate", type="primary",
                                                   key="tddi_calculate_btn")

    # ── Calculations (only run when the button is clicked) ────────────────────
    if tddi_calc_clicked:
        tddi_source_lines = tddi_hres * 3
        tddi_per_ic_ch    = tddi_disp_ch * tddi_disp_mux
        tddi_ics_ch       = math.ceil(tddi_source_lines / tddi_per_ic_ch)

        tddi_active_px  = tddi_hres * tddi_vres
        tddi_total_px   = tddi_active_px / (1 - tddi_blank / 100)
        tddi_pixel_rate = tddi_total_px * tddi_fps
        tddi_per_ic_bw  = tddi_lvds_out * tddi_mhz_out * 1e6
        tddi_ics_bw     = math.ceil(tddi_pixel_rate / tddi_per_ic_bw)

        tddi_ratio   = tddi_hres / tddi_vres
        tddi_diag_mm = tddi_dsize * 25.4
        tddi_h_mm    = tddi_diag_mm / math.sqrt(tddi_ratio**2 + 1)
        tddi_w_mm    = tddi_ratio * tddi_h_mm
        tddi_nx      = math.ceil(tddi_w_mm / tddi_pitch)
        tddi_ny      = math.ceil(tddi_h_mm / tddi_pitch)
        tddi_touch_nodes  = tddi_nx * tddi_ny
        tddi_per_ic_touch = tddi_touch_ch * tddi_touch_mux
        tddi_ics_touch    = math.ceil(tddi_touch_nodes / tddi_per_ic_touch)

        tddi_final_ics = max(tddi_ics_ch, tddi_ics_bw, tddi_ics_touch)

        st.session_state["tddi_results"] = dict(
            source_lines=tddi_source_lines, per_ic_ch=tddi_per_ic_ch, ics_ch=tddi_ics_ch,
            pixel_rate=tddi_pixel_rate, per_ic_bw=tddi_per_ic_bw, ics_bw=tddi_ics_bw,
            nx=tddi_nx, ny=tddi_ny, touch_nodes=tddi_touch_nodes,
            per_ic_touch=tddi_per_ic_touch, ics_touch=tddi_ics_touch,
            final_ics=tddi_final_ics,
        )

    # ── Results (persist across reruns until Calculate is clicked again) ───────
    if "tddi_results" in st.session_state:
        r = st.session_state["tddi_results"]
        st.markdown("#### IC Count by Limiting Factor")
        t1, t2, t3, t4 = st.columns(4)
        mcard(t1, "Source-limited", str(r["ics_ch"]),
              f"{r['source_lines']:,} ch needed / {r['per_ic_ch']:,} per IC")
        mcard(t2, "Bandwidth-limited", str(r["ics_bw"]),
              f"{r['pixel_rate']/1e6:,.1f} MHz needed / {r['per_ic_bw']/1e6:,.0f} MHz per IC")
        mcard(t3, "Touch-limited", str(r["ics_touch"]),
              f"{r['touch_nodes']:,} nodes ({r['nx']}×{r['ny']}) / {r['per_ic_touch']:,} per IC")
        mcard(t4, "Recommended ICs", str(r["final_ics"]),
              "Worst-case across all three limits", border="#16a34a")

        st.caption(
            "Source channels = H-res × 3 (RGB). Pixel rate = H×V×FPS÷(1−blanking). "
            "Touch nodes = ceil(panel width/pitch) × ceil(panel height/pitch), derived from "
            "diagonal size and H:V aspect ratio. Each limit is rounded up to whole ICs "
            "independently, then the largest of the three is the recommended IC count.")
    else:
        st.info("Set the parameters above, then click **Calculate** to see results.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB – Display Case Study
# ══════════════════════════════════════════════════════════════════════════════
with tab_case_study:
    st.markdown('<h3 class="section-header">📋 Display Case Study — Video Path Analysis</h3>',
                unsafe_allow_html=True)
    st.markdown(
        "Loads design cases from **GMSL IVI Cases Study.xlsx**. "
        "Select a Case No. to analyse the full video path: "
        "**SOC → SER → GMSL Link → DES → Bridge IC → TDDI IC**. "
        "Each node's bandwidth is calculated and the bottleneck is highlighted in red.",
        unsafe_allow_html=False,
    )

    # ── Load Excel ─────────────────────────────────────────────────────────
    import os as _cs_os
    _CS_XLSX = _cs_os.path.join(_cs_os.path.dirname(__file__), "GMSL IVI Cases Study.xlsx")

    @st.cache_data(show_spinner=False)
    def _cs_load_cases(path):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        header = rows[0]
        cases = {}
        for row in rows[1:]:
            if row[0] is None:
                continue
            d = {header[i]: row[i] for i in range(len(header))}
            cases[int(row[0])] = d
        return cases

    try:
        _cs_cases = _cs_load_cases(_CS_XLSX)
    except Exception as _e_cs:
        st.error(f"Cannot load GMSL IVI Cases Study.xlsx: {_e_cs}")
        st.stop()

    # ── Sidebar-style settings panel ───────────────────────────────────────
    _cs_col_sel, _cs_col_main = st.columns([1, 3])

    with _cs_col_sel:
        st.markdown("#### ⚙️ Case Settings")
        _cs_case_num = st.selectbox(
            "Case No.",
            options=sorted(_cs_cases.keys()),
            format_func=lambda x: f"Case {x}",
            key="cs_case_num",
        )
        st.markdown("---")
        st.markdown("**Override / Options**")
        _cs_des_ports = st.radio("DES output ports", [1, 2], index=0, key="cs_des_ports",
                                 horizontal=True)
        _cs_bridge_rate = st.selectbox("Bridge IC data rate",
                                       ["HBR1 (3.24 Gbps)", "HBR2 (5.40 Gbps)", "HBR3 (8.10 Gbps)"],
                                       index=2, key="cs_bridge_rate")
        _cs_edp_rate = st.selectbox("TDDI eDP data rate (if eDP interface)",
                                    ["R324 — 3.24 Gbps", "R423 — 4.23 Gbps"],
                                    index=0, key="cs_edp_rate")
        _cs_run = st.button("🔄 Analyse", type="primary", key="cs_run_btn",
                            use_container_width=True)

    # ── Constants ──────────────────────────────────────────────────────────
    _CS_HBR1_GBPS  = 3.24       # effective (8b/10b encoded)
    _CS_HBR2_GBPS  = 5.40
    _CS_HBR3_GBPS  = 8.10
    _CS_GMSL_GBPS  = 9.7        # per link effective
    _CS_DP21_GBPS  = 20.0       # DP 2.1 UHBR20 single port effective; UHBR10 = 10 Gbps
    _CS_UHBR10     = 10.0
    _CS_UHBR20     = 20.0

    _bridge_gbps_map = {
        "HBR1 (3.24 Gbps)": _CS_HBR1_GBPS,
        "HBR2 (5.40 Gbps)": _CS_HBR2_GBPS,
        "HBR3 (8.10 Gbps)": _CS_HBR3_GBPS,
    }
    _edp_gbps_map = {
        "R324 — 3.24 Gbps": 3.24,
        "R423 — 4.23 Gbps": 4.23,
    }

    def _cs_parse_res(s):
        """Parse '6300x1740 (29.1")' → (6300, 1740, 29.1)"""
        import re
        m = re.match(r"(\d+)[xX×](\d+)\s*\(?([\d.]+)", str(s))
        if m:
            return int(m.group(1)), int(m.group(2)), float(m.group(3))
        return 0, 0, 0.0

    def _cs_parse_fps_bpp(s):
        """Parse '90Hz, 30bpp' → (90, 30)"""
        import re
        m = re.search(r"(\d+)\s*[Hh]z", str(s))
        fps = int(m.group(1)) if m else 60
        m2 = re.search(r"(\d+)\s*bpp", str(s))
        bpp = int(m2.group(1)) if m2 else 24
        return fps, bpp

    def _cs_raw_gbps(hres, vres, fps, bpp, blanking_pct):
        """Raw (uncompressed) video payload in Gbps."""
        total_px = (hres * vres) / (1 - blanking_pct / 100.0)
        return total_px * fps * bpp / 1e9

    def _cs_dsc_ratio(interface_str):
        """Return DSC compression ratio implied by pass-through or decompress flags."""
        s = str(interface_str).upper()
        if "3:1" in s:
            return 3.0
        if "4:1" in s:
            return 4.0
        if "2:1" in s or "2.5:1" in s:
            return 2.5 if "2.5" in s else 2.0
        return 3.0  # default DSC ratio when DSC is active but ratio not specified

    # ── Run analysis ───────────────────────────────────────────────────────
    if _cs_run or "cs_result" in st.session_state:
        if _cs_run:
            c = _cs_cases[_cs_case_num]

            # -- Parse display parameters --
            hres, vres, diag = _cs_parse_res(c.get("Resolution & Size", ""))
            fps, bpp = _cs_parse_fps_bpp(c.get("FPS & BPP", ""))
            blanking = float(c.get("Total Blanking Ratio (%)", 5.0) or 5.0) * 100  # col is 0.05 → 5%
            # Excel stores 0.05 for 5%; convert
            if blanking <= 1.0:
                blanking = blanking  # already fraction? no – it's 0.05 = 5%
            # Re-check: value 0.05 means 5%
            blanking_pct_val = float(c.get("Total Blanking Ratio (%)", 0.05) or 0.05)
            if blanking_pct_val < 1.0:
                blanking_pct_val *= 100  # convert 0.05 → 5.0

            raw_gbps = _cs_raw_gbps(hres, vres, fps, bpp, blanking_pct_val)

            # -- SOC output --
            soc_out_str = str(c.get("Video Output", "DP2.1, UHBR10"))
            if "UHBR20" in soc_out_str.upper():
                soc_gbps = _CS_UHBR20
            else:
                soc_gbps = _CS_UHBR10  # UHBR10 default for DP2.1

            # DSC at SOC?
            dsc_soc = str(c.get("DSC compressed by SOC", "No")).strip().upper() == "YES"
            dsc_ratio = _cs_dsc_ratio(soc_out_str) if dsc_soc else 1.0
            soc_payload = raw_gbps / dsc_ratio  # what actually leaves SOC

            # -- SER → GMSL Link --
            n_links = int(c.get("GMSL Links", 1) or 1)
            ser_gbps = _CS_HBR3_GBPS  # SER max (HBR3 input)
            gmsl_total = _CS_GMSL_GBPS * n_links
            gmsl_payload = soc_payload  # same payload traverses the link

            # -- DES --
            des_gbps_per_port = _CS_HBR3_GBPS  # DES max per output port
            des_ports = _cs_des_ports
            des_total = des_gbps_per_port * des_ports

            # DSC at DES?
            dsc_des_decomp = str(c.get("DSC decompressed by DES", "No")).strip().upper() == "YES"
            dsc_des_pass   = str(c.get("DSC pass-through by DES", "No")).strip().upper() == "YES"
            if dsc_des_decomp:
                des_out_payload = raw_gbps  # decompressed → full raw
            elif dsc_des_pass:
                des_out_payload = gmsl_payload  # still compressed
            else:
                des_out_payload = gmsl_payload

            # -- Bridge IC --
            bridge_name = str(c.get("Bridge IC", "N/A"))
            bridge_present = bridge_name.upper() not in ("N/A", "NONE", "")
            bridge_gbps_cap = _bridge_gbps_map[_cs_bridge_rate]

            dsc_bridge = str(c.get("DSC decompressed by Bridge IC", "No")).strip().upper() == "YES"
            if bridge_present:
                if dsc_bridge:
                    bridge_out = raw_gbps
                else:
                    bridge_out = des_out_payload
                bridge_cap = bridge_gbps_cap * des_ports  # one bridge per DES port
            else:
                bridge_out = des_out_payload
                bridge_cap = float("inf")

            # -- TDDI --
            tddi_iface = str(c.get("TDDI Interface", "LVDS")).strip().upper()
            tddi_name  = str(c.get("TDDI", "N/A")).strip()
            dsc_tddi   = str(c.get("DSC decompressed by TDDI", "No")).strip().upper() == "YES"

            edp_per_lane = _edp_gbps_map[_cs_edp_rate]

            if tddi_iface == "EDP":
                # eDP: 4 lanes, each at selected rate
                tddi_cap = edp_per_lane * 4
            elif tddi_iface == "LVDS":
                # LVDS: typically 4 pairs × 140 MHz × 7 bits = ~3.92 Gbps per IC
                tddi_cap = 140e6 * 7 * 4 / 1e9  # ≈ 3.92 Gbps per IC
            elif tddi_iface in ("MIPI", "DSI"):
                tddi_cap = 5.0  # typical MIPI DSI aggregate
            else:
                tddi_cap = _CS_HBR3_GBPS

            if dsc_tddi:
                tddi_in = raw_gbps  # TDDI receives decompressed
            else:
                tddi_in = bridge_out if bridge_present else des_out_payload

            # -- Build node list --
            nodes = [
                {"name": "SOC\n(DP 2.1)",
                 "cap": soc_gbps, "payload": soc_payload,
                 "detail": f"{soc_out_str}\n{'DSC ÷'+str(int(dsc_ratio)) if dsc_soc else 'No DSC'}\n{soc_gbps:.2f} Gbps port cap"},
                {"name": f"SER\n(HBR3 in)",
                 "cap": _CS_HBR3_GBPS, "payload": soc_payload,
                 "detail": f"Max {_CS_HBR3_GBPS:.2f} Gbps\nPayload → {soc_payload:.2f} Gbps"},
                {"name": f"GMSL Link\n({n_links}×9.7 Gbps)",
                 "cap": gmsl_total, "payload": gmsl_payload,
                 "detail": f"{n_links} link(s) × 9.7 Gbps = {gmsl_total:.1f} Gbps\nPayload {gmsl_payload:.2f} Gbps"},
                {"name": f"DES\n(HBR3 out × {des_ports})",
                 "cap": des_total, "payload": des_out_payload,
                 "detail": (f"Max {_CS_HBR3_GBPS:.2f} Gbps × {des_ports} port(s) = {des_total:.2f} Gbps\n"
                            f"{'Decompressed → ' if dsc_des_decomp else 'Pass-through → '}{des_out_payload:.2f} Gbps")},
            ]
            if bridge_present:
                nodes.append({
                    "name": f"Bridge IC\n({bridge_name[:12]})",
                    "cap": bridge_cap, "payload": bridge_out,
                    "detail": (f"{_cs_bridge_rate}\n"
                               f"Cap {bridge_gbps_cap:.2f} Gbps × {des_ports} = {bridge_cap:.2f} Gbps\n"
                               f"{'Decompress → ' if dsc_bridge else 'Pass-through → '}{bridge_out:.2f} Gbps"),
                })
            nodes.append({
                "name": f"TDDI IC\n({tddi_name[:14]})\n[{tddi_iface}]",
                "cap": tddi_cap, "payload": tddi_in,
                "detail": (f"Interface: {tddi_iface}\n"
                           f"Cap ≈ {tddi_cap:.2f} Gbps\n"
                           f"Input payload {tddi_in:.2f} Gbps"),
            })

            # -- Find bottleneck: node where payload > cap, or smallest headroom --
            margins = [nd["cap"] - nd["payload"] for nd in nodes]
            bottleneck_idx = int(min(range(len(margins)), key=lambda i: margins[i]))

            st.session_state["cs_result"] = dict(
                case_num=_cs_case_num,
                c=c, hres=hres, vres=vres, diag=diag,
                fps=fps, bpp=bpp, blanking_pct=blanking_pct_val,
                raw_gbps=raw_gbps, nodes=nodes,
                bottleneck_idx=bottleneck_idx,
                n_links=n_links, bridge_present=bridge_present,
                bridge_name=bridge_name, tddi_iface=tddi_iface, tddi_name=tddi_name,
            )

        # ── Render Results ─────────────────────────────────────────────────
        with _cs_col_main:
            if "cs_result" not in st.session_state:
                st.info("Click **Analyse** to run the calculation.")
                st.stop()

            _r = st.session_state["cs_result"]
            nodes = _r["nodes"]
            bottleneck_idx = _r["bottleneck_idx"]
            raw_gbps = _r["raw_gbps"]
            hres, vres = _r["hres"], _r["vres"]
            fps, bpp = _r["fps"], _r["bpp"]
            c_data = _r["c"]

            # ── 1. Summary metrics ─────────────────────────────────────────
            st.markdown(f"### Case {_r['case_num']} — {c_data.get('SOC','?')} · {c_data.get('Resolution & Size','?')}")
            _mc1, _mc2, _mc3, _mc4 = st.columns(4)
            mcard(_mc1, "Resolution", f"{hres}×{vres}", f"{_r['diag']}\" diagonal")
            mcard(_mc2, "Frame Rate / BPP", f"{fps} Hz / {bpp} bpp", f"Blanking {_r['blanking_pct']:.1f}%")
            mcard(_mc3, "Raw Video Payload", f"{raw_gbps:.2f} Gbps", "Uncompressed @ active+blanking")
            bott_node = nodes[bottleneck_idx]
            _over = bott_node['payload'] > bott_node['cap']
            mcard(_mc4, "⚠️ Bottleneck" if _over else "✅ Bottleneck (headroom)",
                  bott_node['name'].replace('\n', ' '),
                  f"Cap {bott_node['cap']:.2f} Gbps, Payload {bott_node['payload']:.2f} Gbps",
                  border="#dc2626" if _over else "#d97706")

            st.markdown("---")

            # ── 2. Block Diagram (Plotly) ──────────────────────────────────
            import plotly.graph_objects as _cs_go

            _N = len(nodes)
            _X_STEP = 2.2
            _xs = [i * _X_STEP for i in range(_N)]
            _y_node = 0.0
            _BOX_W = 1.8
            _BOX_H = 1.1

            fig_bd = _cs_go.Figure()

            # Arrow connectors between boxes
            for i in range(_N - 1):
                x0 = _xs[i] + _BOX_W / 2
                x1 = _xs[i+1] - _BOX_W / 2
                xm = (x0 + x1) / 2
                pay = nodes[i]["payload"]
                arrow_color = "#dc2626" if pay > nodes[i+1]["cap"] else "#374151"
                fig_bd.add_shape(type="line",
                    x0=x0, y0=0, x1=x1, y1=0,
                    line=dict(color=arrow_color, width=3),
                    layer="below")
                # Arrowhead triangle
                fig_bd.add_shape(type="path",
                    path=f"M {x1-0.15},{0.07} L {x1},{0} L {x1-0.15},{-0.07} Z",
                    fillcolor=arrow_color, line_color=arrow_color, layer="below")
                # Payload label on arrow
                fig_bd.add_annotation(
                    x=xm, y=0.28,
                    text=f"<b>{pay:.2f} Gbps</b>",
                    showarrow=False,
                    font=dict(size=13, color=arrow_color),
                    bgcolor="rgba(255,255,255,0.85)",
                    bordercolor=arrow_color,
                    borderwidth=1,
                )

            # Node boxes
            for i, nd in enumerate(nodes):
                _over_node = nd["payload"] > nd["cap"]
                _is_bott = (i == bottleneck_idx)
                box_color = "#fef2f2" if _is_bott else "#eff6ff"
                border_color = "#dc2626" if _is_bott else "#2563eb"
                bw = 2.5 if _is_bott else 1.5
                xc = _xs[i]
                # Box
                fig_bd.add_shape(type="rect",
                    x0=xc - _BOX_W/2, y0=_y_node - _BOX_H/2,
                    x1=xc + _BOX_W/2, y1=_y_node + _BOX_H/2,
                    fillcolor=box_color, line=dict(color=border_color, width=bw))
                # Node label
                name_label = nd["name"]
                fig_bd.add_annotation(
                    x=xc, y=0.18,
                    text=f"<b>{name_label.replace(chr(10),'<br>')}</b>",
                    showarrow=False,
                    font=dict(size=14, color="#1e293b"),
                    align="center",
                )
                # Capacity label
                cap_color = "#dc2626" if _over_node else "#16a34a"
                fig_bd.add_annotation(
                    x=xc, y=-0.25,
                    text=f"Cap: <b>{nd['cap']:.2f} Gbps</b>",
                    showarrow=False,
                    font=dict(size=12, color=cap_color),
                    align="center",
                )
                # Bottleneck badge
                if _is_bott:
                    fig_bd.add_annotation(
                        x=xc, y=_y_node + _BOX_H/2 + 0.18,
                        text="⚠️ BOTTLENECK",
                        showarrow=False,
                        font=dict(size=13, color="#dc2626", family="Arial Black"),
                        bgcolor="#fef2f2",
                        bordercolor="#dc2626",
                        borderwidth=1,
                    )

            _total_w = (_N - 1) * _X_STEP + _BOX_W + 0.4
            fig_bd.update_layout(
                height=320,
                margin=dict(l=20, r=20, t=50, b=20),
                title=dict(
                    text=f"Video Path Block Diagram — Case {_r['case_num']}",
                    font=dict(size=18, family="Arial"),
                    x=0.5,
                ),
                xaxis=dict(visible=False, range=[-_BOX_W/2-0.2, _total_w]),
                yaxis=dict(visible=False, range=[-0.9, 1.1]),
                plot_bgcolor="white",
                paper_bgcolor="white",
                showlegend=False,
            )
            st.plotly_chart(fig_bd, use_container_width=True)

            # ── 3. Bandwidth Bar Chart ─────────────────────────────────────
            _node_names = [nd["name"].replace("\n", "<br>") for nd in nodes]
            _caps   = [nd["cap"]     for nd in nodes]
            _pays   = [nd["payload"] for nd in nodes]
            _bar_colors = ["#dc2626" if i == bottleneck_idx else "#2563eb" for i in range(_N)]

            fig_bar = _cs_go.Figure()
            fig_bar.add_trace(_cs_go.Bar(
                name="Node Capacity (Gbps)",
                x=_node_names, y=_caps,
                marker_color=["#dc2626" if i == bottleneck_idx else "#93c5fd" for i in range(_N)],
                text=[f"{v:.2f}" for v in _caps],
                textposition="outside",
                textfont=dict(size=14),
                opacity=0.85,
            ))
            fig_bar.add_trace(_cs_go.Bar(
                name="Payload (Gbps)",
                x=_node_names, y=_pays,
                marker_color=["#fca5a5" if i == bottleneck_idx else "#1d4ed8" for i in range(_N)],
                text=[f"{v:.2f}" for v in _pays],
                textposition="outside",
                textfont=dict(size=14),
                opacity=0.9,
            ))

            # Raw video reference line
            fig_bar.add_hline(y=raw_gbps, line_dash="dash", line_color="#d97706",
                              annotation_text=f"Raw payload {raw_gbps:.2f} Gbps",
                              annotation_font=dict(size=13, color="#d97706"))

            fig_bar.update_layout(
                title=dict(text="Node Capacity vs. Payload", font=dict(size=17), x=0.5),
                barmode="group",
                height=420,
                margin=dict(l=40, r=40, t=60, b=80),
                legend=dict(font=dict(size=14), orientation="h", x=0.5, xanchor="center", y=-0.25),
                xaxis=dict(tickfont=dict(size=13)),
                yaxis=dict(title="Gbps", tickfont=dict(size=13), titlefont=dict(size=14)),
                plot_bgcolor="white",
                paper_bgcolor="white",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # ── 4. Detailed Node Table ─────────────────────────────────────
            st.markdown("#### Node-by-Node Analysis")
            _tbl_rows = []
            for i, nd in enumerate(nodes):
                margin = nd["cap"] - nd["payload"]
                status = "⚠️ OVER LIMIT" if margin < 0 else ("🔴 BOTTLENECK" if i == bottleneck_idx else "✅ OK")
                _tbl_rows.append({
                    "Node": nd["name"].replace("\n", " / "),
                    "Capacity (Gbps)": f"{nd['cap']:.2f}",
                    "Payload (Gbps)": f"{nd['payload']:.2f}",
                    "Headroom (Gbps)": f"{margin:+.2f}",
                    "Status": status,
                    "Detail": nd["detail"].replace("\n", " | "),
                })

            import pandas as _cs_pd
            _cs_df = _cs_pd.DataFrame(_tbl_rows)

            def _cs_style_row(row):
                styles = [""] * len(row)
                if "BOTTLENECK" in row["Status"] or "OVER" in row["Status"]:
                    styles = ["background-color:#fef2f2;color:#dc2626;font-weight:700"] * len(row)
                return styles

            _cs_styled = _cs_df.style.apply(_cs_style_row, axis=1).set_properties(**{
                "font-size": "15px", "padding": "8px 12px",
            }).hide(axis="index")

            st.dataframe(_cs_styled, use_container_width=True, height=300)

            # ── 5. Design Parameters Summary ──────────────────────────────
            st.markdown("#### Case Parameters from Excel")
            _param_cols = [
                ("SOC", "SOC"), ("Video Output", "Video Output"),
                ("DSC compressed by SOC", "DSC @ SOC"),
                ("GMSL Links", "GMSL Links"),
                ("DSC decompressed by DES", "DSC decomp @ DES"),
                ("DSC pass-through by DES", "DSC pass @ DES"),
                ("Bridge IC", "Bridge IC"),
                ("DSC decompressed by Bridge IC", "DSC decomp @ Bridge"),
                ("TDDI Interface", "TDDI Interface"),
                ("TDDI", "TDDI IC"),
                ("DSC decompressed by TDDI", "DSC decomp @ TDDI"),
            ]
            _param_html = '<table style="width:100%;border-collapse:collapse;font-size:15px">'
            _param_html += '<tr style="background:#1e40af;color:white">'
            for _, col_label in _param_cols:
                _param_html += f'<th style="padding:8px 12px;text-align:left">{col_label}</th>'
            _param_html += "</tr>"
            _param_html += '<tr style="background:#f0f9ff">'
            for col_key, _ in _param_cols:
                val = str(c_data.get(col_key, "—") or "—")
                _param_html += f'<td style="padding:8px 12px;border-bottom:1px solid #e2e8f0">{val}</td>'
            _param_html += "</tr></table>"
            st.markdown(_param_html, unsafe_allow_html=True)

    else:
        with _cs_col_main:
            st.info("👈 Select a **Case No.** on the left and click **Analyse** to begin.")

