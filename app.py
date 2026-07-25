import streamlit as st
import sys
import os
import io
import contextlib
import re
import time
import matplotlib.pyplot as plt
import builtins
import html as html_mod
import requests

# Ensure UTF-8 output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import special

# ── Completely block any AI network requests (OpenRouter API) ──
_real_requests_post = requests.post
_real_requests_get = requests.get

def _blocked_requests_post(url, *args, **kwargs):
    class FakeResponse:
        status_code = 200
        def json(self):
            return {"choices": [{"message": {"content": ""}}]}
        @property
        def text(self):
            return ""
    return FakeResponse()

def _blocked_requests_get(url, *args, **kwargs):
    class FakeGetResponse:
        status_code = 200
        def json(self):
            return {"data": []}
        @property
        def text(self):
            return '{"data": []}'
    return FakeGetResponse()

requests.post = _blocked_requests_post
requests.get = _blocked_requests_get

def _bypassed_ai_call(self, *args, **kwargs):
    return ("", 0.0)

# Patch AI calls in special.py classes if they exist
for attr in dir(special):
    obj = getattr(special, attr)
    if isinstance(obj, type):
        if hasattr(obj, "_ai_call"):
            setattr(obj, "_ai_call", _bypassed_ai_call)
        if hasattr(obj, "run_ai_fundamental_analysis"):
            setattr(obj, "run_ai_fundamental_analysis", lambda self: "")
        if hasattr(obj, "run_ai_trade_setup"):
            setattr(obj, "run_ai_trade_setup", lambda self: "")

# ── Patch rich.prompt.Prompt.ask so it reads from our mocked builtins.input ──
try:
    from rich.prompt import Prompt as _RichPrompt

    @classmethod
    def _patched_ask(cls, prompt="", **kwargs):
        p_str = str(prompt).lower()
        if "ai" in p_str or "copilot" in p_str or "chat" in p_str:
            return "N"
        try:
            return builtins.input(str(prompt) + ": ")
        except EOFError:
            return kwargs.get("default", "0")

    _RichPrompt.ask = _patched_ask
except ImportError:
    pass

# ── Patch yfinance with retry-on-rate-limit ──
import yfinance as yf
_real_yf_download = yf.download.__wrapped__ if hasattr(yf.download, '__wrapped__') else special._ORIG_DOWNLOAD

def _retry_download(tickers, *args, **kwargs):
    for attempt in range(3):
        try:
            result = _real_yf_download(tickers, *args, **kwargs)
            if result is not None and not result.empty:
                return result
        except Exception as e:
            if "Too Many Requests" in str(e) or "Rate" in str(e):
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    return _real_yf_download(tickers, *args, **kwargs)

yf.download = _retry_download

st.set_page_config(
    page_title="Elite Quantitative Terminal",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS: Edge-to-edge full width terminal + bottom input ──
st.markdown("""
<style>
    /* Full width container overrides */
    .stMainBlockContainer {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .terminal-output {
        background-color: #0b0e14;
        border: 1px solid #30363d;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 1.2rem;
        font-family: 'Consolas', 'Courier New', monospace !important;
        color: #58a6ff;
        font-size: 13.5px;
        line-height: 1.35;
        white-space: pre !important;
        overflow-x: auto !important;
        overflow-y: auto !important;
        min-height: 450px;
        max-height: 72vh;
        width: 100% !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
    }
    .prompt-bar {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 0 0 8px 8px;
        padding: 0.6rem 1rem;
        font-family: 'Consolas', 'Courier New', monospace;
        color: #39d353;
        font-size: 13px;
        margin-bottom: 1rem;
        width: 100% !important;
    }
    .stTextInput input {
        background-color: #0d1117 !important;
        color: #39d353 !important;
        border: 1px solid #30363d !important;
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-weight: bold;
        font-size: 14px !important;
    }
    .stButton>button {
        background-color: #238636;
        color: #ffffff;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.2rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2ea043;
    }
    img {
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: crisp-edges !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Global Matplotlib config ──
plt.style.use('dark_background')
plt.rcParams['figure.dpi'] = 200
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['font.size'] = 10
plt.rcParams['figure.facecolor'] = '#0d1117'
plt.rcParams['axes.facecolor'] = '#161b22'
plt.rcParams['grid.color'] = '#21262d'
plt.rcParams['text.color'] = '#e6edf3'
plt.rcParams['axes.labelcolor'] = '#58a6ff'
plt.rcParams['xtick.color'] = '#8b949e'
plt.rcParams['ytick.color'] = '#8b949e'

# ── Session State Init ──
if "terminal_log" not in st.session_state:
    st.session_state["terminal_log"] = ""
if "pending_cmds" not in st.session_state:
    st.session_state["pending_cmds"] = []
if "stored_figs" not in st.session_state:
    st.session_state["stored_figs"] = []
if "last_module" not in st.session_state:
    st.session_state["last_module"] = None
if "last_ticker" not in st.session_state:
    st.session_state["last_ticker"] = None
if "needs_run" not in st.session_state:
    st.session_state["needs_run"] = True

# ── Module dispatch & names ──
MODULE_DISPATCH = special.get_module_dispatch()
MODULE_NAMES = {
    "1": "Technical Indicators Hub",
    "2": "Master Charting Engine",
    "3": "Historical Price & Volatility Analysis",
    "4": "Multi-Indicator Comparison Engine",
    "5": "Pro Technical Analysis & Signals",
    "6": "Merton Jump-Diffusion Monte Carlo",
    "7": "XGBoost Signal Classifier",
    "8": "Institutional Order Flow Engine",
    "9": "ML Price Forecast & Ensemble",
    "10": "ARIMA + LSTM Meta Predictor",
    "11": "Fundamental Health & Ratios",
    "12": "Financial Statements Explorer",
    "13": "Financial Statement Visualizer",
    "14": "DuPont 5-Way Analysis",
    "15": "Forensic Accounting & Beneish M-Score",
    "16": "Statement Trend & Variance Analyzer",
    "17": "Company Profiler & Competitor Matrix",
    "18": "Institutional DCF Valuation Model",
    "19": "Institutional LBO Valuation Model",
    "20": "4-Year Historical Financials",
    "21": "Groww Live Intraday Tracker",
    "22": "Comprehensive Risk Assessment Engine",
    "23": "Rolling Risk & Drawdown Dynamics",
    "24": "GARCH Volatility Modeling",
    "25": "Market Regime Detection Engine",
    "26": "Volatility Trading & Hedging Framework",
    "27": "Pairs Trading & Cointegration",
    "28": "Fama-French Factor Model",
    "29": "Efficient Frontier & Markowitz Optimization",
    "30": "Mean Reversion & Stat-Arb Backtester",
    "31": "Advanced Monte Carlo Simulation",
    "32": "Options Chain & Black-Scholes Engine",
    "33": "Options Greeks Matrix",
    "34": "Google News Sentiment Analysis",
    "35": "Sector & Industry Performance Matrix",
    "36": "Advanced Options Greeks & Vol Surface",
    "37": "News & Market Events Hub",
    "38": "Global Macro & Intermarket Dashboard",
    "39": "Shareholding & Insider Scraper",
    "40": "Dividend Scanner & Yield Screener",
    "41": "Large Deals & Block Deals Scanner",
    "42": "External Terminal & Script Launcher",
    "43": "Financial Documents Hub",
    "44": "Finshots Daily Reader",
    "45": "NBFC & Banking News Scanner",
    "46": "LiveMint News Intelligence Scraper",
    "47": "Bloomberg Latest Headlines",
    "48": "Statistical Arbitrage & Cointegration",
    "49": "Trading Bible & Book Terminal",
    "50": "EPUB Book Reader",
    "51": "Wikipedia Finance Intelligence Scraper",
    "52": "Predictive Stochastic Engine",
    "53": "Terminal Dashboard & Snapshot",
    "54": "Alpha Autoencoder (Deep Factor)",
    "55": "Hybrid GARCH-LSTM Volatility Model",
    "56": "Transformer Quant (Multi-Head Self-Attention)",
    "57": "Quantum Portfolio Optimizer (QAOA)",
    "58": "Federated Swarm Intelligence Trader",
    "59": "Neural ODE Continuous-Time Quant",
    "60": "Asset Graph & Microstructure Network",
    "61": "Reinforcement Learning Agent (PPO/DQN)",
    "62": "Regime HMM (Hidden Markov Model)",
    "63": "Risk vs Return Markowitz Analyzer",
    "64": "Three-Statement Integrated Linker Model",
    "65": "New & Trending Companies / IPOs",
    "66": "OpenRouter Market Analyst Chat",
    "67": "Workflow Scanner & Automation Engine",
    "68": "Multi-Strategy Backtester & Optimizer",
    "69": "Multi-Strategy Quant Arena",
    "70": "Options Greeks Strategy Recommender",
    "71": "Markdown Task Executor & Journal",
    "73": "Prediction Market Oracle (Polymarket/Kalshi)",
    "74": "Swing Trading Setup Oracle",
    "75": "Deep-Value Drawdown Scanner",
}

def sanitize_ansi(text):
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)

def strip_rich_markup(text):
    """Remove rich markup tags like [dim], [bold], [/], [green], etc."""
    return re.sub(r'\[/?[a-zA-Z0-9_ #.,;:!-]*\]', '', text)

# ── Sidebar Controls ──
st.sidebar.title("⚡ Quant Controls")
ticker = st.sidebar.text_input("🎯 Stock Ticker", value="RELIANCE.NS").strip().upper()
selected_module = st.sidebar.selectbox(
    "⚡ Select Module to Launch",
    options=list(MODULE_DISPATCH.keys()),
    format_func=lambda x: f"[{x}] {MODULE_NAMES.get(x, 'Module ' + str(x))}"
)

# Detect module/ticker switch → clear terminal
if st.session_state["last_module"] != selected_module or st.session_state["last_ticker"] != ticker:
    st.session_state["terminal_log"] = ""
    st.session_state["stored_figs"] = []
    st.session_state["pending_cmds"] = []
    st.session_state["last_module"] = selected_module
    st.session_state["last_ticker"] = ticker
    st.session_state["needs_run"] = True

# ── Execute module (only when needed) ──
def execute_module():
    mod_fn = MODULE_DISPATCH[selected_module]
    output_buffer = io.StringIO()
    plt.close('all')

    cmds = list(st.session_state["pending_cmds"])
    feed = list(cmds) + ["0"]

    def mocked_input(prompt=""):
        p_str = str(prompt).lower()
        if "ai" in p_str or "copilot" in p_str or "chat" in p_str:
            return "N"
        if feed:
            ans = feed.pop(0)
            output_buffer.write(f"{prompt}{ans}\n")
            return ans
        return "0"

    orig_input = builtins.input
    builtins.input = mocked_input
    special._CLI_BATCH_MODE = True

    try:
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            mod_fn(ticker)
    except SystemExit:
        pass
    except Exception as e:
        output_buffer.write(f"\n[Terminal Error]: {e}\n")
    finally:
        builtins.input = orig_input
        special._CLI_BATCH_MODE = False

    raw_text = output_buffer.getvalue()
    new_text = strip_rich_markup(sanitize_ansi(raw_text))

    # Append new output to the rolling log
    if cmds:
        separator = f"\n{'─'*70}\n▶ Command: {', '.join(cmds)}\n{'─'*70}\n"
        st.session_state["terminal_log"] += separator + new_text
    else:
        st.session_state["terminal_log"] += new_text

    # Capture figures as PNG bytes
    figs = [plt.figure(i) for i in plt.get_fignums()]
    for fig in figs:
        try:
            fig.tight_layout()
        except Exception:
            pass
        png_io = io.BytesIO()
        fig.savefig(png_io, format='png', bbox_inches='tight', facecolor='#0d1117')
        png_io.seek(0)
        st.session_state["stored_figs"].append(png_io.getvalue())
    plt.close('all')

    st.session_state["pending_cmds"] = []
    st.session_state["needs_run"] = False

# Run if needed
if st.session_state["needs_run"]:
    execute_module()

# ══════════════════════════════════════════════════════
# RENDER: Single continuous display
# ══════════════════════════════════════════════════════

st.title("💻 Elite Terminal Console")

# ── Terminal Output (scrollable, full-width) ──
escaped_log = html_mod.escape(st.session_state["terminal_log"])
st.markdown(f'''
<div id="term-out" class="terminal-output">{escaped_log}</div>
<script>
    var el = document.getElementById("term-out");
    if (el) {{ el.scrollTop = el.scrollHeight; }}
</script>
''', unsafe_allow_html=True)

# ── Command Input Bar (directly under terminal window) ──
st.markdown('<div class="prompt-bar">⌨️  Enter command below and press Enter:</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([5, 1, 1])

with col1:
    cmd_input = st.text_input(
        "cmd", key="cmd_box",
        placeholder="Type command (e.g. F, R, 2, 14, 0) ...",
        label_visibility="collapsed"
    )

with col2:
    send_btn = st.button("⏎ Send")

with col3:
    clear_btn = st.button("🔄 Clear")

# ── Charts (rendered inline below terminal and controls) ──
if st.session_state["stored_figs"]:
    st.markdown("---")
    for idx, png_bytes in enumerate(st.session_state["stored_figs"], 1):
        with st.expander(f"📊 Chart #{idx}", expanded=True):
            st.image(png_bytes, width="stretch")

# Handle button actions
if clear_btn:
    st.session_state["terminal_log"] = ""
    st.session_state["stored_figs"] = []
    st.session_state["pending_cmds"] = []
    st.session_state["needs_run"] = True
    st.rerun()

if send_btn and cmd_input.strip():
    raw_cmds = [c.strip() for c in cmd_input.split(",") if c.strip()]
    st.session_state["pending_cmds"] = raw_cmds
    st.session_state["needs_run"] = True
    st.rerun()
