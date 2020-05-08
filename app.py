import keys

import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob

import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

class TwitterClient(object):
    
    def __init__(self): 
            consumer_key = keys.c_key
            consumer_secret = keys.c_secret
            access_token = keys.a_key
            access_token_secret = keys.a_secret

            try: 
                self.auth = OAuthHandler(consumer_key, consumer_secret) 
                self.auth.set_access_token(access_token, access_token_secret) 

                self.api = tweepy.API(self.auth)

            except: 
                print("Error: Authentication Failed") 
                
    def clean_tweet(self, tweet): 
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 

    def get_tweet_sentiment(self, tweet): 
        analysis = TextBlob(self.clean_tweet(tweet)) 
        if analysis.sentiment.polarity > 0: 
            return 'positive'
        elif analysis.sentiment.polarity == 0: 
            return 'neutral'
        else: 
            return 'negative'
    
    def get_tweets(self, query, count = 10): 
         
        tweets = [] 
  
        try: 
            fetched_tweets = self.api.search(q = query, count = count) 
   
            for tweet in fetched_tweets: 
             
                parsed_tweet = {} 
   
                parsed_tweet['text'] = tweet.text 
    
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text) 
  
                if tweet.retweet_count > 0: 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
  
            return tweets 
  
        except tweepy.TweepError as e: 
            print("Error : " + str(e)) 

def main(): 

    api = TwitterClient() 

    tweets = api.get_tweets(query = 'coronavirus', count = 200) 

    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 

    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 

    @app.route('/positive', methods=['GET'])
    def positive():
        return jsonify(ptweets)

    @app.route('/negative', methods=['GET'])
    def negative():
        return jsonify(ntweets)
    
    app.run()
  
if __name__ == "__main__": 

    main()
