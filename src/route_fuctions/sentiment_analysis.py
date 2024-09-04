from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# * Sample text for sentiment analysis
text = """Worth 
noting as 
reference 
is made to 
the 
Ministry’s 
name
"""

# * Initialize VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

blob = TextBlob(text)

# * Perform sentiment analysis
sentiment_score = sid.polarity_scores(text)

# * Print sentiment score
print(sentiment_score)

# * Perform sentiment analysis
sentiment = blob.sentiment

# * Print sentiment
print(sentiment)
