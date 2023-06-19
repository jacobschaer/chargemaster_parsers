from chargemaster_parsers.parsers.uci import UCIChargeMasterParser
from chargemaster_parsers.parsers import ChargeMasterEntry

import pytest
import requests
import json

@pytest.fixtures
def parser():
    yield UCIChargeMasterParser()

def test_open_file(parser):
    for url in parser.artifact_urls:
        r = requests.get(url)
        open('data.json', 'wb').write(r.content)
        with open('data.json', 'r') as data:
            data_dict = json.load(data)
        


        
