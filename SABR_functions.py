import pandas as pd
from scipy.stats import norm
import numpy as np


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
