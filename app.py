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

# Import special module engine
import special

st.set_page_config(
    page_title="Elite Quant & Financial Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark terminal styling
st.markdown("""
<style>
    .main {
        background-color: #0d1117;
        color: #e6edf3;
    }
    .stSelectbox label, .stTextInput label, .stSlider label {
        color: #58a6ff !important;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #21262d;
        color: #58a6ff;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 0.4rem 1rem;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #30363d;
        color: #79c0ff;
        border-color: #8b949e;
    }
    .terminal-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.2rem;
        font-family: 'Courier New', Courier, monospace;
        color: #e6edf3;
        overflow-x: auto;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# Module Categorization
MODULE_CATEGORIES = {
    "📈 Technical Analysis & Charts": {
        "1": "Technical Indicators Hub",
        "2": "Master Charting Engine",
        "3": "Historical Price & Volatility Analysis",
        "4": "Multi-Indicator Comparison Engine",
        "5": "Pro Technical Analysis & Signals",
        "8": "Institutional Order Flow Engine",
        "21": "Groww / Live Intraday Tracker",
        "53": "Terminal Dashboard & Snapshot",
    },
    "🤖 AI & Machine Learning Quant": {
        "6": "Monte Carlo & Merton Jump Diffusion",
        "7": "XGBoost Signal Classifier",
        "9": "ML Price Forecast & Ensemble",
        "10": "ARIMA + LSTM Meta Predictor",
        "52": "Predictive Stochastic Engine",
        "54": "Alpha Autoencoder (Deep Factor)",
        "55": "Hybrid GARCH-LSTM Volatility Forecasting",
        "56": "Transformer Quant (Multi-Head Self-Attention)",
        "57": "Quantum Portfolio Optimizer (QAOA Simulator)",
        "58": "Federated Swarm Intelligence Trader",
        "59": "Neural ODE Continuous-Time Quant",
        "61": "Reinforcement Learning Agent (PPO/DQN)",
        "62": "Regime HMM (Hidden Markov Model)",
        "66": "OpenRouter AI Market Analyst Chat",
    },
    "💼 Fundamental & Valuation": {
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
        "39": "Shareholding & Insider Scraper",
        "64": "Three-Statement Integrated Linker Model",
    },
    "⚖️ Risk, Portfolio & Quant Strategies": {
        "22": "Comprehensive Risk Assessment",
        "23": "Rolling Risk & Drawdown Dynamics",
        "24": "GARCH Volatility Modeling",
        "25": "Market Regime Detection Engine",
        "26": "Volatility Trading & Hedging Framework",
        "27": "Pairs Trading & Cointegration",
        "28": "Fama-French Factor Model",
        "29": "Efficient Frontier & Markowitz Optimization",
        "30": "Mean Reversion & Stat-Arb Backtester",
        "31": "Advanced Monte Carlo Simulation",
        "48": "Statistical Arbitrage & Cointegration Engine",
        "60": "Asset Graph & Market Microstructure Network",
        "63": "Risk vs Return Markowitz Analyzer",
        "67": "Workflow Scanner & Automation Engine",
        "68": "Multi-Strategy Backtester & Strategy Optimizer",
        "69": "Multi-Strategy Quant Arena",
        "75": "Deep-Value Drawdown Scanner",
    },
    "📊 Options & Derivatives": {
        "32": "Options Chain & Black-Scholes Engine",
        "33": "Options Greeks Matrix",
        "36": "Advanced Options Greeks & Volatility Surface",
        "70": "Options Greeks & Strategy Recommender",
    },
    "📰 News, Sentiment & Market Intel": {
        "34": "Google News Sentiment Analysis",
        "35": "Sector & Industry Performance Matrix",
        "37": "News & Market Events Hub",
        "38": "Global Macro & Intermarket Dashboard",
        "40": "Dividend Scanner & Yield Screener",
        "41": "Large Deals & Block Deals Scanner",
        "44": "Finshots Daily Financial Reader",
        "45": "NBFC & Banking News Scanner",
        "46": "LiveMint News Intelligence Scraper",
        "47": "Bloomberg Latest Headlines",
        "65": "New & Trending Companies / IPOs",
        "73": "Prediction Market Oracle (Polymarket/Kalshi)",
        "74": "Swing Trading Setup Oracle",
    },
    "📚 Document Readers & Utilities": {
        "42": "External Terminal & Script Launcher",
        "43": "Financial Documents Hub",
        "49": "Trading Bible & Book Terminal",
        "50": "EPUB Book Reader",
        "51": "Wikipedia Finance Intelligence Scraper",
        "71": "Markdown Task Executor & Automated Trading Journal",
    }
}

# Extensive Sub-Option Mappings for Multi-Layered Modules
MODULE_SUBOPTIONS = {
    "1": {
        "ALL": "Run Full Technical Suite",
        "RSI": "RSI Analysis",
        "MACD": "MACD Analysis",
        "BB": "Bollinger Bands",
        "EMA": "Moving Averages (EMA/SMA)",
    },
    "2": {
        "14": "Full 14-Panel Master Dashboard",
        "1": "Candlestick + SMA/EMA + Supertrend",
        "2": "Heikin-Ashi Candles",
        "3": "Bollinger Bands + Keltner Channels",
        "4": "RSI-14 (with Divergence)",
        "5": "MACD (12,26,9) + Histogram",
        "6": "Volume + OBV + CMF",
        "7": "Stochastic %K/%D",
        "8": "ATR + Historical Volatility",
        "9": "ADX-14 + DI",
        "10": "CCI-20",
        "11": "P/E Ratio + Relative Strength",
        "12": "Classic Pivot Points",
        "13": "Williams %R + MFI",
    },
    "5": {
        "1": "Full Pro Analysis Report",
        "2": "Signals Only",
        "3": "Support & Resistance Levels",
    },
    "8": {
        "1": "Footprint Tape",
        "2": "Volume Profile + DOM",
        "3": "Signal Panel",
        "4": "VWAP Bands Table",
        "5": "AI Trade Setup Brief",
    },
    "12": {
        "1": "Income Statement",
        "2": "Balance Sheet",
        "3": "Cash Flow Statement",
        "4": "Key Financial Ratios",
    },
    "22": {
        "1": "Full Risk Assessment",
        "2": "Value at Risk (VaR)",
        "3": "Stress Testing",
    },
    "26": {
        "1": "Volatility Surface & Hedging",
        "2": "Straddle/Strangle Simulator",
    },
    "32": {
        "1": "Black-Scholes Options Pricing",
        "2": "Implied Volatility Surface",
        "3": "Options Strategy Payoff",
    },
    "43": {
        "1": "View Document Catalog",
        "2": "Read Financial Summary",
    },
    "49": {
        "1": "View Trading Rules",
        "2": "Psychology & Risk Guidelines",
    },
    "50": {
        "1": "List Available Books",
        "2": "Read Chapter Excerpt",
    },
    "68": {
        "1": "Run Strategy Backtest",
        "2": "Optimize Strategy Parameters",
    },
    "69": {
        "1": "Multi-Strategy Arena Comparison",
        "2": "Leaderboard Rankings",
    },
    "74": {
        "1": "Swing Setup Oracle Report",
        "2": "Risk/Reward Invalidation Levels",
    },
    "75": {
        "1": "Highest Weekly Dips (1W)",
        "2": "Highest Monthly Dips (1M)",
        "3": "Highest Quarterly Dips (1Q)",
        "4": "Highest Yearly Dips (1Y)",
        "5": "Max Drawdown Drop",
    }
}

# Sidebar UI
st.sidebar.title("⚡ Elite Quant Engine")
st.sidebar.markdown("---")

ticker = st.sidebar.text_input("🎯 Stock Ticker (NSE / US)", value="RELIANCE.NS").strip().upper()
if not ticker:
    ticker = "RELIANCE.NS"

st.sidebar.markdown("### 🧭 Navigation & Modules")

category = st.sidebar.selectbox("Select Category", list(MODULE_CATEGORIES.keys()))
modules_in_cat = MODULE_CATEGORIES[category]

module_id = st.sidebar.selectbox(
    "Select Analysis Module",
    options=list(modules_in_cat.keys()),
    format_func=lambda x: f"Mod {x}: {modules_in_cat[x]}"
)

sub_choice = None
if module_id in MODULE_SUBOPTIONS:
    sub_opts = MODULE_SUBOPTIONS[module_id]
    sub_choice = st.sidebar.selectbox(
        "Select Layer / Sub-Option",
        options=list(sub_opts.keys()),
        format_func=lambda x: sub_opts[x]
    )

run_button = st.sidebar.button("🚀 Run Analysis Module")

st.sidebar.markdown("---")
st.sidebar.caption("Deployable on Streamlit Community Cloud (Free Tier)")

# Main Header
st.title("📈 Elite Quantitative & Institutional Financial Terminal")
st.markdown(f"**Active Ticker:** `{ticker}` | **Selected Module:** `[{module_id}] {modules_in_cat[module_id]}`")
st.markdown("---")

def sanitize_ansi(text):
    """Remove ANSI color escape sequences from captured terminal outputs."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def capture_and_run_module(mod_id, tkr, sub_opt=None):
    dispatch = special.get_module_dispatch()
    if mod_id not in dispatch:
        st.error(f"Module {mod_id} is not registered in dispatch dictionary.")
        return

    mod_fn = dispatch[mod_id]

    output_buffer = io.StringIO()
    plt.close('all')

    # Smart Input Queue:
    # 1. First choice: User selected sub-option (if applicable)
    # 2. Second choice: Default confirmation / enter
    # 3. Third choice: "0" to exit nested interactive menus cleanly
    orig_input = builtins.input
    input_queue = [sub_opt, "1", "0", "0", "0"] if sub_opt else ["1", "0", "0", "0"]

    def mocked_input(prompt=""):
        if input_queue:
            return input_queue.pop(0)
        return "0"

    builtins.input = mocked_input
    special._CLI_BATCH_MODE = True

    with st.spinner(f"Processing Module {mod_id} for {tkr}..."):
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                res = mod_fn(tkr)
        except SystemExit:
            pass
        except Exception as e:
            st.error(f"An error occurred while executing module {mod_id}: {e}")
        finally:
            builtins.input = orig_input
            special._CLI_BATCH_MODE = False

    raw_output = output_buffer.getvalue()
    clean_output = sanitize_ansi(raw_output)

    # Render matplotlib figures if any were generated
    figs = [plt.figure(i) for i in plt.get_fignums()]
    if figs:
        st.subheader("📊 Graphical Output & Charts")
        for fig in figs:
            st.pyplot(fig)
        plt.close('all')

    # Render text/terminal logs
    if clean_output.strip():
        st.subheader("📋 Output & Analysis Results")
        st.markdown(f'<div class="terminal-box">{clean_output}</div>', unsafe_allow_html=True)
    elif not figs:
        st.info("Module completed execution with no text or graphical output returned.")

if run_button or st.session_state.get("auto_run", False):
    st.session_state["auto_run"] = False
    capture_and_run_module(module_id, ticker, sub_choice)
else:
    st.markdown("""
    ### Welcome to the Elite Quant Terminal Web App! 👋
    
    This app converts all **68 Quantitative, Technical, Fundamental, Machine Learning, and Risk Modules** from `special.py` into a web dashboard.
    
    #### How to use:
    1. Enter any ticker symbol in the left sidebar (e.g. `RELIANCE.NS`, `TCS.NS`, `AAPL`, `TSLA`, `NVDA`).
    2. Choose a module category and select your desired module.
    3. If the module has sub-layers or options, select your desired layer.
    4. Click **🚀 Run Analysis Module** to view full outputs, metrics, and matplotlib graphs right inside your browser!
    """)
