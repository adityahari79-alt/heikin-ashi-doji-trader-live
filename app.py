import streamlit as st
import threading
from datetime import datetime
from upstox_heikin_ashi_doji_trader import UpstoxLiveHeikinAshiDojiTrader

st.set_page_config(page_title="Upstox Heikin Ashi Doji Streamlit", layout="wide")
st.title("Upstox Heikin Ashi Doji Live Detector")

# UI for credentials and instrument
with st.form("credentials_form"):
    api_key = st.text_input("Upstox API Key", type="password")
    api_secret = st.text_input("Upstox API Secret", type="password")
    redirect_uri = st.text_input("Redirect URI", value="http://localhost")
    instrument_token = st.text_input("Instrument Token (e.g. NSE_INDEX|Nifty 50)", value="NSE_INDEX|Nifty 50")
    submit = st.form_submit_button("Start Live Detection")

if 'trader_thread' not in st.session_state:
    st.session_state.trader_thread = None
if 'doji_data' not in st.session_state:
    st.session_state.doji_data = []

table_placeholder = st.empty()

def streamlit_doji_callback(minute, ha_candle):
    row = {
        "Time": minute.strftime("%Y-%m-%d %H:%M"),
        "HA Open": ha_candle["open"],
        "HA High": ha_candle["high"],
        "HA Low": ha_candle["low"],
        "HA Close": ha_candle["close"],
        "Volume": ha_candle["volume"],
    }
    st.session_state.doji_data.append(row)
    # Keep only the latest 100
    st.session_state.doji_data = st.session_state.doji_data[-100:]

def run_trader(api_key, api_secret, redirect_uri, instrument_token):
    trader = UpstoxLiveHeikinAshiDojiTrader(
        api_key=api_key,
        api_secret=api_secret,
        redirect_uri=redirect_uri,
        instrument_token=instrument_token,
        on_doji_detected=streamlit_doji_callback
    )
    trader.run()

if submit and api_key and api_secret and redirect_uri and instrument_token:
    if st.session_state.trader_thread is None or not st.session_state.trader_thread.is_alive():
        st.session_state.doji_data = []
        t = threading.Thread(
            target=run_trader,
            args=(api_key, api_secret, redirect_uri, instrument_token),
            daemon=True
        )
        t.start()
        st.session_state.trader_thread = t
        st.success("Trader started! Please complete authentication in the terminal/console.")

st.subheader("Detected Doji Heikin Ashi Candles")
table_placeholder.table(st.session_state.doji_data)