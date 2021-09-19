import logging
from requests_oauthlib import OAuth1Session
from secrets import key, secret


_ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
_BASE_AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
_REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"


# TODO: caching

# uses pin to get access token and secret
def _local_session():
    # Get request token
    oauth = OAuth1Session(key, client_secret=secret, callback_uri='oob')

    try:
        fetch_response = oauth.fetch_request_token(_REQUEST_TOKEN_URL)
    except ValueError:
        logging.exception(
            'There may have been an issue with the consumer_key or consumer_secret you entered.')

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    logging.info('Got OAuth token: %s', resource_owner_key)

    # # Get authorization
    authorization_url = oauth.authorization_url(_BASE_AUTHORIZATION_URL)
    print('Please go here and authorize: %s' % authorization_url)
    verifier = input('Paste the PIN here: ')

    # Get the access token
    oauth = OAuth1Session(
        key,
        client_secret=secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier)
    oauth_tokens = oauth.fetch_access_token(_ACCESS_TOKEN_URL)

    return (oauth_tokens['oauth_token'], oauth_tokens['oauth_token_secret'])


def authorization_url(callback_uri):
   # Get request token
    oauth = OAuth1Session(key, client_secret=secret, callback_uri=callback_uri)

    try:
        fetch_response = oauth.fetch_request_token(_REQUEST_TOKEN_URL)
    except ValueError:
        logging.exception(
            'There may have been an issue with the consumer_key or consumer_secret you entered.')

    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    logging.info('Got OAuth token: %s', resource_owner_key)

    authorization_url = oauth.authorization_url(_BASE_AUTHORIZATION_URL)

    # TODO: figure out how to get this oauth session on callback
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")

    # Get the access token
    oauth = OAuth1Session(
        key,
        client_secret=secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier)
    oauth_tokens = oauth.fetch_access_token(_ACCESS_TOKEN_URL)

    return (oauth_tokens["oauth_token"], oauth_tokens["oauth_token_secret"])




def _create_session(access_token, access_token_secret):
    return OAuth1Session(
        key,
        client_secret=secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret)


def create_local_session():
    return _create_session(_local_session())