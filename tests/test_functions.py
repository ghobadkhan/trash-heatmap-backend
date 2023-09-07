from src.utils import OauthObservable, ReceiverOauth
import random

def test_oauth_observable():
    oauth_observable = OauthObservable()
    session_a = ReceiverOauth(session_id='a')
    session_b = ReceiverOauth(session_id='b')
    # session_b = ReceiverOauth(session_id='c')

    oauth_observable.subscribe(session_a)
    oauth_observable.subscribe(session_b)

    oauth_observable.notify(id='a',api_key='NO')
    oauth_observable.notify(id='b',api_key='YES')





