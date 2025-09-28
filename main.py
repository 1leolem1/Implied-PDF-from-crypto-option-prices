import matplotlib.pyplot as plt
from read_prices import option_prices
import read_prices as rp


"""
methods for calibration:

'TNC'
'L-BFGS-B'
'Nelder-Mead'

Last one seems to be quite innacurate tho
"""


def main():

    # test data - conservative vol smile in a risk adverse market

    print(rp.get_available_options("BTC"))

    expiry = "27MAR26"  # for example, choose expiry "26Dec25"
    min_bid_ask_spread = 10  # set a minimum bid-ask spread threshold

    atm = rp.get_forward_price(expiry, underlying="BTC")
    print(f"ATM forward price: {atm}")

    option_data = rp.get_option_data(date=expiry, underlying="BTC")

    a = option_prices(K=list(option_data["strike"]),
                      ImpliedVol=list(
        option_data["mark_iv"]),
        date=expiry, atm=atm)

    a.calibrate_SABR()

    # Plot the SABR model fits
    a.plot_sabr()


if __name__ == "__main__":
    main()
