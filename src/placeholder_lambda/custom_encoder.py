import json
from decimal import Decimal


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)

        return json.JSONDecoder.default(self, o)