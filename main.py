import matplotlib.pyplot as plt
from read_prices import option_prices

"""
methods for calibration:

'TNC'
'L-BFGS-B'
'Nelder-Mead'

Last one seems to be quite innacurate tho
"""


def main():
    # a = option_prices(name="BTC-26APR")
    # a = option_prices(name="BTC-27SEP")
    # a = option_prices(name="BTC-27DEC")
    a = option_prices(name="ETH-27SEP")

    a.calibrate_SABR(method='L-BFGS-B')
    a.plot_bid_ask_SABR_calls()
    a.plot_pdf_cdf()


if __name__ == "__main__":
    main()
