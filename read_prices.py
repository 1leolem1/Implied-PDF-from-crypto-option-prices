import pandas as pd
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import requests as req
import SABR_functions as sabr


class option_prices():
    def __init__(self, K, ImpliedVol, date, atm):
        """
        K is a list of strikes
        ImpliedVol is a list of implied volatilities for each strike
        Strikes can be moneyess (delta) Doesn't have to be strikes        
        Implied vol in pct form (50 for 50%)
        date in format "26Jan24" 

        """
        self.atm = atm
        self.df = pd.DataFrame({"strikes": K, "impliedVols": ImpliedVol})
        self.exp = dt.strptime(date, "%d%b%y")

        # ASSUMES CURRENT PRICING DATE !!!! > in years tho
        self.ttm = (self.exp - dt.today()).days/365 + \
            (self.exp - dt.today()).seconds/(3600*24*365)

    def __repr__(self):
        return f"Option Prices for expiry {self.exp.strftime('%d-%b-%Y')} - > TTM {self.ttm} years with {len(self.df)} strikes and ATM forward {self.atm} USD"

    def calibrate_SABR(self, initial_guess=None):
        import scipy.optimize as opt

        if initial_guess is None:
            # initial guess: [alpha, beta, rho, nu]
            initial_guess = [0.2, 0.5, 0.0, 0.2]

        strikes = self.df["strikes"].values
        market_vols = np.array(self.df["impliedVols"])

        def objective(params):
            alpha, beta, rho, nu = params
            model_vols = np.array([
                sabr.strike_volatility_SABR(
                    k=K, f=self.atm, alpha=alpha, beta=beta, rho=rho, nu=nu, t=self.ttm)
                for K in strikes
            ])
            return np.sum((model_vols - market_vols) ** 2)

        bounds = [(1e-6, None), (0.0, 1.0), (-0.999, 0.999), (1e-6, None)]
        result = opt.minimize(objective, initial_guess, bounds=bounds)

        if result.success:
            self.SABR_params = result.x
            print("Calibration successful.")
            print(
                f"Parameters: alpha = {result.x[0]:.4f}, beta = {result.x[1]:.4f}, rho = {result.x[2]:.4f}, nu = {result.x[3]:.4f}")
        else:
            print("Calibration failed:", result.message)

    def plot_sabr_withoutcalibration(self, alpha, beta, rho, nu):
        k = self.df["strikes"]
        v = self.df["impliedVols"]

        v = np.array(self.df["impliedVols"])

        k_range = np.linspace(min(k)*0.8, max(k)*1.2, 100)
        sabr_vols = [sabr.strike_volatility_SABR(k=ki, f=self.atm, alpha=alpha,
                                                 beta=beta, nu=nu, rho=rho, t=self.ttm) for ki in k_range]

        plt.figure(figsize=(10, 6))
        plt.plot(k_range, sabr_vols, label='SABR Model', color='blue')
        plt.scatter(k, v, color='red',
                    label='Market Implied Volatilities')
        plt.xlabel('Strike Price')
        plt.ylabel('Implied Volatility')
        plt.title('SABR Model with Given Parameters')
        plt.legend()
        plt.grid()
        plt.show()

    def plot_sabr(self):
        if not hasattr(self, 'SABR_params'):
            print("! No SABR parameters found. Please calibrate SABR first !")
        else:
            alpha, beta, rho, nu = self.SABR_params
            k = self.df["strikes"]
            v = self.df["impliedVols"]

            k_range = np.linspace(min(k)*0.8, max(k)*1.2, 100)
            sabr_vols = [sabr.strike_volatility_SABR(k=ki, f=self.atm, alpha=alpha,
                                                     beta=beta, nu=nu, rho=rho, t=self.ttm) for ki in k_range]

            plt.figure(figsize=(10, 6), dpi=150)
            plt.plot(k_range, sabr_vols, label='SABR Model', color='blue')
            plt.scatter(k, v, color='red', label='Market Implied Volatilities')
            plt.axvline(self.atm, color='black', linestyle='--', alpha=0.6,
                        label=f'ATM (USDC${self.atm:,.2f})')
            plt.xlabel('Strike Price')
            plt.ylabel('Implied Volatility')
            plt.title(
                f'SABR Calibration to options expiring {self.exp.strftime("%d-%b-%Y")}', fontweight='bold')
            plt.legend()
            plt.grid(alpha=0.3)
            plt.show()


def get_forward_price(expiry, underlying="BTC"):
    """
    Retrieves the dated future price for the given underlying and expiry date.
    It fetches all available future instruments for the underlying, filters those
    matching the given expiry, and returns the last traded price.
    """
    # Retrieve future instruments for the underlying.
    instruments_url = f"https://www.deribit.com/api/v2/public/get_instruments?currency={underlying}&kind=future&expired=false"
    response = req.get(instruments_url)
    data = response.json()

    if "result" not in data or not data["result"]:
        raise ValueError(
            "No available future instruments found for the given underlying.")

    # Filter instruments with the specified expiry in the instrument name.
    instruments = []
    for inst in data["result"]:
        # Expected instrument format example: "BTC-26JAN24" or "BTC-26JAN24-..."
        parts = inst["instrument_name"].split("-")
        if len(parts) >= 2 and parts[1].upper() == expiry.upper():
            instruments.append(inst)

    if not instruments:
        raise ValueError("No future instruments found for the given expiry.")

    # Pick the first instrument as the dated future.
    instrument_name = instruments[0]["instrument_name"]

    # Retrieve the summary to get the last traded price.
    summary_url = f"https://www.deribit.com/api/v2/public/ticker?instrument_name={instrument_name}"
    summary_response = req.get(summary_url)
    summary_data = summary_response.json()
    if "result" not in summary_data or "last_price" not in summary_data["result"]:
        raise ValueError(
            "No price data found for the dated future instrument.")

    future_price = summary_data["result"]["last_price"]
    return future_price


def get_available_options(underlying="BTC", kind="C"):
    """
    Retrieves available expiry dates for the given underlying and option type.
    """
    url = f"https://www.deribit.com/api/v2/public/get_instruments?currency={underlying}&kind=option&expired=false"
    response = req.get(url)
    data = response.json()
    if "result" in data and data["result"]:
        expiry_set = set()
        for inst in data["result"]:
            parts = inst["instrument_name"].split("-")
            if len(parts) >= 2:
                expiry_set.add(parts[1])
        expiries = sorted(list(expiry_set))
        return expiries
    else:
        raise ValueError("No available options instruments found.")


def get_option_data(date="26Jan24", underlying="BTC", kind="C"):
    base_url = "https://www.deribit.com/api/v2/public"

    # 1. Get all instruments
    instruments_url = f"{base_url}/get_instruments"
    params = {"currency": underlying, "kind": "option"}
    response = req.get(instruments_url, params=params).json()
    if "result" not in response:
        raise ValueError(f"Error from Deribit API: {response}")
    instruments = response["result"]

    # 2. Robust filter by expiry and option type
    filtered = [
        ins for ins in instruments
        if date.upper() in ins["instrument_name"].upper()
        and ins["option_type"][0].upper() == kind.upper()
    ]

    if not filtered:
        raise ValueError(
            f"No options found for {underlying} {kind} expiring {date}")

    option_data = []

    # 3. Get order book for each option
    for ins in filtered:
        instrument_name = ins["instrument_name"]
        ob_url = f"{base_url}/get_order_book"
        ob = req.get(ob_url, params={
                     "instrument_name": instrument_name}).json()
        if "result" not in ob:
            continue
        ob_data = ob["result"]

        option_data.append({
            "instrument": instrument_name,
            "strike": ins.get("strike"),
            "mark_iv": ob_data.get("mark_iv"),
            "bid_iv": ob_data.get("bid_iv"),
            "ask_iv": ob_data.get("ask_iv")
        })

    if not option_data:
        raise ValueError(
            "No order book data returned. Check date formatting (e.g., 29SEP25).")

    # 4. Build DataFrame
    df = pd.DataFrame(option_data).sort_values("strike").reset_index(drop=True)
    return df
