import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import read_prices as rp

st.title("SABR Calibration on crypto calls")

st.write("This app calibrates the SABR model to market option prices for a selected crypto asset and expiry date using Streamlit. Deribit API. A new version will soon add ETH and pddf implied by market prices.")
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 0.8em;
        color: #888;
    }
    </style>
    <div class="footer">
      dev by <a href="https://github.com/1leolem1/">LeoLem</a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Asset selection
asset = st.selectbox("Select Asset", ["BTC"])

# Get available expiries
try:
    expiries = rp.get_available_options(underlying=asset)
except Exception as e:
    st.error(f"Error fetching expiries: {e}")
    st.stop()

expiry = st.selectbox("Select Expiry", expiries)

if st.button("Calibrate SABR"):
    try:
        atm = rp.get_forward_price(expiry, underlying="BTC")
        print(f"ATM forward price: {atm}")

        option_data = rp.get_option_data(date=expiry, underlying="BTC")

        a = rp.option_prices(K=list(option_data["strike"]),
                             ImpliedVol=list(option_data["mark_iv"]),
                             date=expiry, atm=atm)

        a.calibrate_SABR()

        # Plot the SABR model fits
        a.plot_sabr()
        st.pyplot(plt)

    except Exception as e:
        st.error(f"Error: {e}")
