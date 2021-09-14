import argparse
import json
import os
import sys
from requests_oauthlib import OAuth1Session

parser = argparse.ArgumentParser(description='Identify fake followers.')
parser.add_argument(
    '--key', type=str, default=os.environ.get("CONSUMER_KEY"), help='the consumer key')
parser.add_argument(
    '--secret', type=str, default=os.environ.get("CONSUMER_SECRET"), help='the consumer secret')
parser.add_argument('user', type=str, help='the user name to check')

args = parser.parse_args()

def authenticate():
    consumer_key = args.key
    consumer_secret = args.secret

    # Get request token
    REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri='oob')

    try:
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    except ValueError:
        sys.exit("There may have been an issue with the consumer_key or consumer_secret you entered.")

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token: %s" % resource_owner_key)

    # # Get authorization
    BASE_AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(BASE_AUTHORIZATION_URL)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")

    # Get the access token
    ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    return OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )


def get_user_id(oauth):
    screen_name = args.user
    user_response = oauth.get("https://api.twitter.com/2/users/by/username/{}".format(screen_name))

    if user_response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(user_response.status_code, user_response.text))

    print("Response code: {}".format(user_response.status_code))

    json_response = user_response.json()

    print(json.dumps(json_response, indent=2, sort_keys=True))

    return json_response['id']


def get_followers(oauth, user_id):
    params = {"user.fields": "created_at,public_metrics,verified"}
    followers_response = oauth.get(
        "https://api.twitter.com/2/users/{}/followers".format(user_id), params=params)

    if followers_response.status_code != 200:
        raise Exception("Request returned an error: {} {}".format(
        followers_response.status_code, followers_response.text))

    print("Response code: {}".format(followers_response.status_code))

    json_response = followers_response.json()

    print(json.dumps(json_response, indent=2, sort_keys=True))

    return json_response['data']


oauth = authenticate()
user_id = get_user_id(oauth)
followers = get_followers(oauth, user_id)
print(followers)