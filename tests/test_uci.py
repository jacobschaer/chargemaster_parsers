from chargemaster_parsers.parsers.uci import UCIChargeMasterParser
from chargemaster_parsers.parsers import ChargeMasterEntry

import pytest
import json
import io
import pprint

pp = pprint.PrettyPrinter()

@pytest.fixture
def parser():
    yield UCIChargeMasterParser()

def test_gross_charge_entry(parser):
    row = {
        "Gross Charges": [
            {
                "Itemcode": "00000001_7143",
                "Description": "HB FINE NEEDLE ASPIRATION BX W/O IMG GDN 1ST LESION",
                "CDM Revenue Code": "761",
                "CDM HCPCS": "10021",
                "UCI HB INPATIENT": "N/A",
                "UCI HB INPATIENT Discount Cash Price": "N/A",
                "UCI HB OUTPATIENT": "532.00",
                "UCI HB OUTPATIENT Discount Cash Price": "212.8",
                "Outside Lab": "N/A",
                "Outside Lab Discount Cash Price": "N/A",
                "FQHC FSC": "N/A",
                "FQHC FSC Discount Cash Price": "N/A"
            },
            
            {
                "Itemcode": "99800003_7904",
                "Description": "HB SKIN TEST READING (UCI ONLY)",
                "CDM Revenue Code": "998",
                "UCI HB INPATIENT": "N/A",
                "UCI HB INPATIENT Discount Cash Price": "N/A",
                "UCI HB OUTPATIENT": "N/A",
                "UCI HB OUTPATIENT Discount Cash Price": "N/A",
                "Outside Lab": "N/A",
                "Outside Lab Discount Cash Price": "N/A",
                "FQHC FSC": "N/A",
                "FQHC FSC Discount Cash Price": "N/A"
            }
        ]
    }

    expected_result = [
        ChargeMasterEntry(
            location = 'standard',
            procedure_identifier = '00000001_7143',
            procedure_description = "HB FINE NEEDLE ASPIRATION BX W/O IMG GDN 1ST LESION",
            hcpcs_code = 10021,
            in_patient = False,
            payer = 'UCI HB',
            gross_charge = 532.00
        ), 
    
        ChargeMasterEntry(
            location = 'standard',
            procedure_identifier = '00000001_7143',
            procedure_description = "HB FINE NEEDLE ASPIRATION BX W/O IMG GDN 1ST LESION",
            hcpcs_code = 10021,
            in_patient = False,
            payer = 'Cash',
            gross_charge = 212.8
        ), 
    ]

    actual_results = list(parser.parse_artifacts({UCIChargeMasterParser.ARTIFACT_URL: io.BytesIO(json.dumps(row).encode('utf-8'))}))
    assert(sorted(expected_result) == sorted(actual_results))
        
