from typing import Any, Dict, List
from flask import current_app, has_app_context
from abc import ABC, abstractmethod

def get_config(key:str):     
    if has_app_context() and not current_app.config.get('TESTING',True):
            value = current_app.config.get(key)
    else:
        # TODO: Change this later
        value = "TESTING"
    assert value is not None
    return value
     

class Observer(ABC):
    
    @abstractmethod
    def get_id(self) -> int|str:
        ...

    @abstractmethod
    def update(self,**kwargs) -> Any:
        ...

        
class Observable(ABC):
    @abstractmethod
    def subscribe(self, observer:Observer, **kwargs):
        ...
    
    @abstractmethod
    def unsubscribe(self, observer:Observer, **kwargs):
        ...
    
    @abstractmethod
    def notify(self, *args, **kwargs):
        ...


class OauthObservable(Observable):
    def __init__(self) -> None:
        self.observers: Dict[str|int,Observer] = {}

    def subscribe(self, observer: Observer, **kwargs):
        id = observer.get_id()
        self.observers[id] = observer

    def unsubscribe(self, observer: Observer, **kwargs):
        id = observer.get_id()
        self.observers.pop(id)

    def notify(self, id:str, api_key:str):
        observer = self.observers.get(id)
        if observer is not None:
            self.unsubscribe(observer)
            observer.update(api_key=api_key)

class ReceiverOauth(Observer):
    def __init__(self, session_id:str) -> None:
        self.session_id = session_id
    
    def get_id(self) -> int | str:
        return self.session_id
    
    def update(self, **kwargs):
        api_key = kwargs['api_key']
        print(api_key)
        return api_key

        
    