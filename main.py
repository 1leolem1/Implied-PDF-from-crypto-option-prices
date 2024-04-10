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
    a = option_prices(name="BTC-26APR")
    a.calibrate_SABR(method='L-BFGS-B')
    a.price_butterflies()


if __name__ == "__main__":
    main()
