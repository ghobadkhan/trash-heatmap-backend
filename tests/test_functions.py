from src.utils import OauthObservable, ReceiverOauth
from flask_socketio.test_client import SocketIOTestClient

def test_oauth_observable():
    oauth_observable = OauthObservable()
    session_a = ReceiverOauth(session_id='a')
    session_b = ReceiverOauth(session_id='b')
    # session_b = ReceiverOauth(session_id='c')

    oauth_observable.subscribe(session_a)
    oauth_observable.subscribe(session_b)

    oauth_observable.notify(id='a',api_token='NO')
    oauth_observable.notify(id='b',api_token='YES')

def test_socket_broadcast(socket_client:SocketIOTestClient):
    @socket_client.socketio.on('my_event')
    def handle_event():
        global received
        received = True
    socket_client.emit(event="my_event",data="test", broadcast=True)
    assert received #type: ignore





