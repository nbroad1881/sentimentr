# Sentimentr

A flask app to display the sentiments of various news titles as analyzed in the senti-news package.  Specifically, each 
headline mentions one presidential candidate in the US 2020 election. Recent headlines from CNN, Fox News, and New
 York Times are analyzed using sentiment analysis tools such as:
* [VADER](https://github.com/cjhutto/vaderSentiment) 
* [TextBlob](https://textblob.readthedocs.io/en/dev/) 
* LSTM
* BERT


The app is hosted at https://sentimentr.nmbroad.com. It includes an interactive graph to see the scores of recent articles for each candidate, separated by news group and sentiment analysis model.

The app works by making requests to the database to pull recent scores and then plot them using Chart.js.  The app is also in charge of periodically looking for recently published articles using Celery.