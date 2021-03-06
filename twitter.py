
from model import Base, Tweet
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import unicodedata

import random, string
import tweepy
from textblob import TextBlob
import json, re

engine = create_engine('sqlite:///tweets.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Step 1 - Authenticate
consumer_key= 'COMSUMER_KEY'
consumer_secret= 'CONSUMER_SECRET'

access_token='ACCESS_TOKEN'
access_token_secret='ACCESS_TOKEN_SECRET'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# query string
query = 'INDvSA'
max_tweets = 50

# list of objects containing tweet's data
tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]


# clean tweet text
def clean_tweet(tweet):
        return ' '.join(re.sub("(RT) | ([^0-9A-Za-z \t])|(\w+:\/\/\S+) | (http)", " ", tweet).split())


# calculate sentiment type as positive, negative or neutral upon text of tweet
def tweet_sentiment(tweet_text):
    testimonial = TextBlob(tweet_text)
    polarity = testimonial.sentiment.polarity
    if (polarity >= 0.2):
        return 'positive'
    elif ((polarity < 0.3) and (polarity >= 0)):
        return 'neutral'
    else:
        return 'negative'


# Store tweets with their sentiments in a database
def store_tweets():
    for tweet in tweets:
        tweet_id = tweet.id
        tweet_text = clean_tweet(tweet.text)
        tweet_text = unicodedata.normalize('NFKD', tweet_text).encode('ascii','ignore')
        sentiment = tweet_sentiment(tweet_text)
        if(session.query(Tweet).filter_by(tweet_id = tweet_id).scalar() is None):
            newTweet = Tweet(tweet_id=tweet_id, tweet_text= tweet_text, sentiment= sentiment)
            session.add(newTweet)
            session.commit()
