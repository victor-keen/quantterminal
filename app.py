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

# Dark Terminal CSS Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .terminal-screen {
        background-color: #161b22;
        border: 2px solid #30363d;
        border-radius: 8px;
        padding: 1.5rem;
        font-family: 'Consolas', 'Courier New', monospace;
        color: #58a6ff;
        font-size: 14px;
        line-height: 1.5;
        white-space: pre-wrap;
        overflow-x: auto;
        min-height: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .stTextInput input {
        background-color: #161b22 !important;
        color: #39d353 !important;
        border: 1px solid #30363d !important;
        font-family: 'Consolas', 'Courier New', monospace !important;
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

# Initialize Terminal State
if "history" not in st.session_state:
    st.session_state["history"] = []
if "input_queue" not in st.session_state:
    st.session_state["input_queue"] = []
if "current_module" not in st.session_state:
    st.session_state["current_module"] = None

# Sidebar Controls
st.sidebar.title("💻 Live Web Terminal")
st.sidebar.markdown("---")

ticker = st.sidebar.text_input("🎯 Active Ticker", value="RELIANCE.NS").strip().upper()

# Module Categorization
MODULE_DISPATCH = special.get_module_dispatch()
MODULE_NAMES = {
    "1": "Technical Indicators Hub",
    "2": "Master Charting Engine",
    "3": "Historical Price & Volatility",
    "4": "Multi-Indicator Comparison",
    "5": "Pro Technical Analysis & Signals",
    "6": "Merton Jump-Diffusion Monte Carlo",
    "7": "XGBoost Signal Classifier",
    "8": "Institutional Order Flow Engine",
    "11": "Fundamental Health & Ratios",
    "12": "Financial Statements Explorer",
    "18": "Institutional DCF Model",
    "19": "Institutional LBO Model",
    "22": "Risk Assessment Engine",
    "24": "GARCH Volatility Modeling",
    "29": "Efficient Frontier Optimization",
    "32": "Options Chain & Black-Scholes",
    "49": "Trading Bible & Book Terminal",
    "50": "EPUB Book Reader",
    "63": "Risk vs Return Markowitz",
    "68": "Multi-Strategy Optimizer",
    "75": "Deep-Value Drawdown Scanner",
}

selected_module = st.sidebar.selectbox(
    "⚡ Select Module to Launch",
    options=list(MODULE_DISPATCH.keys()),
    format_func=lambda x: f"[{x}] {MODULE_NAMES.get(x, 'Module ' + str(x))}"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💬 Interactive Terminal Command Input")

cmd_input = st.sidebar.text_input("Enter Key / Choice (e.g. F, R, 2, 14, 0)", key="terminal_input_key")
send_cmd = st.sidebar.button("⏎ Send Command to Terminal")
reset_btn = st.sidebar.button("🔄 Reset Terminal Output")

if reset_btn:
    st.session_state["history"] = []
    st.session_state["input_queue"] = []
    st.rerun()

st.title("💻 Interactive Quant Terminal")
st.caption(f"Running Module [{selected_module}] for `{ticker}` | Interactive Live Console")
st.markdown("---")

def sanitize_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# Manage Command Submission
if send_cmd and cmd_input.strip():
    st.session_state["input_queue"].append(cmd_input.strip())

# Execute Module Run with Captured Live State
def run_live_terminal():
    mod_fn = MODULE_DISPATCH[selected_module]
    output_buffer = io.StringIO()
    plt.close('all')

    queue = list(st.session_state["input_queue"])
    
    # Fill remaining inputs with 0 to safely complete execution loop without hangs
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

    # Render Terminal Output Screen
    st.subheader("🖥️ Interactive Terminal Output")
    st.markdown(f'<div class="terminal-screen">{clean_output}</div>', unsafe_allow_html=True)

    # Render Matplotlib Plots if any were generated by the command
    figs = [plt.figure(i) for i in plt.get_fignums()]
    if figs:
        st.subheader("📊 Generated Charts & Graphics")
        for fig in figs:
            st.pyplot(fig)
        plt.close('all')

run_live_terminal()
