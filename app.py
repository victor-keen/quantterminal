import streamlit as st
import sys
import os
import io
import contextlib
import re
import matplotlib.pyplot as plt
import builtins

# Ensure UTF-8 output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import special

st.set_page_config(
    page_title="Elite Quantitative Terminal",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enforce Monospace Terminal Styling & Alignment
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .terminal-screen {
        background-color: #0d1117;
        border: 2px solid #30363d;
        border-radius: 6px;
        padding: 1rem;
        font-family: 'Courier New', Courier, monospace !important;
        color: #58a6ff;
        font-size: 13px;
        line-height: 1.25;
        white-space: pre !important;
        overflow-x: auto !important;
        min-height: 380px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    .stTextInput input {
        background-color: #161b22 !important;
        color: #39d353 !important;
        border: 1px solid #30363d !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #238636;
        color: #ffffff;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #2ea043;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "input_queue" not in st.session_state:
    st.session_state["input_queue"] = []

# Sidebar Module Selection
MODULE_DISPATCH = special.get_module_dispatch()

# Full Names Mapping for ALL 68 Modules
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
    "66": "OpenRouter AI Market Analyst Chat",
    "67": "Workflow Scanner & Automation Engine",
    "68": "Multi-Strategy Backtester & Optimizer",
    "69": "Multi-Strategy Quant Arena",
    "70": "Options Greeks Strategy Recommender",
    "71": "Markdown Task Executor & Journal",
    "73": "Prediction Market Oracle (Polymarket/Kalshi)",
    "74": "Swing Trading Setup Oracle",
    "75": "Deep-Value Drawdown Scanner",
}

st.sidebar.title("⚡ Quant Controls")
ticker = st.sidebar.text_input("🎯 Stock Ticker", value="RELIANCE.NS").strip().upper()

selected_module = st.sidebar.selectbox(
    "⚡ Select Module to Launch",
    options=list(MODULE_DISPATCH.keys()),
    format_func=lambda x: f"[{x}] {MODULE_NAMES.get(x, 'Module ' + str(x))}"
)

# TOP CONTROL BAR (Zero Scrolling Required!)
st.title("💻 Elite Terminal Console")

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    cmd_input = st.text_input("⌨️ Terminal Command Input (e.g. F, R, 2, 14, 0)", key="top_cmd_input", placeholder="Type key or choice here...")

with col2:
    st.write("")
    st.write("")
    send_cmd = st.button("⏎ Send Command")

with col3:
    st.write("")
    st.write("")
    reset_btn = st.button("🔄 Clear Output")

if reset_btn:
    st.session_state["input_queue"] = []
    st.rerun()

if send_cmd and cmd_input.strip():
    st.session_state["input_queue"].append(cmd_input.strip())

def sanitize_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# Execute Module Run
def run_live_terminal():
    mod_fn = MODULE_DISPATCH[selected_module]
    output_buffer = io.StringIO()
    plt.close('all')

    queue = list(st.session_state["input_queue"])
    queue_extended = list(queue) + ["0", "0", "0", "0", "0"]

    def mocked_input(prompt=""):
        if queue_extended:
            return queue_extended.pop(0)
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

    raw_output = output_buffer.getvalue()
    clean_output = sanitize_ansi(raw_output)

    # Render Screen Output right below top controls (No Scrolling!)
    st.markdown(f'<div class="terminal-screen">{clean_output}</div>', unsafe_allow_html=True)

    # Render Charts below terminal output
    figs = [plt.figure(i) for i in plt.get_fignums()]
    if figs:
        st.subheader("📊 Generated Charts")
        for fig in figs:
            st.pyplot(fig)
        plt.close('all')

run_live_terminal()
