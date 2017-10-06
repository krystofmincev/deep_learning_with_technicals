#Deep Leaning Code:

Applying deep learning to time sires technicals (12mill data points for 40 companies spanning 3 years). The data is saved in pickle files (/crawlercode/obj... file format [i]_2014_2017.pkl for i in [2 - 45 (no 26)]) and when loaded gives dictionaries with DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL as values. 

##Goal

Test RNNs, TRNNs, CNNs, GANs (create buy) on data. Apply multiple preprocessing steps to data, to see if preprocessing improves performance. Suggested preprocessing: 

Z scores for values across multiple companies, RSI, MACD, and other technical indicators.

Further, when implemented apply multiple visiulisation techniques to determine areas where networks perform well. Eg: Heat Map, Plotting graphs of values, detemining ideal input for Buy or Sell  

## Deep Learning for Time Series Data Papers:
Paper_1: https://arxiv.org/pdf/1701.01887.pdf

Gives a broad overview of the available deep learning approaches to time series problems

Paper_2: https://arxiv.org/pdf/1508.00317.pdf

Looks at a new kind of CNN architecture that does not require max pooling. Also, the author applies this technique to a financial training set underlying its advantages over RNNs.

https://medium.com/@TalPerry/deep-learning-the-stock-market-df853d139e02
