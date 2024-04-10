This project aims to take a CSV extract of the option prices and output an implied Probability Density Function from the option prices. Here my input is a simple extract from Deribit. On the top right, you can see the CSV file. I want to generate this PDF using this CSV file. 

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/8069d1f4-9916-4b7c-9550-8c49e2c0b2a4)


<h3>Methodology</h3>

Morgan Stanley explains how assuming risk-neutral probabilities you can use butterfly options strategies to estimate the odds of the underlying expiring in this range. 

https://www.morganstanley.com/content/dam/msdotcom/en/assets/pdfs/Options_Probabilities_Exhibit_Link.pdf

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/2370b5b7-6878-46ef-a3ae-6595cc503cc5)

Ignoring the premium payment, the average payoff in the butterfly range is: max_payoff/2 

If you look at football betting quotes, the likelihood of an event happening is: 1/payoff 

Let's look at a sample example: 
Man City are playing Luton at home (which they are this weekend), they have a payoff of 1.1 
Their implied odds of winning are 1/1.1 ~ 91% (including the premium charged by the bookmaker)

It's the same thing in this case. You pay a premium p betting the stock will expire in the butterfly range. The average payoff will be max_payoff/2 = bfly_width/2.

The implied odds for this range are given by: premium / average payoff

Using bids and asks marks in the CSV file, it is easy to price butterflies. However, this isn't accurate enough since there are insufficient data points. I will calibrate a SABR stochastic volatility model to the mid-price, recreating a volatility smile. However, this strategy might not be representative and I might want to calibrate the model to the bids and asks to include trading costs.

Given the number of option prices we're dealing with, SABR stochastic volatility (plot below) is much better than interpolation since we won't risk overfitting our option prices.  
![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/35f8f09b-b9b7-4b0c-a463-ae0e93341de7)



<h4>Data processing</h4>

The options data file doesn't include the price of the underlying future, which means we need to extract it from the option prices.
Assuming zero rates, the Put-Call Parity (PCP) states:

Call_Price - Put_Price = Underlying_Price - Strike_Price 

Since in crypto our Call and Put prices are expressed in units of underlying, we can write PCP as:

(Call_Price - Put_Price)Underlying_Price = Underlying_Price - Strike_Price 

Solving for Spot:

Underlying = - (Strike)/(Call - Put - 1)

Using this formula on all option pairs and averaging the Underlying yields a quite strong approximation of the underlying future price.  



<h4>Resulting PDF</h4>

Below is what I came up with thanks to my .price_butterfly() function. Even if it seems wrong for such maturity, it looks like a proper PDF so I'm already pretty proud. 

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/c924d9f6-dea3-4f9b-a464-3f540e3d813b)

I still want to finish a few things such as creating a CDF to get a specific probability based on a range, and I will make adjustments to ensure everything is correct in this project. 
