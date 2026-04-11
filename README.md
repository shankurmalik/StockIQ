# StockIQ India — Gemini Version (100% Free)

## Step 1 — Get your FREE Gemini API key
Go to: https://aistudio.google.com/app/apikey
- Sign in with Google
- Click "Create API Key"
- Copy the key (starts with AIza...)
No credit card needed. Completely free.

## Step 2 — Install dependencies
Open terminal in this folder and run:
```
pip install -r requirements.txt
```

## Step 3 — Add your API key
Open `.streamlit/secrets.toml` and paste your key:
```
GEMINI_API_KEY = "AIza-your-actual-key-here"
```

## Step 4 — Run locally
```
streamlit run app.py
```
Browser opens at http://localhost:8501

---

## Deploy FREE on Streamlit Cloud

1. Push this folder to a GitHub repo
2. Go to https://streamlit.io/cloud → New App
3. Select your repo, set main file as `app.py`
4. Go to Settings → Secrets → paste:
   ```
   GEMINI_API_KEY = "AIza-your-key-here"
   ```
5. Click Deploy — get a free public URL!

---

## NSE symbols to try
RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, TATAMOTORS,
WIPRO, BAJFINANCE, ZOMATO, ADANIPORTS, SUNPHARMA, MARUTI,
AXISBANK, LTIM, COALINDIA, ONGC, NTPC, POWERGRID
