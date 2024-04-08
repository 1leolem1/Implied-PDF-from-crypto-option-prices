import pandas as pd
import os
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.lines import Line2D


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

    def find_atm(self):
        # Gets the underlying future price implied by option prices
        # I do that with an interpolation of strike and delta to find what strike has exactly 0.5 delta

        delta = 0.5
        df = self.filterfree_df

        def interp_helper(x_0, x_1, y_0, y_1, x):
            # linear interpolation
            out = y_0 + (x - x_0)*((y_1 - y_0)/(x_1-x_0))
            return out
        # calls
        row_below = df[df['delta'] < delta].sort_values(by="delta").iloc[-1]
        row_above = df[df['delta'] > delta].sort_values(by="delta").iloc[0]
        atm_call = interp_helper(x_0=row_below["delta"],
                                 x_1=row_above["delta"],
                                 y_0=row_below["strike"],
                                 y_1=row_above["strike"],
                                 x=0.5)
        # puts
        row_below = df[df['delta'] < -delta].sort_values(by="delta").iloc[-1]
        row_above = df[df['delta'] > -delta].sort_values(by="delta").iloc[0]
        atm_put = interp_helper(x_0=row_below["delta"],
                                x_1=row_above["delta"],
                                y_0=row_below["strike"],
                                y_1=row_above["strike"],
                                x=-0.5)
        atm_fwd = (atm_put + atm_call)/2
        return atm_fwd

    def find_atm_pcp(self):
        # lets try with put call parity cause previously was shit

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

    def calibrate_SABR(self):
        return 0
