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

    # test data - conservative vol smile in a risk adverse market

    K = [25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000, 65000, 70000]
    ImpliedVol = [0.98, 0.84, 0.74, 0.65, 0.58, 0.55, 0.57, 0.65, 0.79, 0.94]

    a = option_prices(K, ImpliedVol, date="26Jan26", atm=49950)
    print(a)

    a.calibrate_SABR()
    a.plot_sabr()


if __name__ == "__main__":
    main()
