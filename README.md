# 🚀 Deployment Guide: GitHub & Streamlit Community Cloud (Free)

you can access the live app at https://quantterminal-king.streamlit.app/

This guide walks you through uploading your stock analyzer Streamlit app to GitHub and deploying it on **Streamlit Community Cloud** completely for free.

---

## 🛠️ Step 1: Initialize Git and Commit Your Project

Open your terminal in `c:\Users\keenv\Downloads\streamlit` and run:

```bash
# Initialize git repo
git init

# Add all files (app.py, special.py, requirements.txt, .streamlit/config.toml, etc.)
git add .

# Commit changes
git commit -m "Initial commit of Streamlit Quant Engine App"
```

---

## 🐙 Step 2: Push to GitHub

1. Go to [GitHub](https://github.com/new) and create a **New Repository**.
   - **Repository name**: e.g., `streamlit-quant-engine`
   - **Visibility**: Public (recommended for free Streamlit Community Cloud hosting) or Private.
   - Do **NOT** check "Initialize this repository with a README" (since we already have local files).
2. Click **Create repository**.
3. Copy the repository URL (e.g. `https://github.com/your-username/streamlit-quant-engine.git`).
4. Run the following commands in your terminal:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/streamlit-quant-engine.git
git push -u origin main
```

---

## ☁️ Step 3: Deploy Free on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **New app** (top right corner).
3. Fill in the deployment form:
   - **Repository**: `YOUR_USERNAME/streamlit-quant-engine`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Click **Deploy!**

Streamlit will read `requirements.txt`, install dependencies, and build your live web application. In less than 2 minutes, your web app will be live at a URL like `https://your-app-name.streamlit.app/`.

---

## 💡 Key Features of your Streamlit App
- **All 68 Modules**: Supports Technical, Fundamental, Machine Learning, Options, Sentiment, and Risk modules.
- **Interactive Ticker Selector**: Works seamlessly with Indian (`.NS`) and Global tickers (`AAPL`, `NVDA`, `TSLA`).
- **Dark Mode UI**: Styled cleanly using `.streamlit/config.toml`.
