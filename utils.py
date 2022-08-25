import re
import json

def take_out_json(content):
    """
    take out the json from the content
    """
    s = re.search("^jsonp_\d+_\((.*?)\);?$", content)
    return json.loads(s.group(1) if s else "{}")

