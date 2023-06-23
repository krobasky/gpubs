import json
import os

__version__ = "not none"

cur_dir = os.path.realpath(os.path.dirname(__file__))
rel_path = f"{cur_dir}/../release-info.json"

with open(rel_path) as f:
    j = json.load(f)
    __version__ = j["VERSION"]
