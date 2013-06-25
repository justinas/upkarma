import requests
from requests.exceptions import RequestException

import json
from requests_oauthlib import OAuth1Session
from twitter import TwitterError

class TwitterStream(object):
    URL = 'https://stream.twitter.com/1.1/statuses/filter.json'
    def __init__(self, consumer_key, consumer_secret,
                 token, token_secret):
        """
        Argument names made to match
        the ones used by Python Twitter Tools
        """
        self.session = OAuth1Session(client_key=consumer_key,
                                     client_secret=consumer_secret,
                                     resource_owner_key=token,
                                     resource_owner_secret=token_secret)


    def statuses_filter(self, **kwargs):
        req = self.session.post(self.URL, params=kwargs, stream=True)
        try:
            for line in req.iter_lines():
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                    except:
                        raise
                    # if it's not a tweet...
                    if not obj.get('id', None):
                        raise TwitterError('Unknown message:\n'+line)

                    yield obj
        except RequestException as e:
            raise TwitterError('Disconnected: \n'+str(e))
