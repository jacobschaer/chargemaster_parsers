from chargemaster_parsers.parsers import ChargeMasterEntry, StanfordChargeMasterParser

import tempfile
import json
import pytest
import io


@pytest.fixture
def parser():
    yield StanfordChargeMasterParser()


def test_professional_charges(parser):
    test_input = {
        "File Summary": [{"Prices Posted And Effective": "12/22/2022 12:00:00 AM"}],
        "Professional Charges": [
            {
                "CDM - Standard Gross Charge": 1931.0,
                "Description": "SPINE FUSION EXTRA SEGMENT",
                "Discounted Cash Price": 965.5,
                "Facility": "FACILITY",
                "HCPCS": "22634",
                "Item Code": "22634_8",
                "Location": "Stanford Hospital Clinics",
                "Payer": "Anthem_Blue_Cross",
                "Payer Source": "Fee Schedule",
                "Payer Specific Negotiated Charge": 1607.18,
                "Payer Specific Negotiated Charge - Max": 1852.55,
                "Payer Specific Negotiated Charge - Min": 99.03,
            }
        ],
    }

    expected_result = [
        ChargeMasterEntry(
            gross_charge=1931.0,
            hcpcs_code="22634",
            procedure_identifier="22634_8",
            procedure_description="SPINE FUSION EXTRA SEGMENT",
            payer="Anthem Blue Cross",
            expected_reimbursement=1607.18,
            min_reimbursement=99.03,
            max_reimbursement=1852.55,
            location="Stanford Hospital Clinics",
        ),
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                StanfordChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    json.dumps(test_input).encode("utf-8")
                )
            }
        )
    )
    assert sorted(expected_result) == sorted(actual_result)


def test_gross_charges(parser):
    test_input = {
        "File Summary": [{"Prices Posted And Effective": "12/22/2022 12:00:00 AM"}],
        "Gross Charges": [
            {
                "Code": "HCPCS C1713",
                "Discount Cash Price": 266.56,
                "Price": 666.4,
                "Procedure": 317184,
                "Procedure Description": "SCREW MATRIXMIDFACE 1.55MM",
                "Quantity": "N/A",
            }
        ],
    }

    expected_result = [
        ChargeMasterEntry(
            gross_charge=266.56,
            hcpcs_code="C1713",
            procedure_identifier=317184,
            procedure_description="SCREW MATRIXMIDFACE 1.55MM",
            quantity="N/A",
            payer="Cash",
        )
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                StanfordChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    json.dumps(test_input).encode("utf-8")
                )
            }
        )
    )
    assert sorted(expected_result) == sorted(actual_result)


def test_ms_drg(parser):
    test_input = {
        "File Summary": [{"Prices Posted And Effective": "12/22/2022 12:00:00 AM"}],
        "Inpatient Payer Specific Charge": [
            {
                "Description": "Other Multiple Significant Trauma Without Cc/Mcc",
                "MS-DRG": "965",
                "Payer": "HealthNet",
                "Payer Specific Negotiated Charge": 159516.0,
            }
        ],
    }

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=159516.0,
            ms_drg_code="965",
            procedure_identifier="965",
            procedure_description="Other Multiple Significant Trauma Without Cc/Mcc",
            payer="HealthNet",
        )
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                StanfordChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    json.dumps(test_input).encode("utf-8")
                )
            }
        )
    )
    assert sorted(expected_result) == sorted(actual_result)


def test_institution_name(parser):
    assert StanfordChargeMasterParser.institution_name == "Stanford"
    assert parser.institution_name == "Stanford"


def test_artifact_urls(parser):
    assert (
        StanfordChargeMasterParser.artifact_urls
        == StanfordChargeMasterParser.ARTIFACT_URLS
    )
    assert parser.artifact_urls == StanfordChargeMasterParser.ARTIFACT_URLS
