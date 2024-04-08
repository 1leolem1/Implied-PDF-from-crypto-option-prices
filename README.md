This project aims to take a CSV extract of the option prices and output an implied Probability Density Function from the option prices. Here my input is a simple extract from Deribit. On the top right, you can see the CSV file. I want to be able to quickly generate this PDF using this CSV file. 

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/8069d1f4-9916-4b7c-9550-8c49e2c0b2a4)


The method used for this project is described in the file below. 

https://www.morganstanley.com/content/dam/msdotcom/en/assets/pdfs/Options_Probabilities_Exhibit_Link.pdf

Using bids and asks marks in the CSV file, we can easily price our butterflies. If this data doesn't give enough accuracy, I will calibrate a SABR stochastic volatility model to price options.

![image](https://github.com/1leolem1/Implied-PDF-from-crypto-option-prices/assets/58358116/9b98c48e-cc81-4e75-a36c-3503838edf24)


I am still far from finished with this project, but wanted to make an initial commit.
