This projects aims to take a CSV extract of the option prices and output an implied Probability Density Function from the option prices.

The method used for this project is the one from the pdf file below. 

https://www.morganstanley.com/content/dam/msdotcom/en/assets/pdfs/Options_Probabilities_Exhibit_Link.pdf


Using bid and asks, we first interpolate the implied volatility data by calibrating a SABR stochastic volatility model to then price our butterfly spreads.

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/9b98c48e-cc81-4e75-a36c-3503838edf24)


I am still far from finished in this project, but wanted to do an initial commit.
