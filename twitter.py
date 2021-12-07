import requests
import os
import json
import sys
import datetime, pytz
import translator
import os

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.getenv('TWITTER_TOKEN') 

search_url = "https://api.twitter.com/2/tweets/search/recent"

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def get_id(username):
    api_path = "https://api.twitter.com/2/users/by/username/"
    return connect_to_endpoint(api_path + username, params=None)["data"]["id"]

def get_full_list(api_path, params):
    res = {'data': [], 'users': []}
    params['pagination_token'] = None
    while True:
        response_dictionary = connect_to_endpoint(api_path, params=params)
        res['data'] += response_dictionary.get('data', [])
        if response_dictionary.get('includes', False):
            if response_dictionary['includes'].get('users', False):
                res['users'] += response_dictionary['includes']['users']
        params['pagination_token'] = response_dictionary['meta'].get('next_token', '')
        if not params['pagination_token']: break
    return res

def get_friends(userid):
    api_path = f'https://api.twitter.com/2/users/{userid}/following'
    try:
        friends_list = get_full_list(api_path, {'max_results': 1000})
    except: return False
    return [friend['username'] for friend in friends_list['data']]

def get_date(offset):
    now = datetime.datetime.now(pytz.utc)
    return (now - datetime.timedelta(seconds=offset)).isoformat(timespec="seconds")

def build_query(friends, keywords):
    keywords_string = ' OR '.join(keywords)
    usernames_string = ' OR '.join(map(lambda name : 'from:' + name, friends))
    return f"({keywords_string}) ({usernames_string})"

def get_link_to_tweet(username, tweet_id):
    return f'https://twitter.com/{username}/status/{tweet_id}'

def format_tweet(tweet):
    username = tweet[1]['username']
    tweet_id = tweet[0]['id']
    text = tweet[0]['text'].replace('&lt','').replace('&gt','')
    return get_link_to_tweet(username, tweet_id), translator.translate(text)


friends_in_one_query = 20 #const
def process_tweets(username, keywords, friends_cache=[]):
    friends = get_friends(get_id(username))
    if not friends: friends = friends_cache
    res = []
    params = {
        'start_time': get_date(300),
        'max_results': 100,
        'expansions': 'author_id,referenced_tweets.id',
        'user.fields': 'username',
        'tweet.fields': 'text',
    }
    for iteration in range(0, (len(friends)+friends_in_one_query-1) // friends_in_one_query):
        params['query'] = build_query(friends[friends_in_one_query*iteration: friends_in_one_query*(iteration+1)], keywords)
        api_path = 'https://api.twitter.com/2/tweets/search/recent'
        new_list = get_full_list(api_path, params)
        res += map(format_tweet, zip(new_list['data'], new_list['users']))
    return res, friends

if __name__ == "__main__":
    print(process_tweets(sys.argv[1], ['cars', 'electro']))
