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

            plt.figure(figsize=(10, 6))
            plt.plot(k_range, sabr_vols, label='SABR Model', color='blue')
            plt.scatter(k, v, color='red',
                        label='Market Implied Volatilities')
            plt.xlabel('Strike Price')
            plt.ylabel('Implied Volatility')
            plt.title('SABR Model Calibration to Market Data')
            plt.legend()
            plt.grid(alpha=0.3)
            plt.show()
