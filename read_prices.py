import pandas as pd
import os
from datetime import datetime as dt
import matplotlib.pyplot as plt
import math
from matplotlib.lines import Line2D


class option_prices():
    def __init__(self, name):

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

                found = True

        if found == False:
            print("Error, couldn't find option price file")

        self.puts = self.process_puts()
        self.calls = self.process_calls()
        self.underlying = self.df["underlying"][0]
        self.exp = self.df["date"][0]

    def process_puts(self):
        df = self.df
        return df[df["type"] == "P"]

    def process_calls(self):
        df = self.df
        return df[df["type"] == "C"]

    def plot_bid_ask(self, puts=True, calls=True):

        plt.figure(figsize=(12, 8))

        df = self.df

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
        plt.xlabel(f"Strike (in USDT/{self.underlying})")
        plt.ylabel(f"Implied volatility (in %)")
        plt.show()
