from chargemaster_parsers.parsers.kaiser import KaiserChargeMasterParser
from chargemaster_parsers.parsers import ChargeMasterEntry

import tempfile
import zipfile
import pytest
import io
import os

@pytest.fixture
def parser():
    yield KaiserChargeMasterParser()

def test_simple_row(parser):
    rows = "\n".join([
        "Kaiser Foundation Hospital – San Diego Medical Center,,,,,,,,,,,,,,,,,,",
        "Prices effective February 2023,,,,,,,,,,,,,,,,,,",
        "HOSPITAL SERVICES AND PROCEDURES,,,,,,,,,,,,,,,,,,",
        ",,,,,,,,,,,,,,,,,,",
        "\"Charge # ",
        "(Px Code)\",Procedure Code (CPT / HCPCS),Default Modifier,Rev code,Procedure Name,Gross Charge,Discounted Cash Charge,Hospital Inpatient / Outpatient / Both,\"COMMERCIAL INPATIENT - KAISER FOUNDATION HEALTH PLAN, INC. PRICE\",\"COMMERCIAL OUTPATIENT - KAISER FOUNDATION HEALTH PLAN, INC. PRICE\",Commercial - Notes,\"MEDICARE INPATIENT - KAISER FOUNDATION HEALTH PLAN, INC. PRICE\",\"MEDICARE OUTPATIENT - KAISER FOUNDATION HEALTH PLAN, INC. PRICE\",Medicare - Notes,\"MEDICAID INPATIENT - KAISER FOUNDATION HEALTH PLAN, INC. PRICE\",\"MEDICAID OUTPATIENT - KAISER FOUNDATION HEALTH PLAN, INC. PRICE\",Medicaid - Notes, De-identified Minimum Negotiated $ , De-identified Maximum Negotiated $ ",
        "6003,,,0210,ROOM & BOARD-CCU,\" $11,834 \",\" $4,142 \",INPATIENT,Note A, Not applicable ,,Note A, Not applicable ,,Note A, Not applicable ,, None , None "])

    expected_result = [
        ChargeMasterEntry(
            procedure_description = "ROOM & BOARD-CCU",
            in_patient = True,
            payer = 'COMMERCIAL',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        ),
        ChargeMasterEntry(
            procedure_description = "ROOM & BOARD-CCU",
            in_patient = False,
            payer = 'COMMERCIAL',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        ),
        ChargeMasterEntry(
            procedure_description = "ROOM & BOARD-CCU",
            in_patient = True,
            payer = 'MEDICAID',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        ),
        ChargeMasterEntry(
            procedure_description = "ROOM & BOARD-CCU",
            in_patient = False,
            payer = 'MEDICAID',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        ),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        filename = os.path.join(tmp_dir, "kaiser.zip")
        with zipfile.ZipFile(filename, 'w') as artifact:
            artifact.writestr("941105628-san-diego-medical-center-standard-charges-scal-en/KaiserSanDiegoChargeDescriptionMaster.csv", rows.encode("utf-8"))
        with open(filename, "rb") as artifact:
            actual_result = list(parser.parse_artifacts({
                parser.SAN_DIEGO_ARTIFACT_URL : artifact,
            }))
            assert actual_result == expected_result

