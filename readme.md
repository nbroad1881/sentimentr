# Sentimentr

A flask app to display the sentiments of various news titles as analyzed in the senti-news package.  Specifically, each 
headline mentions one presidential candidate in the US 2020 election. Recent headlines from CNN, Fox News, and New
 York Times will be analyzed using various sentiment analysis tools such as:
* VADER (Valence Aware Dictionary and sEntiment Reasoner)
* TextBlob 
* LSTM trained on IMBD, Yelp, and Amazon reviews
* BERT trained on hand-labeled news headlines

