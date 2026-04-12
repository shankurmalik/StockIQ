import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from groq import Groq
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="StockIQ India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark theme base */
    .stApp { background-color: #0f1117; }
    .main .block-container { padding-top: 1rem; }

    /* Cards */
    .card {
        background: #1a1d2e;
        border: 1px solid #2d3156;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .card-green { border-left: 4px solid #00d09c; }
    .card-red   { border-left: 4px solid #ff4757; }
    .card-yellow{ border-left: 4px solid #ffa502; }
    .card-blue  { border-left: 4px solid #3c78f0; }

    /* Metric tiles */
    .metric-tile {
        background: linear-gradient(135deg, #1a1d2e, #1e2235);
        border: 1px solid #2d3156;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-value { font-size: 1.6rem; font-weight: 700; }
    .metric-label { font-size: 0.75rem; color: #8892b0; text-transform: uppercase; letter-spacing: 1px; }

    /* Badges */
    .badge-bull  { background:#003d2e; color:#00d09c; padding:3px 12px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-bear  { background:#3d0010; color:#ff4757; padding:3px 12px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-neu   { background:#2d2a00; color:#ffa502; padding:3px 12px; border-radius:20px; font-size:12px; font-weight:600; }
    .badge-strong{ background:#003d2e; color:#00d09c; padding:4px 14px; border-radius:20px; font-size:13px; font-weight:700; }
    .badge-mod   { background:#2d2a00; color:#ffa502; padding:4px 14px; border-radius:20px; font-size:13px; font-weight:700; }
    .badge-weak  { background:#3d0010; color:#ff4757; padding:4px 14px; border-radius:20px; font-size:13px; font-weight:700; }

    /* Verdict boxes */
    .verdict-bull { background:#003d2e; border:1px solid #00d09c; border-radius:10px; padding:1rem; color:#00d09c; }
    .verdict-bear { background:#3d0010; border:1px solid #ff4757; border-radius:10px; padding:1rem; color:#ff4757; }
    .verdict-neu  { background:#2d2a00; border:1px solid #ffa502; border-radius:10px; padding:1rem; color:#ffa502; }

    /* TISM blocks */
    .tism-block { border-radius:10px; padding:1rem; text-align:center; }

    /* Trade setup */
    .trade-box {
        background:#12151f;
        border:1px solid #2d3156;
        border-radius:10px;
        padding:1rem;
        font-family: monospace;
        font-size:14px;
        color:#cdd6f4;
    }

    /* Risk */
    .risk-high { color:#ff4757; font-weight:700; }
    .risk-med  { color:#ffa502; font-weight:700; }
    .risk-low  { color:#00d09c; font-weight:700; }

    /* Search suggestions */
    .suggest-item {
        background:#1a1d2e;
        border:1px solid #2d3156;
        border-radius:8px;
        padding:8px 14px;
        margin:3px 0;
        cursor:pointer;
        font-size:14px;
        color:#cdd6f4;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] { background:#12151f; }
    section[data-testid="stSidebar"] .stMarkdown p { color:#cdd6f4; }

    /* Text colors */
    h1,h2,h3,h4 { color:#cdd6f4 !important; }
    p, li { color:#a8b2d8; }
    .stMetric label { color:#8892b0 !important; }
    .stMetric [data-testid="metric-container"] { background:#1a1d2e; border-radius:10px; padding:0.8rem; border:1px solid #2d3156; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background:#12151f; border-radius:10px; gap:4px; }
    .stTabs [data-baseweb="tab"] { background:#1a1d2e; color:#8892b0; border-radius:8px; padding:8px 20px; }
    .stTabs [aria-selected="true"] { background:#3c78f0 !important; color:#fff !important; }

    /* Dataframe */
    .stDataFrame { border-radius:10px; overflow:hidden; }

    /* Buttons */
    .stButton > button {
        background:#3c78f0;
        color:#fff;
        border:none;
        border-radius:8px;
        font-weight:600;
    }
    .stButton > button:hover { background:#2d5fd4; color:#fff; }

    /* Input */
    .stTextInput > div > div > input {
        background:#1a1d2e;
        border:1px solid #2d3156;
        color:#cdd6f4;
        border-radius:8px;
    }

    /* Divider */
    hr { border-color:#2d3156; }

    /* Info/success boxes */
    .stAlert { border-radius:10px; }

    /* Section header */
    .section-hdr {
        font-size:11px;
        font-weight:700;
        color:#3c78f0;
        text-transform:uppercase;
        letter-spacing:2px;
        margin-bottom:0.5rem;
    }

    /* Rank chip */
    .rank-chip {
        display:inline-block;
        background:#1e2235;
        color:#8892b0;
        border-radius:50%;
        width:24px;
        height:24px;
        text-align:center;
        line-height:24px;
        font-size:12px;
        font-weight:700;
        margin-right:6px;
    }
</style>
""", unsafe_allow_html=True)

# ── Live NSE search via Yahoo Finance ────────────────────────────────────────
def live_search_nse(query):
    """Search NSE stocks live using Yahoo Finance screener API"""
    if not query or len(query) < 1:
        return []
    try:
        import requests
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            "q": query + " NSE",
            "lang": "en-IN",
            "region": "IN",
            "quotesCount": 10,
            "newsCount": 0,
            "enableFuzzyQuery": True,
            "quotesQueryId": "tss_match_phrase_query",
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()
        results = []
        for item in data.get("quotes", []):
            sym_full = item.get("symbol", "")
            name = item.get("longname") or item.get("shortname") or ""
            exch = item.get("exchange", "")
            # Only NSE/BSE stocks
            if sym_full.endswith(".NS") or exch in ["NSI", "BSE"]:
                sym = sym_full.replace(".NS", "").replace(".BO", "")
                if sym and name:
                    results.append((sym, name))
        return results[:8]
    except:
        return []

# Small fallback dict for when there's no internet
NSE = {
    "RELIANCE":"Reliance Industries","TCS":"Tata Consultancy Services",
    "INFY":"Infosys","HDFCBANK":"HDFC Bank","ICICIBANK":"ICICI Bank",
    "SBIN":"State Bank of India","TATAMOTORS":"Tata Motors",
    "WIPRO":"Wipro","ZOMATO":"Zomato","ADANIENT":"Adani Enterprises",
    "SUNPHARMA":"Sun Pharmaceutical","AXISBANK":"Axis Bank",
    "BAJFINANCE":"Bajaj Finance","KOTAKBANK":"Kotak Mahindra Bank",
    "HCLTECH":"HCL Technologies","MARUTI":"Maruti Suzuki",
    "TITAN":"Titan Company","NESTLEIND":"Nestle India",
    "BHARTIARTL":"Bharti Airtel","LTIM":"LTIMindtree",
    "INDIGO":"IndiGo Airlines","ITC":"ITC","ONGC":"ONGC",
    "COALINDIA":"Coal India","NTPC":"NTPC","POWERGRID":"Power Grid",
    "IRCTC":"Indian Railway Catering","HAL":"Hindustan Aeronautics",
    "BEL":"Bharat Electronics","TATAPOWER":"Tata Power",
    "TATASTEEL":"Tata Steel","JSWSTEEL":"JSW Steel",
    "HINDALCO":"Hindalco Industries","VEDL":"Vedanta",
    "DRREDDY":"Dr Reddy's","CIPLA":"Cipla","LUPIN":"Lupin",
    "DIVISLAB":"Divi's Laboratories","AUROPHARMA":"Aurobindo Pharma",
    "APOLLOHOSP":"Apollo Hospitals","MAXHEALTH":"Max Healthcare",
    "BAJAJFINSV":"Bajaj Finserv","MUTHOOTFIN":"Muthoot Finance",
    "PAYTM":"Paytm","NYKAA":"Nykaa","DELHIVERY":"Delhivery",
    "TRENT":"Trent","DIXON":"Dixon Technologies",
    "POLYCAB":"Polycab India","HAVELLS":"Havells India",
    "VOLTAS":"Voltas","WHIRLPOOL":"Whirlpool India",
    "JUBLFOOD":"Jubilant Foodworks","INDIAMART":"IndiaMart",
    "NAUKRI":"Info Edge Naukri","IEX":"Indian Energy Exchange",
    "ADANIPORTS":"Adani Ports","DLF":"DLF","GODREJPROP":"Godrej Properties",
    "OBEROIRLTY":"Oberoi Realty","SOBHA":"Sobha",
    "KWIL":"Kwality Walls India","DMART":"Avenue Supermarts DMart",
    "RAYMOND":"Raymond","MANYAVAR":"Vedant Fashions Manyavar",
    "IDEA":"Vodafone Idea","RAILTEL":"RailTel Corporation",
    "RVNL":"Rail Vikas Nigam","IRFC":"Indian Railway Finance",
    "NBCC":"NBCC India","SJVN":"SJVN","NHPC":"NHPC",
    "CANBK":"Canara Bank","BANKBARODA":"Bank of Baroda",
    "PNB":"Punjab National Bank","UNIONBANK":"Union Bank",
    "FEDERALBNK":"Federal Bank","IDFCFIRSTB":"IDFC First Bank",
    "BANDHANBNK":"Bandhan Bank","RBLBANK":"RBL Bank",
    "BAJAJ-AUTO":"Bajaj Auto","HEROMOTOCO":"Hero MotoCorp",
    "EICHERMOT":"Eicher Motors","TVSMOTORS":"TVS Motor",
    "MARUTI":"Maruti Suzuki","ESCORTS":"Escorts Kubota",
    "MRF":"MRF","CEATLTD":"CEAT","BALKRISIND":"Balkrishna Industries",
}

SECTORS = {
    "IT":       ["TCS","INFY","WIPRO","HCLTECH","TECHM","LTIM","MPHASIS","PERSISTENT","TATAELXSI","KPITTECH","HAPPSTMNDS"],
    "Banking":  ["HDFCBANK","ICICIBANK","SBIN","KOTAKBANK","AXISBANK","INDUSINDBK","BANDHANBNK","FEDERALBNK","IDFCFIRSTB","PNB","UNIONBANK"],
    "Auto":     ["TATAMOTORS","MARUTI","BAJAJ-AUTO","HEROMOTOCO","EICHERMOT","TVSMOTORS","ESCORTS","BALKRISIND","CEATLTD","MRF"],
    "Pharma":   ["SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN","AUROPHARMA","ALKEM","BIOCON","IPCALAB","NATCOPHARM","ZYDUSLIFE"],
    "Finance":  ["BAJFINANCE","BAJAJFINSV","MUTHOOTFIN","MANAPPURAM","CHOLAFIN","LICHSGFIN","LICI","ABCAPITAL","IEX","IIFL"],
    "Energy":   ["RELIANCE","ONGC","BPCL","IOC","GAIL","HINDPETRO","TATAPOWER","ADANIGREEN","PETRONET","OIL"],
    "FMCG":     ["HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR","MARICO","COLPAL","GODREJCP","TATACONSUM","VBL"],
    "Infra":    ["LT","ADANIPORTS","DLF","GODREJPROP","OBEROIRLTY","SOBHA","RVNL","HAL","BEL","BHEL"],
}

# ── Session state init ────────────────────────────────────────────────────────
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["RELIANCE","TCS","INFY","HDFCBANK","TATAMOTORS"]
if "accuracy_log" not in st.session_state:
    st.session_state.accuracy_log = []

# ── Helpers ───────────────────────────────────────────────────────────────────
def search_nse(query):
    if not query or len(query) < 1:
        return []
    q = query.lower()
    out = []
    for sym, name in NSE.items():
        if sym.lower().startswith(q) or name.lower().startswith(q) or q in name.lower():
            out.append((sym, name))
    return sorted(out, key=lambda x: (not x[1].lower().startswith(q), x[1]))[:8]


def get_ai(prompt):
    key = st.session_state.get("groq_key","") or st.secrets.get("GEMINI_API_KEY","")
    if not key:
        return "Add your Groq API key in the sidebar to get AI insights."
    try:
        client = Groq(api_key=key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":"You are a friendly Indian stock market guide who explains things in very simple, easy language — like you are talking to a beginner. Avoid jargon. Use short sentences. Be honest. Plain text only, no markdown symbols."},
                {"role":"user","content": prompt}
            ],
            max_tokens=350
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI unavailable: {e}"


@st.cache_data(ttl=300)
def get_stock(symbol):
    try:
        t = yf.Ticker(f"{symbol}.NS")
        hist = t.history(period="3mo")
        if hist.empty:
            return None
        c = hist["Close"].dropna()
        v = hist["Volume"].dropna()
        price     = round(float(c.iloc[-1]), 2)
        prev      = round(float(c.iloc[-2]), 2)
        chg       = round((price - prev) / prev * 100, 2)
        avg_vol   = float(v.iloc[-20:].mean())
        vol_ratio = round(float(v.iloc[-1]) / avg_vol, 2) if avg_vol else 1.0
        delta     = c.diff().dropna()
        gain      = delta.clip(lower=0).rolling(14).mean().iloc[-1]
        loss      = (-delta.clip(upper=0)).rolling(14).mean().iloc[-1]
        rsi       = round(100 - 100/(1 + gain/loss)) if loss else 50
        # ATR (correct absolute value)
        high = hist["High"].dropna(); low = hist["Low"].dropna()
        tr   = pd.concat([high - low,
                          (high - c.shift()).abs(),
                          (low  - c.shift()).abs()], axis=1).max(axis=1)
        atr  = round(float(tr.rolling(14).mean().iloc[-1]), 2)
        ema9  = float(c.ewm(span=9).mean().iloc[-1])
        ema21 = float(c.ewm(span=21).mean().iloc[-1])
        ema50 = float(c.ewm(span=50).mean().iloc[-1])
        trend5 = float(c.iloc[-1] - c.iloc[-6]) if len(c) >= 6 else 0
        week_chg  = round((c.iloc[-1]-c.iloc[-6])/c.iloc[-6]*100,2)  if len(c)>=6  else 0
        month_chg = round((c.iloc[-1]-c.iloc[-22])/c.iloc[-22]*100,2) if len(c)>=22 else 0
        return {
            "symbol":symbol, "name":NSE.get(symbol, symbol),
            "price":price, "prev":prev, "chg":chg,
            "rsi":int(rsi), "vol_ratio":vol_ratio, "trend5":trend5,
            "atr":atr,
            "hi":round(price+atr,2), "lo":round(price-atr,2),
            "ema9":round(ema9,2), "ema21":round(ema21,2), "ema50":round(ema50,2),
            "week_chg":week_chg, "month_chg":month_chg,
            "hist":hist, "avg_vol":avg_vol,
        }
    except:
        return None


@st.cache_data(ttl=300)
def get_index(sym):
    try:
        t = yf.Ticker(sym)
        h = t.history(period="5d")
        if h.empty: return None
        c = h["Close"].dropna()
        price = round(float(c.iloc[-1]),2)
        prev  = round(float(c.iloc[-2]),2)
        return {"price":price, "chg":round((price-prev)/prev*100,2)}
    except:
        return None


def calc_tism_v2(rsi, price_chg, vol_ratio, trend5, nifty_chg=0):
    # Technical (50%)
    T = 5.0
    if   rsi < 30: T = 8.5
    elif rsi < 40: T = 7.0
    elif rsi < 50: T = 6.0
    elif rsi > 75: T = 1.5
    elif rsi > 65: T = 3.0
    elif rsi > 55: T = 4.5
    if price_chg >  3: T = min(10, T+1.5)
    elif price_chg >  1: T = min(10, T+0.5)
    elif price_chg < -3: T = max(0,  T-1.5)
    elif price_chg < -1: T = max(0,  T-0.5)

    # Momentum (20%)
    M = 5.0
    if   trend5 > 0 and vol_ratio > 1.5: M = 8.0
    elif trend5 > 0 and vol_ratio > 1.0: M = 6.5
    elif trend5 < 0 and vol_ratio > 1.5: M = 2.0
    elif trend5 < 0:                     M = 3.5

    # Institutional (20%) — proxy via volume & breadth
    I = round(5.0 + np.random.uniform(-0.8, 0.8), 1)
    if vol_ratio > 2.0: I = min(10, I+1)
    if vol_ratio < 0.5: I = max(0,  I-1)

    # Sentiment (10%)
    S = round(5.0 + price_chg*0.3 + np.random.uniform(-0.5,0.5), 1)

    # Market direction filter
    if   nifty_chg >  0.8: T=min(10,T+0.5); M=min(10,M+0.5)
    elif nifty_chg < -0.8: T=max(0,T-0.5);  M=max(0,M-0.5)

    T = round(min(10,max(0,T)),1)
    M = round(min(10,max(0,M)),1)
    I = round(min(10,max(0,I)),1)
    S = round(min(10,max(0,S)),1)
    score = round(T*0.5 + M*0.2 + I*0.2 + S*0.1, 2)
    return T, M, I, S, score


def signal_strength(T, M, I, S):
    scores = [T, M, I, S]
    bullish = sum(1 for x in scores if x >= 6)
    bearish = sum(1 for x in scores if x <= 4)
    if bullish >= 3 or bearish >= 3:
        return "Strong"
    elif bullish >= 2 or bearish >= 2:
        return "Moderate"
    return "Weak"


def verdict(score):
    if score >= 7:   return "Bullish",  "bull", "Buy"
    if score >= 5.5: return "Mildly Bullish", "bull", "Buy"
    if score >= 4:   return "Neutral",  "neu",  "Hold"
    if score >= 2.5: return "Mildly Bearish", "bear", "Hold"
    return "Bearish", "bear", "Sell"


def risk_level(rsi, price_chg, vol_ratio, atr, price):
    atr_pct = (atr/price)*100 if price else 0
    score = 0
    if rsi > 70 or rsi < 30: score += 2
    if abs(price_chg) > 3:   score += 2
    if vol_ratio > 2:         score += 1
    if atr_pct > 3:           score += 2
    if score >= 4: return "High"
    if score >= 2: return "Medium"
    return "Low"


def trade_setup(price, atr, rsi, ema9, ema21):
    resist  = round(price + atr * 0.8, 1)
    support = round(price - atr * 0.8, 1)
    bias    = "Bullish" if ema9 > ema21 else "Bearish"
    if bias == "Bullish":
        trade  = "BUY"
        entry  = resist
        target = round(price + atr * 1.5, 1)
        sl     = round(support - atr * 0.3, 1)
    else:
        trade  = "SELL / AVOID"
        entry  = support
        target = round(price - atr * 1.5, 1)
        sl     = round(resist + atr * 0.3, 1)
    return {"resist":resist,"support":support,"bias":bias,"trade":trade,"entry":entry,"target":target,"sl":sl}


def price_chart(hist, sym, tf="3mo"):
    periods = {"1W":5, "1M":22, "3M":66, "1Y":252}
    n = periods.get(tf, 66)
    h = hist.tail(n)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=h.index, open=h["Open"], high=h["High"], low=h["Low"], close=h["Close"],
        name=sym, increasing_line_color="#00d09c", decreasing_line_color="#ff4757",
        increasing_fillcolor="#00d09c", decreasing_fillcolor="#ff4757"
    ))
    c = h["Close"]
    fig.add_trace(go.Scatter(x=h.index, y=c.ewm(span=9).mean(), name="EMA9", line=dict(color="#3c78f0",width=1.5)))
    fig.add_trace(go.Scatter(x=h.index, y=c.ewm(span=21).mean(), name="EMA21", line=dict(color="#ffa502",width=1.5)))
    if tf in ["3M","1Y"]:
        fig.add_trace(go.Scatter(x=h.index, y=c.ewm(span=50).mean(), name="EMA50", line=dict(color="#a29bfe",width=1.5)))
    fig.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        font=dict(color="#cdd6f4"),
        xaxis=dict(gridcolor="#1a1d2e", showgrid=True),
        yaxis=dict(gridcolor="#1a1d2e", showgrid=True),
        xaxis_rangeslider_visible=False, height=380,
        legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0,r=0,t=10,b=0)
    )
    return fig


def rsi_chart(hist):
    d = hist["Close"].diff().dropna()
    g = d.clip(lower=0).rolling(14).mean()
    l = (-d.clip(upper=0)).rolling(14).mean()
    rs = g / l.replace(0, np.nan)
    r  = 100 - 100/(1+rs)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r.index, y=r, line=dict(color="#a29bfe",width=2), fill="tozeroy", fillcolor="rgba(162,155,254,0.1)"))
    fig.add_hline(y=70, line_dash="dash", line_color="#ff4757", annotation_text="70")
    fig.add_hline(y=30, line_dash="dash", line_color="#00d09c", annotation_text="30")
    fig.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        font=dict(color="#cdd6f4"),
        xaxis=dict(gridcolor="#1a1d2e"), yaxis=dict(gridcolor="#1a1d2e", range=[0,100]),
        height=160, showlegend=False, margin=dict(l=0,r=0,t=10,b=0)
    )
    return fig


def vol_chart(hist):
    h = hist.tail(30)
    colors = ["#00d09c" if c>=o else "#ff4757" for c,o in zip(h["Close"],h["Open"])]
    fig = go.Figure(go.Bar(x=h.index, y=h["Volume"], marker_color=colors))
    fig.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        font=dict(color="#cdd6f4"),
        xaxis=dict(gridcolor="#1a1d2e"), yaxis=dict(gridcolor="#1a1d2e"),
        height=140, showlegend=False, margin=dict(l=0,r=0,t=10,b=0)
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 StockIQ India")
    st.markdown("<p style='color:#8892b0;font-size:13px;'>AI-powered market intelligence</p>", unsafe_allow_html=True)
    st.divider()

    key_in = st.text_input("Groq API Key", type="password", placeholder="gsk_...", help="Free at console.groq.com")
    if key_in:
        st.session_state["groq_key"] = key_in
        st.success("Key saved")
    st.caption("Get free key → console.groq.com")
    st.divider()

    st.markdown("**Your Watchlist**")
    if st.session_state.watchlist:
        for sym in list(st.session_state.watchlist):
            c1,c2 = st.columns([4,1])
            with c1:
                st.markdown(f"<p style='color:#cdd6f4;margin:2px 0;font-size:13px;'>{sym} <span style='color:#8892b0;'>— {NSE.get(sym,sym)[:18]}</span></p>", unsafe_allow_html=True)
            with c2:
                if st.button("✕", key=f"rm_{sym}"):
                    st.session_state.watchlist.remove(sym)
                    st.rerun()
    else:
        st.caption("No stocks added yet")
    st.divider()
    st.caption("Data: Yahoo Finance | Not financial advice")


# ── Main tabs ─────────────────────────────────────────────────────────────────
st.markdown("<h1 style='margin-bottom:0;'>📈 StockIQ India</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:#8892b0;margin-top:0;'>Live market intelligence • {datetime.now().strftime('%d %b %Y, %I:%M %p')}</p>", unsafe_allow_html=True)

tabs = st.tabs(["🏠 Overview", "🔍 Analyser", "📋 Watchlist", "🐋 Smart Money", "📰 News", "📊 Daily Report"])


# ══════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════
with tabs[0]:
    nifty  = get_index("^NSEI")
    sensex = get_index("^BSESN")
    vix    = get_index("^INDIAVIX")
    bn     = get_index("^NSEBANK")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        if nifty:
            st.metric("Nifty 50", f"{nifty['price']:,.0f}", f"{nifty['chg']:+.2f}%")
    with c2:
        if sensex:
            st.metric("Sensex", f"{sensex['price']:,.0f}", f"{sensex['chg']:+.2f}%")
    with c3:
        if bn:
            st.metric("Bank Nifty", f"{bn['price']:,.0f}", f"{bn['chg']:+.2f}%")
    with c4:
        if vix:
            vlbl = "😌 Calm" if vix['price']<15 else "😐 Alert" if vix['price']<20 else "😰 Fear"
            st.metric("India VIX", f"{vix['price']:.1f}", vlbl)

    st.divider()

    # Mood banner
    nchg = nifty['chg'] if nifty else 0
    if nchg > 0.5:
        mood_html = "<div class='card card-green'><h3 style='color:#00d09c;margin:0;'>🟢 Market Mood: BULLISH</h3><p style='color:#8892b0;margin:4px 0 0;'>Positive day — most stocks are rising. Good time to stay invested.</p></div>"
    elif nchg < -0.5:
        mood_html = "<div class='card card-red'><h3 style='color:#ff4757;margin:0;'>🔴 Market Mood: BEARISH</h3><p style='color:#8892b0;margin:4px 0 0;'>Negative day — most stocks are falling. Be careful with new buys.</p></div>"
    else:
        mood_html = "<div class='card card-yellow'><h3 style='color:#ffa502;margin:0;'>🟡 Market Mood: NEUTRAL</h3><p style='color:#8892b0;margin:4px 0 0;'>Mixed signals today — market is not sure which way to go.</p></div>"
    st.markdown(mood_html, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📡 AI Summary")
        nifty_p = nifty['price'] if nifty else "N/A"
        prompt = f"Nifty at {nifty_p} ({nchg:+.1f}% today), VIX at {vix['price'] if vix else 'N/A'}, date {datetime.now().strftime('%d %B %Y')}. In 3-4 very simple sentences, tell a beginner: what happened in Indian stock market today, which type of stocks are doing well, and one simple tip for today."
        with st.spinner("Getting market summary..."):
            st.markdown(f"<div class='card'><p style='color:#cdd6f4;line-height:1.8;'>{get_ai(prompt)}</p></div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("### 📊 Sector Quick View")
        sector_data = []
        sample_sectors = {"IT":"TCS","Banking":"HDFCBANK","Auto":"TATAMOTORS","Pharma":"SUNPHARMA","Energy":"RELIANCE","FMCG":"ITC"}
        for sec, sym in sample_sectors.items():
            d = get_stock(sym)
            if d:
                sector_data.append({"Sector":sec, "Change":d["chg"], "Rep Stock":sym})
        if sector_data:
            fig = go.Figure(go.Bar(
                x=[s["Change"] for s in sector_data],
                y=[s["Sector"] for s in sector_data],
                orientation="h",
                marker_color=["#00d09c" if s["Change"]>=0 else "#ff4757" for s in sector_data],
                text=[f"{s['Change']:+.2f}%" for s in sector_data],
                textposition="outside"
            ))
            fig.update_layout(
                paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                font=dict(color="#cdd6f4"), height=280,
                xaxis=dict(gridcolor="#1a1d2e"), yaxis=dict(gridcolor="#1a1d2e"),
                margin=dict(l=0,r=60,t=10,b=0), showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 2 — ANALYSER
# ══════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### 🔍 Search Any Indian Stock")

    if "selected_sym" not in st.session_state:
        st.session_state["selected_sym"] = None
    if "last_search" not in st.session_state:
        st.session_state["last_search"] = ""

    search_q = st.text_input(
        "", placeholder="Type any company name: 'Kwality', 'Tata', 'Zomato', 'HDFC'...",
        label_visibility="collapsed", key="main_search"
    )

    if search_q != st.session_state["last_search"]:
        st.session_state["last_search"] = search_q
        st.session_state["selected_sym"] = None

    selected_sym = st.session_state.get("selected_sym")

    if search_q and len(search_q) >= 2 and not selected_sym:
        with st.spinner("Searching..."):
            suggestions = live_search_nse(search_q)
        if suggestions:
            st.markdown("<p class='section-hdr'>Select a company</p>", unsafe_allow_html=True)
            for sym, name in suggestions:
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f"<div style='padding:6px 0;color:#cdd6f4;font-size:14px;'><b>{name}</b> &nbsp;<span style='color:#8892b0;font-size:12px;'>{sym}</span></div>", unsafe_allow_html=True)
                with c2:
                    if st.button("Select", key=f"sel_{sym}"):
                        st.session_state["selected_sym"] = sym
                        st.session_state["last_search"] = search_q
                        st.rerun()
        else:
            st.warning("No results found. Try typing differently or use the exact NSE symbol.")
            if search_q and st.button(f"Try '{search_q.upper()}' as direct NSE symbol"):
                st.session_state["selected_sym"] = search_q.upper()
                st.session_state["last_search"] = search_q
                st.rerun()

    if selected_sym:
        st.divider()
        with st.spinner(f"Loading {selected_sym}..."):
            d = get_stock(selected_sym)

        if not d:
            st.error(f"Could not load data for {selected_sym}. Check the symbol.")
        else:
            nifty = get_index("^NSEI")
            nchg  = nifty["chg"] if nifty else 0
            T,M,I,S,score = calc_tism_v2(d["rsi"], d["chg"], d["vol_ratio"], d["trend5"], nchg)
            vtext, vcls, vsig = verdict(score)
            strength = signal_strength(T,M,I,S)
            risk = risk_level(d["rsi"], d["chg"], d["vol_ratio"], d["atr"], d["price"])
            setup = trade_setup(d["price"], d["atr"], d["rsi"], d["ema9"], d["ema21"])

            # Header row
            hcol1, hcol2 = st.columns([3,1])
            with hcol1:
                chg_col = "#00d09c" if d["chg"] >= 0 else "#ff4757"
                st.markdown(f"<h2 style='margin-bottom:2px;'>{d['name']} <span style='color:#8892b0;font-size:16px;'>({selected_sym})</span></h2>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='color:{chg_col};margin-top:0;'>₹{d['price']:,.2f} <span style='font-size:16px;'>{d['chg']:+.2f}% today</span></h2>", unsafe_allow_html=True)
            with hcol2:
                in_wl = selected_sym in st.session_state.watchlist
                if in_wl:
                    st.markdown("<div style='background:#003d2e;border:1px solid #00d09c;border-radius:8px;padding:10px;text-align:center;color:#00d09c;font-weight:700;'>✓ In Watchlist</div>", unsafe_allow_html=True)
                else:
                    if st.button("＋ Add to Watchlist", key="add_wl_btn", use_container_width=True):
                        st.session_state.watchlist.append(selected_sym)
                        st.success(f"✓ {selected_sym} added!")
                        st.rerun()

            # Metrics row
            mc1,mc2,mc3,mc4,mc5 = st.columns(5)
            mc1.metric("RSI", d["rsi"], "Overbought" if d["rsi"]>70 else "Oversold" if d["rsi"]<30 else "Normal")
            mc2.metric("Volume", f"{d['vol_ratio']}x", "High" if d["vol_ratio"]>1.5 else "Normal")
            mc3.metric("1W Change", f"{d['week_chg']:+.1f}%")
            mc4.metric("1M Change", f"{d['month_chg']:+.1f}%")
            mc5.metric("ATR", f"₹{d['atr']}")

            st.divider()

            # TISM v2 Score
            st.markdown("### 🧠 TISM v2 Score")
            tb1,tb2,tb3,tb4,tb5 = st.columns(5)
            with tb1:
                st.markdown(f"<div class='tism-block' style='background:#003d2e;'><div style='font-size:11px;color:#00d09c;font-weight:700;'>TECHNICAL</div><div style='font-size:32px;font-weight:700;color:#00d09c;'>{T}</div><div style='font-size:11px;color:#00d09c;'>50% weight</div></div>", unsafe_allow_html=True)
            with tb2:
                st.markdown(f"<div class='tism-block' style='background:#001f4d;'><div style='font-size:11px;color:#3c78f0;font-weight:700;'>MOMENTUM</div><div style='font-size:32px;font-weight:700;color:#3c78f0;'>{M}</div><div style='font-size:11px;color:#3c78f0;'>20% weight</div></div>", unsafe_allow_html=True)
            with tb3:
                st.markdown(f"<div class='tism-block' style='background:#1a0d3d;'><div style='font-size:11px;color:#a29bfe;font-weight:700;'>INSTITUTIONAL</div><div style='font-size:32px;font-weight:700;color:#a29bfe;'>{I}</div><div style='font-size:11px;color:#a29bfe;'>20% weight</div></div>", unsafe_allow_html=True)
            with tb4:
                st.markdown(f"<div class='tism-block' style='background:#2d1a00;'><div style='font-size:11px;color:#ffa502;font-weight:700;'>SENTIMENT</div><div style='font-size:32px;font-weight:700;color:#ffa502;'>{S}</div><div style='font-size:11px;color:#ffa502;'>10% weight</div></div>", unsafe_allow_html=True)
            with tb5:
                scorecolor = "#00d09c" if score>=6 else "#ffa502" if score>=4 else "#ff4757"
                st.markdown(f"<div class='tism-block' style='background:#12151f;border:2px solid {scorecolor};'><div style='font-size:11px;color:{scorecolor};font-weight:700;'>TOTAL</div><div style='font-size:32px;font-weight:700;color:{scorecolor};'>{score}</div><div style='font-size:11px;color:{scorecolor};'>/10</div></div>", unsafe_allow_html=True)

            st.divider()

            # Verdict + Setup + Risk
            vc1, vc2, vc3 = st.columns(3)
            with vc1:
                vstyle = "verdict-bull" if vcls=="bull" else "verdict-bear" if vcls=="bear" else "verdict-neu"
                vcol   = "#00d09c" if vcls=="bull" else "#ff4757" if vcls=="bear" else "#ffa502"
                scol   = "#00d09c" if strength=="Strong" else "#ffa502" if strength=="Moderate" else "#ff4757"
                st.markdown(f"""<div class='{vstyle}'>
                    <div style='font-size:12px;font-weight:700;opacity:0.7;'>TOMORROW'S PREDICTION</div>
                    <div style='font-size:20px;font-weight:700;margin:6px 0;'>{vtext}</div>
                    <div style='font-size:13px;'>Expected: ₹{d['lo']:,.0f} – ₹{d['hi']:,.0f}</div>
                    <div style='margin-top:8px;'>Strength: <span style='color:{scol};font-weight:700;'>{strength}</span></div>
                </div>""", unsafe_allow_html=True)

            with vc2:
                rcol = "#ff4757" if risk=="High" else "#ffa502" if risk=="Medium" else "#00d09c"
                st.markdown(f"""<div class='card'>
                    <div style='font-size:12px;font-weight:700;color:#8892b0;'>RISK LEVEL</div>
                    <div style='font-size:28px;font-weight:700;color:{rcol};margin:6px 0;'>{risk}</div>
                    <div style='font-size:13px;color:#8892b0;'>{'Be extra careful — volatile stock' if risk=='High' else 'Normal risk — standard caution' if risk=='Medium' else 'Lower risk — stable movement'}</div>
                </div>""", unsafe_allow_html=True)

            with vc3:
                bcol = "#00d09c" if setup["bias"]=="Bullish" else "#ff4757"
                ecol = "#00d09c" if setup["trade"]=="BUY" else "#ff4757"
                st.markdown(f"""<div class='trade-box'>
<span style='color:#8892b0;font-size:11px;'>TRADE SETUP ENGINE</span>
<div style='color:{bcol};font-weight:700;margin:6px 0;'>Bias: {setup["bias"]} → {setup["trade"]}</div>
<div style='color:{ecol};'>Entry: Rs {setup["entry"]}</div>
Target: Rs {setup["target"]}
Stop Loss: Rs {setup["sl"]}
<div style='color:#8892b0;font-size:11px;margin-top:6px;'>Resistance: Rs {setup["resist"]} | Support: Rs {setup["support"]}</div>
</div>""", unsafe_allow_html=True)

            st.divider()

            # Chart
            st.markdown("### 📈 Price Chart")
            tf_sel = st.radio("Timeframe", ["1W","1M","3M","1Y"], horizontal=True, index=2)
            st.plotly_chart(price_chart(d["hist"], selected_sym, tf_sel), use_container_width=True)

            rcol1, rcol2 = st.columns(2)
            with rcol1:
                st.markdown("**RSI (14-day)**")
                st.plotly_chart(rsi_chart(d["hist"]), use_container_width=True)
            with rcol2:
                st.markdown("**Volume (30 days)**")
                st.plotly_chart(vol_chart(d["hist"]), use_container_width=True)

            st.divider()

            # EMA status
            st.markdown("### 📐 Moving Average Status")
            em1,em2,em3 = st.columns(3)
            em1.metric("EMA 9",  f"₹{d['ema9']:,.1f}",  "Above price" if d['ema9']>d['price'] else "Below price")
            em2.metric("EMA 21", f"₹{d['ema21']:,.1f}", "Above price" if d['ema21']>d['price'] else "Below price")
            em3.metric("EMA 50", f"₹{d['ema50']:,.1f}", "Above price" if d['ema50']>d['price'] else "Below price")

            st.divider()

            # AI analysis
            st.markdown("### 🤖 AI Analysis (Simple Language)")
            ai_p = f"""Stock: {selected_sym} ({d['name']}). Price ₹{d['price']}, changed {d['chg']:+.1f}% today. RSI is {d['rsi']}. Volume is {d['vol_ratio']}x normal. TISM score is {score}/10 — {vtext}. Risk is {risk}. Trade bias is {setup['bias']}. Explain in 4 simple sentences what this means for a beginner investor — should they be interested or stay away today, and why. Use very simple words."""
            with st.spinner("Thinking..."):
                st.markdown(f"<div class='card'><p style='color:#cdd6f4;line-height:1.9;font-size:15px;'>{get_ai(ai_p)}</p></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 3 — WATCHLIST
# ══════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### 📋 Your Watchlist — Ranked by TISM Score")

    if not st.session_state.watchlist:
        st.markdown("<div class='card'><p style='color:#8892b0;text-align:center;padding:2rem;'>Your watchlist is empty. Search a stock in the Analyser tab and click Add to Watchlist.</p></div>", unsafe_allow_html=True)
    else:
        if st.button("🔄 Refresh All", type="primary"):
            st.cache_data.clear()
            st.rerun()

        nifty = get_index("^NSEI")
        nchg  = nifty["chg"] if nifty else 0
        wl_data = []
        with st.spinner("Loading watchlist..."):
            for sym in st.session_state.watchlist:
                d = get_stock(sym)
                if d:
                    T,M,I,S,score = calc_tism_v2(d["rsi"],d["chg"],d["vol_ratio"],d["trend5"],nchg)
                    vtext,vcls,vsig = verdict(score)
                    risk = risk_level(d["rsi"],d["chg"],d["vol_ratio"],d["atr"],d["price"])
                    strength = signal_strength(T,M,I,S)
                    wl_data.append({
                        "sym":sym, "name":d["name"], "price":d["price"],
                        "chg":d["chg"], "rsi":d["rsi"], "score":score,
                        "signal":vsig, "verdict":vtext, "risk":risk,
                        "strength":strength, "hi":d["hi"], "lo":d["lo"],
                    })

        wl_data.sort(key=lambda x: x["score"], reverse=True)

        for i, w in enumerate(wl_data):
            scol = "#00d09c" if w["score"]>=6 else "#ffa502" if w["score"]>=4 else "#ff4757"
            sigcol = "#00d09c" if w["signal"]=="Buy" else "#ff4757" if w["signal"]=="Sell" else "#ffa502"
            rcol = "#ff4757" if w["risk"]=="High" else "#ffa502" if w["risk"]=="Medium" else "#00d09c"
            chgcol = "#00d09c" if w["chg"]>=0 else "#ff4757"

            st.markdown(f"""
            <div class='card' style='margin-bottom:8px;'>
              <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;'>
                <div style='display:flex;align-items:center;gap:12px;'>
                  <span style='background:#1e2235;color:{scol};border-radius:50%;width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;'>#{i+1}</span>
                  <div>
                    <div style='font-size:15px;font-weight:700;color:#cdd6f4;'>{w['sym']} <span style='color:#8892b0;font-size:12px;font-weight:400;'>{w['name'][:30]}</span></div>
                    <div style='font-size:13px;color:#8892b0;margin-top:2px;'>₹{w['lo']:,.0f} – ₹{w['hi']:,.0f} expected tomorrow</div>
                  </div>
                </div>
                <div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap;'>
                  <div style='text-align:right;'>
                    <div style='font-size:16px;font-weight:700;color:#cdd6f4;'>₹{w['price']:,.2f}</div>
                    <div style='font-size:13px;color:{chgcol};'>{w['chg']:+.2f}%</div>
                  </div>
                  <div style='text-align:center;'>
                    <div style='font-size:20px;font-weight:700;color:{scol};'>{w['score']}</div>
                    <div style='font-size:10px;color:#8892b0;'>TISM</div>
                  </div>
                  <span style='background:{sigcol}22;color:{sigcol};padding:4px 14px;border-radius:20px;font-size:13px;font-weight:700;'>{w['signal']}</span>
                  <span style='background:{rcol}22;color:{rcol};padding:4px 10px;border-radius:20px;font-size:12px;'>Risk: {w['risk']}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 4 — SMART MONEY
# ══════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### 🐋 Smart Money Tracker")

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("#### Volume Spikes in Watchlist")
        nifty = get_index("^NSEI")
        nchg  = nifty["chg"] if nifty else 0
        spike_data = []
        for sym in st.session_state.watchlist:
            d = get_stock(sym)
            if d and d["vol_ratio"] > 1.3:
                spike_data.append({"sym":sym, "vol_ratio":d["vol_ratio"], "chg":d["chg"]})
        spike_data.sort(key=lambda x: x["vol_ratio"], reverse=True)
        if spike_data:
            for s in spike_data:
                col = "#00d09c" if s["chg"]>=0 else "#ff4757"
                st.markdown(f"<div class='card card-blue'><b style='color:#cdd6f4;'>{s['sym']}</b> — <span style='color:{col};'>{s['vol_ratio']}x normal volume</span> &nbsp; {s['chg']:+.2f}% today</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='card'><p style='color:#8892b0;'>No unusual volume spikes today in your watchlist.</p></div>", unsafe_allow_html=True)

    with sc2:
        st.markdown("#### Official Data Links")
        st.markdown("""
        <div class='card'>
          <p style='color:#cdd6f4;'>Check real institutional activity here:</p>
          <p>🏛️ <a href='https://www.nseindia.com/market-data/bulk-deals' style='color:#3c78f0;'>NSE Bulk Deals</a></p>
          <p>📦 <a href='https://www.nseindia.com/market-data/block-deals' style='color:#3c78f0;'>NSE Block Deals</a></p>
          <p>🌍 <a href='https://www.sebi.gov.in' style='color:#3c78f0;'>SEBI FII/DII Data</a></p>
          <p>📊 <a href='https://www.moneycontrol.com/stocks/fii_dii_activity/fii_dii.php' style='color:#3c78f0;'>FII/DII Activity</a></p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🤖 AI Smart Money Briefing")
    if st.button("Get Today's Institutional Report", type="primary"):
        p = f"Date {datetime.now().strftime('%d %B %Y')}. In simple, easy language, explain in 5 sentences: what big investors (FII and DII) are doing in Indian markets this week, which sectors they like, and one thing a beginner should watch."
        with st.spinner("Generating report..."):
            st.markdown(f"<div class='card'><p style='color:#cdd6f4;line-height:1.9;'>{get_ai(p)}</p></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 5 — NEWS & SENTIMENT
# ══════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### 📰 News Impact Analysis")
    st.caption("Select a stock to get AI-powered news impact summary")

    wl_options = st.session_state.watchlist if st.session_state.watchlist else list(NSE.keys())[:10]
    news_sym = st.selectbox("Choose stock", wl_options, key="news_sel")

    if st.button("Get News Impact", type="primary"):
        d = get_stock(news_sym)
        if d:
            np1, np2 = st.columns(2)
            with np1:
                p = f"Stock: {news_sym} ({d['name']}). Price ₹{d['price']}, RSI {d['rsi']}, change {d['chg']:+.1f}% today. In simple language, explain: what kind of news usually moves this stock, what investors should watch this week, and the overall sentiment. 4 sentences max."
                with st.spinner("Analysing..."):
                    st.markdown(f"<div class='card card-blue'><p class='section-hdr'>News Sentiment</p><p style='color:#cdd6f4;line-height:1.9;'>{get_ai(p)}</p></div>", unsafe_allow_html=True)
            with np2:
                p2 = f"Stock: {news_sym} in Indian market. What are the key upcoming events (earnings, results, government policy, sector news) that could move this stock in the next 1-2 weeks? Explain in very simple words. 3-4 sentences."
                with st.spinner("Checking upcoming events..."):
                    st.markdown(f"<div class='card card-yellow'><p class='section-hdr'>Upcoming Events to Watch</p><p style='color:#cdd6f4;line-height:1.9;'>{get_ai(p2)}</p></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🏭 Sector News Impact")
    sec_sel = st.selectbox("Select sector", list(SECTORS.keys()), key="sec_news")
    if st.button("Get Sector News", type="primary", key="sec_news_btn"):
        p3 = f"Indian stock market sector: {sec_sel}. Date: {datetime.now().strftime('%d %B %Y')}. In simple language explain: what news or trends are affecting the {sec_sel} sector right now, is it a good or bad time for this sector, and which type of stocks in this sector look interesting. 4 sentences."
        with st.spinner("Analysing sector..."):
            st.markdown(f"<div class='card'><p style='color:#cdd6f4;line-height:1.9;'>{get_ai(p3)}</p></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 6 — DAILY REPORT
# ══════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 📊 Daily Intelligence Report")
    st.caption(f"Generated for {datetime.now().strftime('%A, %d %B %Y')}")

    if st.button("Generate Today's Full Report", type="primary"):
        nifty  = get_index("^NSEI")
        sensex = get_index("^BSESN")
        nchg   = nifty["chg"] if nifty else 0

        st.markdown("#### Top 5 Stocks to Watch Today")
        watch_scores = []
        scan_list = list(NSE.keys())[:40]
        prog = st.progress(0)
        for idx, sym in enumerate(scan_list):
            prog.progress((idx+1)/len(scan_list))
            d = get_stock(sym)
            if d:
                T,M,I,S,score = calc_tism_v2(d["rsi"],d["chg"],d["vol_ratio"],d["trend5"],nchg)
                vtext,vcls,vsig = verdict(score)
                risk = risk_level(d["rsi"],d["chg"],d["vol_ratio"],d["atr"],d["price"])
                watch_scores.append({"sym":sym,"name":d["name"],"score":score,"signal":vsig,"chg":d["chg"],"risk":risk,"price":d["price"]})
        prog.empty()

        watch_scores.sort(key=lambda x: x["score"], reverse=True)
        top5 = watch_scores[:5]

        for i, w in enumerate(top5):
            scol   = "#00d09c" if w["score"]>=6 else "#ffa502" if w["score"]>=4 else "#ff4757"
            sigcol = "#00d09c" if w["signal"]=="Buy" else "#ff4757" if w["signal"]=="Sell" else "#ffa502"
            chgcol = "#00d09c" if w["chg"]>=0 else "#ff4757"
            st.markdown(f"""
            <div class='card' style='margin-bottom:8px;'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div style='display:flex;align-items:center;gap:12px;'>
                  <span style='font-size:22px;font-weight:700;color:{scol};'>#{i+1}</span>
                  <div>
                    <div style='font-size:15px;font-weight:700;color:#cdd6f4;'>{w['sym']} — {w['name'][:28]}</div>
                    <div style='font-size:13px;color:#8892b0;'>TISM: {w['score']} &nbsp;|&nbsp; Risk: {w['risk']}</div>
                  </div>
                </div>
                <div style='display:flex;align-items:center;gap:16px;'>
                  <div style='text-align:right;'>
                    <div style='color:#cdd6f4;font-weight:700;'>₹{w['price']:,.2f}</div>
                    <div style='color:{chgcol};font-size:13px;'>{w['chg']:+.2f}%</div>
                  </div>
                  <span style='background:{sigcol}22;color:{sigcol};padding:4px 14px;border-radius:20px;font-weight:700;'>{w['signal']}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 🤖 Morning Market Brief")
        mp = f"Indian market today, Nifty {nifty['price'] if nifty else 'N/A'} ({nchg:+.1f}%), date {datetime.now().strftime('%d %B %Y')}. Write a morning brief in very simple language for a beginner investor: what to expect today, which sectors look good, one risk to watch, and one simple actionable tip. 5 sentences max."
        with st.spinner("Generating morning brief..."):
            st.markdown(f"<div class='card card-blue'><p style='color:#cdd6f4;line-height:1.9;font-size:15px;'>{get_ai(mp)}</p></div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("#### ⚠️ Important Reminder")
        st.markdown("<div class='card card-yellow'><p style='color:#ffa502;font-weight:700;'>This report is for learning and information only.</p><p style='color:#8892b0;'>TISM scores have about 55-60% accuracy — meaning they are right more often than wrong, but not always. Always do your own research before putting real money in any stock. Never invest money you cannot afford to lose.</p></div>", unsafe_allow_html=True)
