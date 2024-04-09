import SABR_functions as sabr
from scipy.optimize import minimize


def calibrate_SABR(strikes, volatilities, forward, TTM, method='Nelder-Mead'):
    # strikes and vol

    def mse_function(params):
        # mean squared error
        alpha, beta, rho, nu = params
        mse = 0
        for i in range(len(strikes)):
            temp = (volatilities[i]-sabr.strike_volatility_SABR(k=strikes[i],
                    f=forward, alpha=alpha, beta=beta, nu=nu, rho=rho, t=TTM))**2
            mse += temp
        return mse

    def find_optimal_rho_nu(method=method):

        ALPHA = 0.03
        BETA = 1
        RHO = -0.9
        NU = 0.1

        PARAMS = {"alpha": {"x0": ALPHA, "lbub": [0.001, 5]},
                  "beta": {"x0": BETA, "lbub": [1, 1]},
                  "rho": {"x0": RHO, "lbub": [-0.99, 0.99]},
                  "nu": {"x0": NU, "lbub": [0.001, 10]}, }

        # calibrate rho, nu:

        x0 = [param["x0"] for key, param in PARAMS.items()]
        bounds = [param["lbub"] for key, param in PARAMS.items()]

        result = minimize(mse_function, x0, tol=1e-7, method=method,
                          options={'maxiter': 1e9}, bounds=bounds)

        print(f"Calibration MSE: {mse_function(result.x)}")
        return result.x

    if len(strikes) != len(volatilities):
        print("! strike and volatilities not of same length !")
        raise ValueError

    ALPHA, BETA, RHO, NU = find_optimal_rho_nu()

    return ALPHA, BETA, RHO, NU
