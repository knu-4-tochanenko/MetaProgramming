import json


def load_settings(path):
    file = open(path)
    text = file.read().replace("\n", " ")
    res = json.loads(text)
    return res

