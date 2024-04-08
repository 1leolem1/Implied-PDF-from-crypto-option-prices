import pandas as pd
from scipy.stats import norm
import numpy as np
from scipy.optimize import minimize


def strike_volatility_SABR(k, f, alpha, beta, nu, rho, t):
    """  
    f: forward rate
    k: strike 
    t: time to maturity (in years) 
    """
    z = (nu/alpha)*(f*k)**((1-beta)/2)*np.log(f/k)
    x = np.log((np.sqrt(1-2*rho*z+z**2)+z-rho)/(1-rho))  # x(z)
    num = alpha*(1+(((1-beta)**2)/24)*(alpha**2/((f*k)**(1-beta))) + 0.25 *
                 (rho*beta*nu*alpha)/((f*k)**((1-beta)/2))+((2-3*rho**2)/24)*nu**2) * t
    denum = (f * k) ** ((1 - beta) / 2) * (1 + ((1 - beta) ** 2 / 24) *
                                           (np.log(f / k) ** 2) + ((1 - beta) ** 4 / 1920) * (np.log(f / k) ** 4))
    vol_bs = (num/denum) * (z/x)
    return vol_bs


def atm_forward(spot, term_rate, base_rate, ttm):
    """
    spot: in dom currency
    term_rate and base_rate expressed as percentage points (0.01 is 1%)
    time: in days assuming 365 days a year. This figure simplifies calculations for TTM and FX trades almost 24/7
    """
    return spot * np.exp((term_rate - base_rate)*(ttm/365))


def get_gk_price(w, forward, term_rate, base_rate, ttm, vol, strike):
    """
    Gets the price of a call option using the Garman Kohlhagen formula

    Parameters:

    w: type of option: 1 for a call and -1 for a put
    spot: Current price of the underlying asset
    term_rate: Term risk-free rate
    base_rate: Base risk-free rate
    ttm: Time to maturity
    vol: Volatility of the underlying asset
    strike: Strike price of the option
    Return value: Price of call option

    """
    T = ttm/365  # from days to years -> calculated using Time Delta

    d1 = (np.log(forward / strike) + (0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    d2 = (np.log(forward / strike) - (0.5 * vol ** 2) * T) / (vol * np.sqrt(T))

    value = w*np.exp(-term_rate) * \
        (forward*norm.cdf(w*d1) - strike*norm.cdf(w*d2))
    return value


def get_strike(w, delta, forward, term_rate, base_rate, ttm, vol, minimum_tick):
    """
    Gets the strike of a call option
    w: type of option: 1 for a call and -1 for a put
    spot: in base currency
    term_rate and base_rate expressed as percentage points (0.01 is 1%)
    time: in days assuming 365 days a year
    vol: same format as rate
    """

    guess = 0.01
    threshold = 0.01
    a = 0
    b = 0
    computed_delta = 0

    while np.abs(computed_delta - delta) > threshold:
        a = get_gk_price(w, forward+minimum_tick, term_rate,
                         base_rate, ttm, vol, guess)
        b = get_gk_price(w, forward-minimum_tick, term_rate,
                         base_rate, ttm, vol, guess)
        computed_delta = (a-b)/(2*minimum_tick)  # Central difference
        guess += minimum_tick
    return guess


def get_market_volatilty_surface(df, term_rate, base_rate, spot, start=0, stop=30*365, save=False):
    """ 
    input format:

    TTM ATM 25DCall 25DPut  10DCall 25DPut TTM(days)
    1D  11.1 10.1    14.52  11.81   9.65    1
    1W  11.5 11.5    15.10  10.45   9.55    7
                        ...
    30Y  11.5 11.5   15.10  14.44  12.48   10950

    output format df:

    Strike  TTM  Vol    Fwd
    111.51  1   10.84   142.65
    165.15  1   10.57   142.65
    ...
    50.12   10950   12.65   53.18

    """

    # Only take wantyed part of DF
    df = df.loc[(df["TTM(days)"] >= start) & (df["TTM(days)"] <= stop)]

    delta = [0.5, 0.25, -0.25, 0.10, -0.10]
    w = [1, 1, -1, 1, -1]  # option sign

    x, y, z, f = [], [], [], []  # Strike, TTM, Implied Vol -> To plot

    df = df.drop(['TTM'], axis=1)

    for index, row in df.iterrows():
        TTM = row[-1]
        FWD = atm_forward(ttm=TTM, term_rate=term_rate,
                          base_rate=base_rate, spot=spot)
        print(TTM)
        for i in range(len(row[:-1])):
            implied_volatility = row[i]/100
            strike = get_strike(w=w[i], delta=delta[i], forward=FWD, term_rate=term_rate,
                                base_rate=base_rate, ttm=TTM, vol=implied_volatility, minimum_tick=0.01)
            x.append(strike)
            y.append(TTM)
            z.append(implied_volatility)
            f.append(FWD)

    out = pd.DataFrame([x, y, z, f]).T
    out.columns = ['Strike', 'TTM', 'Vol', 'Fwd']

    if save:
        out.to_csv("Strike Vol Surface.csv", index=False)
    return out


def FFVI(t1, v1, t2, v2, x):
    """
    x is the unknown between t1 and t2
    v1 is the volatility at t1  
    """
    a = (t2*(x-t1))/(x*(t2-t1))*(v2)**2
    b = (t1*(t2-x))/(x*(t2-t1))*(v1)**2
    out = np.sqrt(a+b)
    return out


def mse_function(params):
    alpha, beta, rho, nu = params
    mse = 0
    for i in range(len(STRIKEs)):
        temp = (INTERP_SMILE[i]-pf.strike_volatility_SABR(k=STRIKEs[i],
                f=FORWARD, alpha=alpha, beta=beta, nu=nu, rho=rho, T=4467/365))**2
        mse += temp
    return mse


def compute_delta(w, strike, forward, term_rate, base_rate, ttm, vol, minimum_tick=0.01):

    a = get_gk_price(w, forward+minimum_tick, term_rate,
                     base_rate, ttm, vol, strike)
    b = get_gk_price(w, forward-minimum_tick, term_rate,
                     base_rate, ttm, vol, strike)
    computed_delta = (a-b)/(2*minimum_tick)
    return computed_delta


def strike_volatility_SABR(k, f, alpha, beta, nu, rho, T):
    """  
    f: forward rate
    k: strike
    t: time to maturity (in years)
    """
    z = (nu/alpha)*(f*k)**((1-beta)/2)*np.log(f/k)
    x = np.log((np.sqrt(1-2*rho*z+z**2)+z-rho)/(1-rho))  # x(z)
    num = alpha*(1+(((1-beta)**2)/24)*(alpha**2/((f*k)**(1-beta))) + 0.25 *
                 (rho*beta*nu*alpha)/((f*k)**((1-beta)/2))+((2-3*rho**2)/24)*nu**2) * T
    denum = (f * k) ** ((1 - beta) / 2) * (1 + ((1 - beta) ** 2 / 24) *
                                           (np.log(f / k) ** 2) + ((1 - beta) ** 4 / 1920) * (np.log(f / k) ** 4))
    vol_bs = (num/denum) * (z/x)
    return vol_bs


def find_optimal_rho_nu(method='L-BFGS-B'):
    ALPHA = 0.06
    BETA = 1
    RHO = -0.155
    NU = 0.417
    PARAMS = {"alpha": {"x0": ALPHA, "lbub": [0.001, 1]},
              "beta": {"x0": BETA, "lbub": [1, 1]},
              "rho": {"x0": RHO, "lbub": [-1, 1]},
              "nu": {"x0": NU, "lbub": [0.001, 1]}, }

    # calibrate rho, nu:

    x0 = [param["x0"] for key, param in PARAMS.items()]
    bounds = [param["lbub"] for key, param in PARAMS.items()]

    result = minimize(mse_function, x0, tol=1e-7, method=method,
                      options={'maxiter': 1e9}, bounds=bounds)

    return result.x
