import matplotlib.pyplot as plt
from read_prices import option_prices


def main():
    a = option_prices(name="BTC-26APR")
    a.plot_bid_ask()


if __name__ == "__main__":
    main()
