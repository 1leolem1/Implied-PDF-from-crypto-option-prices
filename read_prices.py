import pandas as pd
import os
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.lines import Line2D
import SABR_calibration as s
import SABR_functions as sabr


class option_prices():
    def __init__(self, name, min_vol_ba_spread=15):

        header = ["instrument", 'volume', 'open', 'extvalue', 'rho', 'theta', 'vega', 'gamma',
                  'ndelta', 'delta', 'last', 'bid_size', 'iv_bid', 'bid', 'mark', 'ask', 'iv_ask', 'ask_size']
        columns_to_transform = ['strike', 'volume', 'open', 'extvalue', 'rho', 'theta', 'vega', 'gamma',
                                'ndelta', 'delta', 'last', 'bid_size', 'iv_bid', 'bid', 'mark', 'ask', 'iv_ask', 'ask_size']

        found = False
        for file in os.listdir():
            if ".csv" in str(file) and name in file:
                self.df = pd.read_csv(file, header=0, names=header)
                self.df[['underlying', 'date', 'strike', 'type']
                        ] = self.df['instrument'].str.split('-', expand=True)

                self.df[columns_to_transform] = self.df[columns_to_transform].apply(
                    pd.to_numeric, errors='coerce')
                self.df["vol_mid"] = (self.df["iv_bid"]+self.df["iv_ask"])/2
                self.df["mark_mid"] = (self.df["bid"]+self.df["ask"])/2
                found = True

        if found == False:
            print("Error, couldn't find option price file")

        def liquidity_filering(df, spread):
            df["vol_bid_ask_spread"] = df["iv_ask"] - \
                df["iv_bid"]
            df = df[df["vol_bid_ask_spread"] < spread]
            return df

        self.filterfree_df = self.df
        self.df = liquidity_filering(self.df, spread=min_vol_ba_spread)
        self.puts = self.df[self.df["type"] == "P"]
        self.calls = self.df[self.df["type"] == "C"]
        self.underlying = self.df["underlying"].iloc[0]
        exp_date_str = self.df["date"].iloc[0]
        self.exp = dt.strptime(exp_date_str, "%d%b%y")
        self.atm = self.find_atm_pcp()
        # ASSUMES CURRENT PRICING DATE !!!! > in years tho
        self.ttm = (self.exp - dt.today()).days/365 + \
            (self.exp - dt.today()).seconds/(3600*24*365)

    def plot_bid_ask(self, puts=True, calls=True):

        plt.figure(figsize=(12, 8))
        df = self.df
        if not calls:
            df = df[df["type"] != "C"]
        if not puts:
            df = df[df["type"] != "P"]
        for option in df.iterrows():
            if not math.isnan(option[1]["iv_bid"]):
                plt.scatter(option[1]["strike"], option[1]["iv_bid"],
                            color="r")
            if not math.isnan(option[1]["iv_ask"]):
                plt.scatter(option[1]["strike"], option[1]
                            ["iv_ask"], color="c")

        legend_elements = [Line2D([0], [0], marker='o', color='cyan', label='Ask', markerfacecolor='cyan', markersize=10),
                           Line2D([0], [0], marker='o', color='red', label='Bid', markerfacecolor='red', markersize=10)]
        # Add legend with custom handles and labels
        plt.legend(handles=legend_elements, loc='best')
        plt.title(
            f"{self.underlying} options implied volatility for {self.exp} expiry", fontweight="bold")
        plt.xlabel(f"Strike (in {self.underlying}/USDT)")
        plt.ylabel(f"Implied volatility (in %)")
        plt.show()

    def find_atm_pcp(self):
        # deriving the fwd price from atm price
        df = self.filterfree_df.groupby("strike")
        found_atm_fwd = []
        for strike in df:
            if not strike[1]["mark_mid"].isna().any():
                i = strike[1]
                call = i[i["type"] == "C"]
                put = i[i["type"] == "P"]
                """
                Original PCP assuming 0 interest rate:
                Call Price - Put Price = Spot Price - Strike Price
                
                PCP if Price call price in units:
                Spot = - (Strike)/(Call - Put - 1)
                
                since option price is in units and not in USD
                """
                spot = - float(call["strike"]) / \
                    (float(call["mark_mid"]) - float(put["mark_mid"])-1)
                found_atm_fwd.append(spot)
        return round(np.mean(found_atm_fwd), 2)

    def calibrate_SABR(self, method="Newton-CG", init_values=[0.99, 1, -0.1, 0.99], number_of_tries=10):
        # Calls asks
        print("Calls asks:")

        best_params = None
        best_mse = float('inf')  # Initialize with positive infinity
        k = np.array(self.calls["strike"])
        v = np.array(self.calls["iv_ask"]) / 100

        for _ in range(number_of_tries):
            init_values = [np.random.uniform(0.01, 1),
                           1,
                           np.random.uniform(-1, 1),
                           np.random.uniform(0.01, 1)]
            [alpha, beta, rho, nu], mse = s.calibrate_SABR(strikes=k,
                                                           volatilities=v,
                                                           forward=self.atm,
                                                           TTM=self.ttm,
                                                           method=method,
                                                           init_param=init_values)
            if mse < best_mse:
                best_mse = mse
                best_params = [alpha, beta, rho, nu]
        print(f"-> Best MSE: {round(best_mse, 8)} ")
        self.SABR_call_params_asks = best_params

        # Calls bids
        print("Call bids:")

        best_params = None
        best_mse = float('inf')  # Initialize with positive infinity
        v = np.array(self.calls["iv_bid"])/100

        for _ in range(number_of_tries):
            init_values = [np.random.uniform(0.01, 1),
                           1,
                           np.random.uniform(-1, 1),
                           np.random.uniform(0.01, 1)]
            [alpha, beta, rho, nu], mse = s.calibrate_SABR(strikes=k,
                                                           volatilities=v,
                                                           forward=self.atm,
                                                           TTM=self.ttm,
                                                           method=method,
                                                           init_param=init_values
                                                           )
            self.SABR_call_params_bids = [alpha, beta, rho, nu]
            if mse < best_mse:
                best_mse = mse
                best_params = [alpha, beta, rho, nu]
        print(f"-> Best MSE: {round(best_mse, 8)} ")
        self.SABR_call_params_bids = best_params

        # Puts asks
        print("Put asks:")

        best_params = None
        best_mse = float('inf')  # Initialize with positive infinity
        k = np.array(self.puts["strike"])
        v = np.array(self.puts["iv_ask"])/100

        for _ in range(number_of_tries):
            init_values = [np.random.uniform(0.01, 1),
                           1,
                           np.random.uniform(-1, 1),
                           np.random.uniform(0.01, 1)]
            [alpha, beta, rho, nu], mse = s.calibrate_SABR(strikes=k,
                                                           volatilities=v,
                                                           forward=self.atm,
                                                           TTM=self.ttm,
                                                           method=method,
                                                           init_param=init_values)
            if mse < best_mse:
                best_mse = mse
                best_params = [alpha, beta, rho, nu]
        print(f"-> Best MSE: {round(best_mse, 8)} ")
        self.SABR_put_params_asks = best_params

        # Puts bids
        print("Put bids:")
        best_params = None
        best_mse = float('inf')  # Initialize with positive infinity
        v = np.array(self.puts["iv_bid"])/100

        for _ in range(number_of_tries):
            init_values = [np.random.uniform(0.01, 1),
                           1,
                           np.random.uniform(-1, 1),
                           np.random.uniform(0.01, 1)]
            [alpha, beta, rho, nu], mse = s.calibrate_SABR(strikes=k,
                                                           volatilities=v,
                                                           forward=self.atm,
                                                           TTM=self.ttm,
                                                           method=method,
                                                           init_param=init_values)
            if mse < best_mse:
                best_mse = mse
                best_params = [alpha, beta, rho, nu]

        print(f"-> Best MSE: {round(best_mse, 8)} ")
        self.SABR_put_params_bids = best_params

    def plot_bid_ask_SABR_calls(self):

        plt.figure(figsize=(12, 8))
        k = np.array(self.calls["strike"])
        v = np.array(self.calls["iv_ask"])/100
        x, y = np.linspace(k[0]-5000, k[-1]+5000, 1000), []

        # asks
        alpha, beta, rho, nu = self.SABR_call_params_asks
        for i in x:
            y.append(sabr.strike_volatility_SABR(k=i,
                                                 f=self.atm,
                                                 alpha=alpha,
                                                 beta=beta,
                                                 nu=nu,
                                                 rho=rho,
                                                 t=self.ttm))

        plt.plot(x, 100*np.array(y), label="Ask SABR Calibration")
        plt.scatter(k, 100*v, marker="+", color="c", label="Asks IV")
        plt.title(
            "Calibration of SABR to BTC call options' implied volatility bid and asks", fontweight="bold")
        plt.xlabel("Strike (in USD)")
        plt.grid(alpha=0.3)
        plt.ylabel("Implied vol (in %)")

        # bids
        alpha, beta, rho, nu = self.SABR_call_params_bids
        y = []
        v = np.array(self.calls["iv_bid"])/100
        for i in x:
            y.append(sabr.strike_volatility_SABR(k=i,
                                                 f=self.atm,
                                                 alpha=alpha,
                                                 beta=beta,
                                                 nu=nu,
                                                 rho=rho,
                                                 t=self.ttm))
        plt.plot(x, 100*np.array(y), label="Bid SABR Calibration")
        plt.scatter(k, 100*v, marker="+", color="orange", label="Bids IV")

        plt.axvline(self.atm, linestyle="--", linewidth=0.5,
                    label="Forward price", color="0")

        plt.legend()
        plt.show()

    def plot_bid_ask_SABR_puts(self):
        plt.figure(figsize=(12, 8))
        k = np.array(self.puts["strike"])
        v = np.array(self.puts["iv_ask"])/100
        x, y = np.linspace(k[0]-5000, k[-1]+5000, 1000), []

        # asks
        alpha, beta, rho, nu = self.SABR_put_params_asks
        for i in x:
            y.append(sabr.strike_volatility_SABR(k=i,
                                                 f=self.atm,
                                                 alpha=alpha,
                                                 beta=beta,
                                                 nu=nu,
                                                 rho=rho,
                                                 t=self.ttm))

        plt.plot(x, 100*np.array(y), label="Ask SABR Calibration")
        plt.scatter(k, 100*v, marker="+", color="c", label="Asks IV")
        plt.title(
            "Calibration of SABR to BTC put options' implied volatility bid and asks", fontweight="bold")
        plt.xlabel("Strike (in USD)")
        plt.grid(alpha=0.3)
        plt.ylabel("Implied vol (in %)")

        # bids
        alpha, beta, rho, nu = self.SABR_put_params_bids
        y = []
        v = np.array(self.puts["iv_bid"])/100
        for i in x:
            y.append(sabr.strike_volatility_SABR(k=i,
                                                 f=self.atm,
                                                 alpha=alpha,
                                                 beta=beta,
                                                 nu=nu,
                                                 rho=rho,
                                                 t=self.ttm))
        plt.plot(x, 100*np.array(y), label="Bid SABR Calibration")
        plt.scatter(k, 100*v, marker="+", color="orange", label="Bids IV")

        plt.axvline(self.atm, linestyle="--", linewidth=0.5,
                    label="Forward price", color="0")
        plt.legend()
        plt.show()

    def plot_pcp(self):

        # calibrate data first

        # option 1: Synthetic long (sell put buy calls)

        plt.figure(figsize=(12, 8))

        alpha, beta, rho, nu = self.SABR_put_params_bids
        k_p = np.array(self.puts["strike"])
        k_c = np.array(self.calls["strike"])
        x, y = np.linspace(k_p[0]-5000, k_c[-1]+5000, 1000), []
        v = np.array(self.puts["iv_bid"])/100
        for i in x:
            y.append(sabr.strike_volatility_SABR(k=i,
                                                 f=self.atm,
                                                 alpha=alpha,
                                                 beta=beta,
                                                 nu=nu,
                                                 rho=rho,
                                                 t=self.ttm))
        plt.plot(x, 100*np.array(y), label="SABR Bid Calibration", color="blue")
        plt.scatter(k_p, 100*v, marker="+", color="blue", label="Put Bids IV")

        # calls

        alpha, beta, rho, nu = self.SABR_call_params_asks
        y = []
        k = np.array(self.calls["strike"])
        v = np.array(self.calls["iv_ask"])/100
        for i in x:
            y.append(sabr.strike_volatility_SABR(k=i,
                                                 f=self.atm,
                                                 alpha=alpha,
                                                 beta=beta,
                                                 nu=nu,
                                                 rho=rho,
                                                 t=self.ttm))
        plt.plot(x, 100*np.array(y),
                 label="SABR call Ask Calibration", color="orange")
        plt.scatter(k, 100*v, marker="+", color="orange", label="Bids IV")
        plt.legend()
        plt.show()

    def price_butterflies(self, bins=2000):

        bins = bins+1  # bins is no of butterflies
        grid = np.linspace(start=np.min(self.df["strike"]),
                           stop=np.max(self.df["strike"]),
                           num=bins)  # create a grid in all options that are liquid enough
        probabilities = []
        payoff = grid[1] - grid[0]  # gonna be the same for ea bfly

        print(payoff)

        for i in range(len(grid[:-2])):

            option_1_iv = sabr.strike_volatility_SABR(k=grid[i],
                                                      f=self.atm,
                                                      alpha=self.SABR_call_params_asks[
                                                          0],
                                                      beta=self.SABR_call_params_asks[
                                                          1],
                                                      nu=self.SABR_call_params_asks[
                                                          2],
                                                      rho=self.SABR_call_params_asks[
                                                          3],
                                                      t=self.ttm)  # long so hit ask
            option_1_price = sabr.get_gk_price(w=1,
                                               forward=self.atm,
                                               term_rate=0,
                                               base_rate=0,
                                               ttm=self.ttm,
                                               vol=option_1_iv*100,
                                               strike=grid[i])
            print(f"strike={grid[i]}, p={option_1_price}")
            # sell 2 option 2
            option_2_iv = sabr.strike_volatility_SABR(k=grid[i+1],
                                                      f=self.atm,
                                                      alpha=self.SABR_call_params_bids[
                                                          0],
                                                      beta=self.SABR_call_params_bids[
                                                          1],
                                                      nu=self.SABR_call_params_bids[
                                                          2],
                                                      rho=self.SABR_call_params_bids[
                                                          3],
                                                      t=self.ttm)  # long so hit ask
            option_2_price = sabr.get_gk_price(w=1,
                                               forward=self.atm,
                                               term_rate=0,
                                               base_rate=0,
                                               ttm=self.ttm,
                                               vol=option_2_iv*100,
                                               strike=grid[i+1])
            option_3_iv = sabr.strike_volatility_SABR(k=grid[i+2],
                                                      f=self.atm,
                                                      alpha=self.SABR_call_params_asks[
                                                          0],
                                                      beta=self.SABR_call_params_asks[
                                                          1],
                                                      nu=self.SABR_call_params_asks[
                                                          2],
                                                      rho=self.SABR_call_params_asks[
                                                          3],
                                                      t=self.ttm)  # long so hit ask
            option_3_price = sabr.get_gk_price(w=1,
                                               forward=self.atm,
                                               term_rate=0,
                                               base_rate=0,
                                               ttm=self.ttm,
                                               vol=option_3_iv*100,
                                               strike=grid[i+2])

            premium = (option_1_price - 2*option_2_price +
                       option_3_price)  # both premium and payoff expressed in $

            # print(
            #     f"bfly {i}: c1 p= {round(option_1_price, 2)}, c2= {round(option_2_price, 2)}, c3= {round(option_3_price, 2)} -> t ={premium}")
            probabilities.append(premium/payoff)

        plt.figure(figsize=(12, 8))
        plt.plot(grid[:-2], -0.001*np.array(probabilities))
        plt.xlabel("Strike (in $)")
        plt.title(
            f"Implied PDF of {self.underlying} options expiring {self.exp}", fontweight="bold")
        plt.axhline(0, linewidth=1, color="0")
        plt.grid(alpha=0.3)
        plt.show()
