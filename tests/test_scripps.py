from chargemaster_parsers.parsers import ChargeMasterEntry, ScrippsChargeMasterParser

import tempfile
import json
import pytest
import io


@pytest.fixture
def parser():
    yield ScrippsChargeMasterParser()


def test_not_ms_drg(parser):
    rows = "\n".join(
        [
            "LOCATION|PROCEDURE CODE|PROCEDURE DESCRIPTION|PAYER|PLAN|GROSS CHARGES IP|IP_EXPECTED_REIMBURSMENT|GROSS CHARGES OP|OP_EXPECTED_REIMBURSMENT|IP_MIN|IP_MAX|OP_MIN|OP_MAX|CASH/SELF PAY",
            "Scripps Green Hospital|50400018|HC High Cost Appl Skin Substitute T/a/L Up to 100 Sq Cm, 1st 25 Sq Cm or Less|AETNA MEDI-CAL [213]|AETNA MEDI-CAL BETTER HEALTH OF CA [21301]|10626.00||10626.00|0.00|||1381.38|10626.00|5313.00",
        ]
    )

    expected_result = [
        ChargeMasterEntry(
            procedure_identifier="50400018",
            location="Scripps Green Hospital",
            procedure_description="HC High Cost Appl Skin Substitute T/a/L Up to 100 Sq Cm, 1st 25 Sq Cm or Less",
            in_patient=True,
            payer="Cash",
            gross_charge=5313.0,
        ),
        ChargeMasterEntry(
            procedure_identifier="50400018",
            location="Scripps Green Hospital",
            procedure_description="HC High Cost Appl Skin Substitute T/a/L Up to 100 Sq Cm, 1st 25 Sq Cm or Less",
            in_patient=True,
            payer="AETNA MEDI-CAL",
            plan="AETNA MEDI-CAL BETTER HEALTH OF CA",
            gross_charge=10626.0,
        ),
        ChargeMasterEntry(
            procedure_identifier="50400018",
            location="Scripps Green Hospital",
            procedure_description="HC High Cost Appl Skin Substitute T/a/L Up to 100 Sq Cm, 1st 25 Sq Cm or Less",
            in_patient=False,
            payer="AETNA MEDI-CAL",
            plan="AETNA MEDI-CAL BETTER HEALTH OF CA",
            gross_charge=10626.0,
            expected_reimbursement=0.0,
            max_reimbursement=10626.00,
            min_reimbursement=1381.38,
        ),
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                ScrippsChargeMasterParser.SCRIPPS_GREEN_HOSPITAL_ARTIFACT_URL: io.BytesIO(
                    rows.encode("utf-8")
                ),
                ScrippsChargeMasterParser.SCRIPPS_MEMORIAL_HOSPITAL_ENCINITAS_ARTIFACT_URL: io.BytesIO(),
                ScrippsChargeMasterParser.SCRIPPS_MEMORIAL_HOSPITAL_LA_JOLLA_ARTIFACT_URL: io.BytesIO(),
                ScrippsChargeMasterParser.SCRIPPS_MERCY_HOSPITAL_SAN_DIEGO_ARTIFACT_URL: io.BytesIO(),
                ScrippsChargeMasterParser.SCRIPPS_MERCY_HOSPITAL_CHULA_VISTA_ARTIFACT_URL: io.BytesIO(),
            }
        )
    )
    assert sorted(expected_result) == sorted(actual_result)


def test_ms_drg(parser):
    rows = "\n".join(
        [
            "LOCATION|PROCEDURE CODE|PROCEDURE DESCRIPTION|PAYER|PLAN|GROSS CHARGES IP|IP_EXPECTED_REIMBURSMENT|GROSS CHARGES OP|OP_EXPECTED_REIMBURSMENT|IP_MIN|IP_MAX|OP_MIN|OP_MAX|CASH/SELF PAY",
            "Scripps Green Hospital|MS940|O.R. Procedures With Diagnoses Of Other Contact With Health Services With Cc|AETNA MEDI-CAL [213]|AETNA MEDI-CAL BETTER HEALTH OF CA [21301], AETNA MEDI-CAL HMO - COMM CARE IPA [21302], AETNA MEDI-CAL HMO - PROSPECT MED GRP [21303]|105058.34||||9000.00|101685.89|||52529.17",
            "Scripps Green Hospital|MS940|O.R. Procedures With Diagnoses Of Other Contact With Health Services With Cc|AETNA MEDI-CAL [213]|AETNA MEDI-CAL HMO - HEALTH EXCEL IPA [21304]|105058.34||||9000.00|101685.89|||52529.17",
            "Scripps Green Hospital|MS940|O.R. Procedures With Diagnoses Of Other Contact With Health Services With Cc|AETNA MEDICARE ADVANTAGE [212]|AETNA MCR ADV HMO - HEALTH EXCEL IPA [21208]|105058.34|18463.80|||9000.00|101685.89|||52529.17",
        ]
    )

    expected_result = [
        ChargeMasterEntry(
            procedure_identifier="MS940",
            location="Scripps Green Hospital",
            procedure_description="O.R. Procedures With Diagnoses Of Other Contact With Health Services With Cc",
            ms_drg_code="940",
            in_patient=True,
            payer="AETNA MEDI-CAL",
            plan="AETNA MEDI-CAL BETTER HEALTH OF CA",
            gross_charge=105058.34,
            max_reimbursement=101685.89,
            min_reimbursement=9000.0,
        ),
        ChargeMasterEntry(
            procedure_identifier="MS940",
            location="Scripps Green Hospital",
            procedure_description="O.R. Procedures With Diagnoses Of Other Contact With Health Services With Cc",
            ms_drg_code="940",
            in_patient=True,
            payer="AETNA MEDI-CAL",
            plan="AETNA MEDI-CAL HMO - HEALTH EXCEL IPA",
            gross_charge=105058.34,
            max_reimbursement=101685.89,
            min_reimbursement=9000.0,
        ),
        ChargeMasterEntry(
            procedure_identifier="MS940",
            location="Scripps Green Hospital",
            procedure_description="O.R. Procedures With Diagnoses Of Other Contact With Health Services With Cc",
            ms_drg_code="940",
            in_patient=True,
            payer="AETNA MEDICARE ADVANTAGE",
            plan="AETNA MCR ADV HMO - HEALTH EXCEL IPA",
            expected_reimbursement=18463.8,
            gross_charge=105058.34,
            max_reimbursement=101685.89,
            min_reimbursement=9000.0,
        ),
        ChargeMasterEntry(
            procedure_identifier="MS940",
            location="Scripps Green Hospital",
            procedure_description="O.R. Procedures With Diagnoses Of Other Contact With Health Services With Cc",
            ms_drg_code="940",
            in_patient=True,
            payer="Cash",
            gross_charge=52529.17,
        ),
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                ScrippsChargeMasterParser.SCRIPPS_GREEN_HOSPITAL_ARTIFACT_URL: io.BytesIO(
                    rows.encode("utf-8")
                ),
                ScrippsChargeMasterParser.SCRIPPS_MEMORIAL_HOSPITAL_ENCINITAS_ARTIFACT_URL: io.BytesIO(),
                ScrippsChargeMasterParser.SCRIPPS_MEMORIAL_HOSPITAL_LA_JOLLA_ARTIFACT_URL: io.BytesIO(),
                ScrippsChargeMasterParser.SCRIPPS_MERCY_HOSPITAL_SAN_DIEGO_ARTIFACT_URL: io.BytesIO(),
                ScrippsChargeMasterParser.SCRIPPS_MERCY_HOSPITAL_CHULA_VISTA_ARTIFACT_URL: io.BytesIO(),
            }
        )
    )
    assert sorted(expected_result) == sorted(actual_result)


def test_institution_name(parser):
    assert ScrippsChargeMasterParser.institution_name == "Scripps"
    assert parser.institution_name == "Scripps"


def test_artifact_urls(parser):
    assert (
        ScrippsChargeMasterParser.artifact_urls
        == ScrippsChargeMasterParser.ARTIFACT_URLS
    )
    assert parser.artifact_urls == ScrippsChargeMasterParser.ARTIFACT_URLS
