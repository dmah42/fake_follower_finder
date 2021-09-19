import authenticate
import json
import logging
import re
import sys


def _get_user_id(oauth, screen_name):
    user_response = oauth.get("https://api.twitter.com/2/users/by/username/{}".format(screen_name))

    if user_response.status_code != 200:
        raise Exception(
            "User request returned an error: {} {}".format(user_response.status_code, user_response.text))

    logging.info("User response code: %s", user_response.status_code)

    json_response = user_response.json()

    logging.info("User response: %s", json.dumps(json_response, indent=2, sort_keys=True))

    return json_response['data']['id']


def _get_followers(oauth, user_id):
    params = {"user.fields": "created_at,public_metrics,verified"}
    followers_response = oauth.get(
        "https://api.twitter.com/2/users/{}/followers".format(user_id), params=params)

    if followers_response.status_code != 200:
        raise Exception("Followers request returned an error: {} {}".format(
        followers_response.status_code, followers_response.text))

    logging.info("Followers response code: %s",format(followers_response.status_code))

    json_response = followers_response.json()

    logging.info("Followers response: %s", json.dumps(json_response, indent=2, sort_keys=True))

    return json_response['data']


def _maybe_fake(follower):
    # verified users are not fake
    if follower['verified']:
        return False

    # TODO: check created_at

    # if the user name still ends with numbers, might be fake
    ends_with_numbers = re.search(r'\d+$', follower['username']) is not None
    if not ends_with_numbers:
        return False

    # any users with more than one tweet are not obviously fake
    if follower['public_metrics']['tweet_count'] > 1:
        return False

    # check some follower counts
    if follower['public_metrics']['followers_count'] < 2:
        return True


def query(oauth, screen_name):
    user_id = _get_user_id(oauth, screen_name)
    followers = _get_followers(oauth, user_id)
    logging.info("%d followers found", len(followers))

    return [f['username'] for f in followers if _maybe_fake(f)]


if __name__ == '__main__':
    oauth = authenticate.create_local_session()
    fake_followers = query(oauth, sys.argv[1])

    logging.info("%d fake followers found: %s", len(fake_followers), fake_followers)