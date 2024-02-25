from dataclasses import dataclass, field, fields
from flask import Request

@dataclass(init=False, repr=False)
class DataParent:
    def __init__(self, **kwargs):
        for f in fields(self):
            if f.name in kwargs:
                value = kwargs[f.name]
                if not isinstance(value,f.type):
                    try:
                        value = f.type(value)
                    except:
                        raise ValueError("Validation Failed")
                setattr(self,f.name,value)

    @classmethod
    def from_request(cls, request:Request):
        if request.method == "GET":
            payload = request.args.to_dict()
        elif request.method == "POST":
            payload = request.get_json()
        else:
            raise ValueError
        return cls(**payload)

@dataclass(init=False, repr=False)
class LitterForm(DataParent):
    lat: float
    lng: float
    count: int = field(default_factory= lambda: 1)
    comment: str | None = field(default_factory= lambda: None)
    pics: list | None = field(default_factory= lambda: None)
