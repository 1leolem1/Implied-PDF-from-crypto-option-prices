This project aims to take a CSV extract of the option prices and output an implied Probability Density Function from the option prices. Here my input is a simple extract from Deribit. On the top right, you can see the CSV file. I want to generate this PDF using this CSV file. 

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/8069d1f4-9916-4b7c-9550-8c49e2c0b2a4)


<h3>Methodology</h3>

Morgan Stanley explains how assuming risk-neutral probabilities you can use butterfly options strategies to estimate the odds of the underlying expiring in this range. 

https://www.morganstanley.com/content/dam/msdotcom/en/assets/pdfs/Options_Probabilities_Exhibit_Link.pdf

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/2370b5b7-6878-46ef-a3ae-6595cc503cc5)

Ignoring the premium payment, the average payoff in the butterfly range is: max_payoff/2 

If you look at football betting quotes, the likelihood of the event happening is: 1/payoff 

Let's look at a sample example: 
Man City are playing Luton at home (which they are this weekend), they have a payoff of 1.1 
Their implied odds of winning are 1/1.1 ~ 91% (includes the premium charged by the bookmaker)

It's the same thing in this case. You pay a premium p betting the stock will expire in the butterfly range. Using simple geometry, your average payoff will be 1/2 * range_width.

The implied odds for this range are given by: premium / average payoff

Using bids and asks marks in the CSV file, it is easy to price butterflies. However, this isn't accurate enough since there are insufficient data points. I will calibrate a SABR stochastic volatility model to the mid-price, recreating a volatility smile. However, this strategy might not be representative and I might want to calibrate the model to the bids and asks to include trading costs.

SABR Stochastic volatility (plot below) is much better than interpolation since we won't have an overfitting problem with it. And since our code takes a lot of option prices, it is better to avoid overfitting data. 
![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/27fabed8-ce70-49d5-9b2e-6727fab1f79b)

I am still far from finished with this project, but I wanted to make an initial commit.

