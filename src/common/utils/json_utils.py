import datetime
import json

def as_json(o):
    return json.dumps(o, default=converter)

def converter(o):
    if isinstance(o, datetime.datetime):
        return str(o)

    return o.__dict__
