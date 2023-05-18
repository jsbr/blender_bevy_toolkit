""" Small Utility Functions """
import json
import os


def jdict(**kwargs):
    """Dump arguments into a JSON-encoded string"""
    return json.dumps(dict(**kwargs))


def getAssetFolder(config):
    if ("assets/" not in config["output_filepath"]):
        raise Exception("Must be export under assets folder")
    return os.path.dirname(config["output_filepath"].split("assets/")[1])
