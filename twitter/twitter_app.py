import socket
import os
import requests
import requests_oauthlib

from requests.exceptions import ChunkedEncodingError
from time import sleep

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", '1199269022447083521-dCaymemHHDkjdsH3OmFcEKAHB9ZB8f')
ACCESS_SECRET = os.getenv("ACCESS_SECRET", 'riDYzKMcOQO7Pk4uKTEqMMfuv7XOTPzqNuoWdSZOSsA9j')
CONSUMER_KEY = os.getenv("CONSUMER_KEY", '4chOZNmrrnejWEgOuiXLpbbSR')
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", 'IgX0Sg7h2Jq5FBN257D74kYAP2UoWDi5pm49x3Oh0hpL3HmkHx')
my_auth = requests_oauthlib.OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)


def get_tweets():
    """
    Make request to Twitter API.
    """
    url = 'https://stream.twitter.com/1.1/statuses/filter.json'
    query_data = [('language', 'en'), ('locations', '2.69170169436, 4.24059418377, 14.5771777686, 13.8659239771')]
    query_url = url + '?' + '&'.join([str(t[0]) + '=' + str(t[1]) for t in query_data])
    response = requests.get(query_url, auth=my_auth, stream=True)
    return response


def send_tweets_to_spark(resp, tcp_connection):
    """
    Send tweets to spark.
    """
    try:
        for line in resp.iter_lines():
            tcp_connection.send((line.decode("utf-8") + "\n").encode())
    except ChunkedEncodingError:
        pass


HOST_NAME = os.getenv("HOST_NAME", "localhost")
PORT = int(os.getenv("PORT", '9009'))
conn = None
while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST_NAME, PORT))
        s.listen(1)
        print("Waiting for TCP connection...")
        conn, addr = s.accept()
        print("Connected... Starting getting tweets.")
        response = get_tweets()
        send_tweets_to_spark(response, conn)
    except Exception as error:
        print('Error!!!', error)
    finally:
        try:
            s.close()
            sleep(10)
        except Exception:
            pass
