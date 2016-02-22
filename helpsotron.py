#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy, re, random, sys

# keys are defined in twitter_secrets.py
from twitter_secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# filename for a list of tweets that the bot has posted
tweets_list = "/Users/shammack/twitterbots/stale_ass_tweets.txt"

class Tweet_with_id(object):
	# define a class for a tweet to post plus the ID of the original
	# tweet from which it's derived
	def __init__(self, tweet, id):
		self.tweet = tweet
		self.id = id

def update_list(sentence):
	# write to a list of things that have been tweeted before.
	stale_tweets = open(tweets_list, 'a')
	stale_tweets.write(sentence + '\n')
	stale_tweets.close()

#def check_list(sentence):
	# check the list to see if a tweet has already been posted.
	# currently not being used and probably doesn't work.
#	stale_tweets = open(tweets_list, 'r')
#	list_of_tweets = stale_tweets.readlines()
#	for tweet in list_of_tweets:
#		get_sentence(tweet)	

def get_sentence(full_tweet):
	# attempt to split a tweet into sentences and remove any URLs.
	# If it finds a suitable tweet, return the stripped-down version plus
	# the tweet's ID.
	encoded_tweet = full_tweet.text.encode('utf-8')
	#split_tweet = re.split(r'[.,;!][\s$]?|http|\s#.|\n', encoded_tweet)
	split_tweet = re.split(r'[.,;!][\s$]?|http|\n', encoded_tweet)
	for sentence in split_tweet:
		# make sure that the sentence starts with "you don't have/need to * to *"
		if re.search("^you don't (have|need) to.* to .*", sentence.lower()):
			sentence = sentence.rstrip('.,;!')
			# make sure tweet won't be too long to post
			if (len(sentence) + len("... but it helps!")) > 140:
				break
			print "About to return: %s (%d)" % (sentence, full_tweet.id)
			return Tweet_with_id(sentence, full_tweet.id)
	return False

def filter_results(results):
	# takes Twitter search API results as input and searches through them
	# until it finds a tweet that fits the format. Returns the finished
	# tweet plus the ID of the tweet from which it's derived.
	full_list = []
	for tweet in results:
		postable_tweet = get_sentence(tweet)
		if postable_tweet:
			final_tweet = postable_tweet.tweet + "... but it helps!"
			return Tweet_with_id(final_tweet, postable_tweet.id)

# search twitter for the format, and exclude a few stale-ass tweets that keep getting reposted
search_results = api.search(q="\"you don't have to\" OR \"you don't need to\" -\"do too much\" -\"see someone everyday\" -\"be worth loving\" -\"love your govt\" -\"drunk to act like a\"", count=100)

tweet_to_post = filter_results(search_results)

# format a version of the output to print when in debug mode and write to the
# stale-ass tweets list
debug_output = tweet_to_post.tweet + " (" + str(tweet_to_post.id) + ")\n"

update_list(debug_output)

# if called with "debug" as an argument, print the tweet and interactively confirm
# whether we actually want to post it.
if len(sys.argv) > 1 and sys.argv[1] == "debug":
	if sys.argv[1] == "debug":
		print debug_output
		if raw_input("Post tweet? ").lower() == 'y':
			api.update_status(tweet_to_post.tweet, tweet_to_post.id)
# post the tweet
else:
	api.update_status(tweet_to_post.tweet, tweet_to_post.id)
