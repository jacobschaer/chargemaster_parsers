from chargemaster_parsers.parsers import SouthwestChargeMasterParser, ChargeMasterEntry

import tempfile
from openpyxl import Workbook
import pytest
import io
import os


@pytest.fixture
def parser():
    yield SouthwestChargeMasterParser()


TEST_CASE_1 = "\n".join(
    [
        "Hospital Name: Southwest Healthcare System,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "Price Effective Date: 4/1/2023,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "Facility,Description,CDM,Code Type,DRG (If Applicable),CPT/HCPCS (If Applicable),EAPG (If Applicable),APC (If Applicable),Rev Code (If Applicable),   Gross Charge   ,   Cash Price   ,   Minimum   ,   Maximum  , Aetna HMO/PPO , Aetna Medicare , Blue Cross Anthem , Blue Cross Medi-Cal , Blue Cross Senior , Blue Shield California Promise , Blue Shield Promise , Blue Shield Promise Rady , Blue Shield Select , Blue Shield Senior , Brand New Day , Cal Optima Medicaid , Cigna HMO/PPO , Epic Health , Epic Health Plan Medicare , Exclusive Care ,First Health, HealthNet , HealthNet Medi-Cal , HealthNet Medicare , Heritage Commercial , Heritage Medi-Cal , Heritage Medicare , Humana Medicare , Inland Empire Health Plan , Inland Empire Health Plan Medicare , Kaiser , Kaiser Medi-Cal , Kaiser Medicare , Molina , Molina Medi-Cal , Molina Medicare , Multiplan , Palomar Health , Scan Medicare , Sharp Health Plan , United Healthcare HMO, United Healthcare PPO, United Healthcare Community Plan  , United Healthcare Medicare ",
        'Southwest Healthcare System,COMPONENT FEM CR LT 4N,38000501,Chargemaster,,C1776,,,278,"1,922",769,398,"5,419",884,-1,761,-1,-1,-1,-1,-1,-1,-1,-1,-1,550,"2,956",-1,"3,941",884,446,-1,"4,050",475,-1,398,-1,-1,-1,646,-1,-1,-1,-1,-1,"1,730",942,-1,"5,419",-1,-1,-1,-1',
    ]
)

TEST_CASE_1_NO_HEADER = "\n".join(
    [
        "Facility,Description,CDM,Code Type,DRG (If Applicable),CPT/HCPCS (If Applicable),EAPG (If Applicable),APC (If Applicable),Rev Code (If Applicable),   Gross Charge   ,   Cash Price   ,   Minimum   ,   Maximum  , Aetna HMO/PPO , Aetna Medicare , Blue Cross Anthem , Blue Cross Medi-Cal , Blue Cross Senior , Blue Shield California Promise , Blue Shield Promise , Blue Shield Promise Rady , Blue Shield Select , Blue Shield Senior , Brand New Day , Cal Optima Medicaid , Cigna HMO/PPO , Epic Health , Epic Health Plan Medicare , Exclusive Care ,First Health, HealthNet , HealthNet Medi-Cal , HealthNet Medicare , Heritage Commercial , Heritage Medi-Cal , Heritage Medicare , Humana Medicare , Inland Empire Health Plan , Inland Empire Health Plan Medicare , Kaiser , Kaiser Medi-Cal , Kaiser Medicare , Molina , Molina Medi-Cal , Molina Medicare , Multiplan , Palomar Health , Scan Medicare , Sharp Health Plan , United Healthcare HMO, United Healthcare PPO, United Healthcare Community Plan  , United Healthcare Medicare ",
        'Southwest Healthcare System,COMPONENT FEM CR LT 4N,38000501,Chargemaster,,C1776,,,278,"1,922",769,398,"5,419",884,-1,761,-1,-1,-1,-1,-1,-1,-1,-1,-1,550,"2,956",-1,"3,941",884,446,-1,"4,050",475,-1,398,-1,-1,-1,646,-1,-1,-1,-1,-1,"1,730",942,-1,"5,419",-1,-1,-1,-1',
    ]
)

TEST_CASE_1_SCRAMBLED_HEADER = "\n".join(
    [
        "Hospital Name: Southwest Healthcare System,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "Price Effective Date: 4/1/2023,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "CPT/HCPCS (If Applicable),EAPG (If Applicable),Facility,Description,CDM,Code Type,DRG (If Applicable),APC (If Applicable),Rev Code (If Applicable),   Gross Charge   ,   Cash Price   ,   Minimum   ,   Maximum  , Aetna HMO/PPO , Aetna Medicare , Blue Cross Anthem , Blue Cross Medi-Cal , Blue Cross Senior , Blue Shield California Promise , Blue Shield Promise , Blue Shield Promise Rady , Blue Shield Select , Blue Shield Senior , Brand New Day , Cal Optima Medicaid , Cigna HMO/PPO , Epic Health , Epic Health Plan Medicare , Exclusive Care ,First Health, HealthNet , HealthNet Medi-Cal , HealthNet Medicare , Heritage Commercial , Heritage Medi-Cal , Heritage Medicare , Humana Medicare , Inland Empire Health Plan , Inland Empire Health Plan Medicare , Kaiser , Kaiser Medi-Cal , Kaiser Medicare , Molina , Molina Medi-Cal , Molina Medicare , Multiplan , Palomar Health , Scan Medicare , Sharp Health Plan , United Healthcare HMO, United Healthcare PPO, United Healthcare Community Plan  , United Healthcare Medicare ",
        'C1776,,Southwest Healthcare System,COMPONENT FEM CR LT 4N,38000501,Chargemaster,,,278,"1,922",769,398,"5,419",884,-1,761,-1,-1,-1,-1,-1,-1,-1,-1,-1,550,"2,956",-1,"3,941",884,446,-1,"4,050",475,-1,398,-1,-1,-1,646,-1,-1,-1,-1,-1,"1,730",942,-1,"5,419",-1,-1,-1,-1',
    ]
)

EXPECTED_RESULTS_1 = [
    ChargeMasterEntry(
        expected_reimbursement=884.0,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Aetna HMO/PPO",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=761,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Blue Cross Anthem",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=550,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Cigna HMO/PPO",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=2956,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Epic Health",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=3941,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Exclusive Care",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=884,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="First Health",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=446,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="HealthNet",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=4050,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="HealthNet Medicare",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=475,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Heritage Commercial",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=398,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Heritage Medicare",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=646,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Kaiser",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=1730,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Multiplan",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=942,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Palomar Health",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        expected_reimbursement=5419,
        gross_charge=1922.0,
        hcpcs_code="C1776",
        max_reimbursement=5419.0,
        min_reimbursement=398.0,
        payer="Sharp Health Plan",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
    ChargeMasterEntry(
        gross_charge=769.0,
        hcpcs_code="C1776",
        payer="Cash",
        procedure_description="COMPONENT FEM CR LT 4N",
        procedure_identifier="38000501",
    ),
]


def test_simple_row(parser):
    actual_result = list(
        parser.parse_artifacts(
            {
                SouthwestChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    TEST_CASE_1.encode("utf-8")
                )
            }
        )
    )

    assert sorted(EXPECTED_RESULTS_1) == sorted(actual_result)


def test_simple_row_no_leadin(parser):
    actual_result = list(
        parser.parse_artifacts(
            {
                SouthwestChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    TEST_CASE_1_NO_HEADER.encode("utf-8")
                )
            }
        )
    )

    assert sorted(EXPECTED_RESULTS_1) == sorted(actual_result)


def test_simple_row_scrambled_columns(parser):
    actual_result = list(
        parser.parse_artifacts(
            {
                SouthwestChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    TEST_CASE_1_SCRAMBLED_HEADER.encode("utf-8")
                )
            }
        )
    )

    assert sorted(EXPECTED_RESULTS_1) == sorted(actual_result)


def test_extra_apc(parser):
    test_input = "\n".join(
        [
            "Facility,Description,CDM,Code Type,DRG (If Applicable),CPT/HCPCS (If Applicable),EAPG (If Applicable),APC (If Applicable),Rev Code (If Applicable),   Gross Charge   ,   Cash Price   ,   Minimum   ,   Maximum  , Aetna HMO/PPO , Aetna Medicare , Blue Cross Anthem , Blue Cross Medi-Cal , Blue Cross Senior , Blue Shield California Promise , Blue Shield Promise , Blue Shield Promise Rady , Blue Shield Select , Blue Shield Senior , Brand New Day , Cal Optima Medicaid , Cigna HMO/PPO , Epic Health , Epic Health Plan Medicare , Exclusive Care ,First Health, HealthNet , HealthNet Medi-Cal , HealthNet Medicare , Heritage Commercial , Heritage Medi-Cal , Heritage Medicare , Humana Medicare , Inland Empire Health Plan , Inland Empire Health Plan Medicare , Kaiser , Kaiser Medi-Cal , Kaiser Medicare , Molina , Molina Medi-Cal , Molina Medicare , Multiplan , Palomar Health , Scan Medicare , Sharp Health Plan , United Healthcare HMO, United Healthcare PPO, United Healthcare Community Plan  , United Healthcare Medicare ",
            "Southwest Healthcare System,PATHOGEN REDUCED PLATELETS,50302033,Chargemaster,,P9073,,9536,390,793,317,266,974,288,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1",
        ]
    )

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=288,
            gross_charge=793.0,
            hcpcs_code="P9073",
            max_reimbursement=974.0,
            min_reimbursement=266.0,
            payer="Aetna HMO/PPO",
            procedure_description="PATHOGEN REDUCED PLATELETS",
            procedure_identifier="50302033",
            extra_data={"APC (If Applicable)": "9536"},
        ),
        ChargeMasterEntry(
            gross_charge=317,
            hcpcs_code="P9073",
            payer="Cash",
            procedure_description="PATHOGEN REDUCED PLATELETS",
            procedure_identifier="50302033",
            extra_data={"APC (If Applicable)": "9536"},
        ),
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                SouthwestChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_input.encode("utf-8")
                )
            }
        )
    )

    assert sorted(expected_result) == sorted(actual_result)


def test_other_cpt(parser):
    test_input = "\n".join(
        [
            "Facility,Description,CDM,Code Type,DRG (If Applicable),CPT/HCPCS (If Applicable),EAPG (If Applicable),APC (If Applicable),Rev Code (If Applicable),   Gross Charge   ,   Cash Price   ,   Minimum   ,   Maximum  , Aetna HMO/PPO , Aetna Medicare , Blue Cross Anthem , Blue Cross Medi-Cal , Blue Cross Senior , Blue Shield California Promise , Blue Shield Promise , Blue Shield Promise Rady , Blue Shield Select , Blue Shield Senior , Brand New Day , Cal Optima Medicaid , Cigna HMO/PPO , Epic Health , Epic Health Plan Medicare , Exclusive Care ,First Health, HealthNet , HealthNet Medi-Cal , HealthNet Medicare , Heritage Commercial , Heritage Medi-Cal , Heritage Medicare , Humana Medicare , Inland Empire Health Plan , Inland Empire Health Plan Medicare , Kaiser , Kaiser Medi-Cal , Kaiser Medicare , Molina , Molina Medi-Cal , Molina Medicare , Multiplan , Palomar Health , Scan Medicare , Sharp Health Plan , United Healthcare HMO, United Healthcare PPO, United Healthcare Community Plan  , United Healthcare Medicare ",
            'Southwest Healthcare System,Spirom fev/fvc>/=70%/w/ocopd,,Other CPT/HCPCS,,3027F,,,,-1,-1,"10,526","10,526",-1,-1,-1,-1,-1,-1,-1,-1,"10,526",-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1',
        ]
    )

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=10526.0,
            procedure_identifier="CPT_3027F",
            cpt_code="3027F",
            max_reimbursement=10526.0,
            min_reimbursement=10526.0,
            payer="Blue Shield Select",
            procedure_description="Spirom fev/fvc>/=70%/w/ocopd",
        ),
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                SouthwestChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_input.encode("utf-8")
                )
            }
        )
    )

    assert sorted(expected_result) == sorted(actual_result)


def test_ms_drg(parser):
    test_input = "\n".join(
        [
            "Facility,Description,CDM,Code Type,DRG (If Applicable),CPT/HCPCS (If Applicable),EAPG (If Applicable),APC (If Applicable),Rev Code (If Applicable),   Gross Charge   ,   Cash Price   ,   Minimum   ,   Maximum  , Aetna HMO/PPO , Aetna Medicare ",
            'Southwest Healthcare System,HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC,,MS-DRG,1,,,,,-1,-1,"239,580","448,170",-1,"254,017",',
        ]
    )

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=254017.0,
            procedure_identifier="MS_DRG_001",
            ms_drg_code="001",
            max_reimbursement=448170.0,
            min_reimbursement=239580.0,
            payer="Aetna Medicare",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
        ),
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                SouthwestChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_input.encode("utf-8")
                )
            }
        )
    )

    assert sorted(expected_result) == sorted(actual_result)


def test_per_diem(parser):
    test_input = "\n".join(
        [
            "Facility,Description,CDM,Code Type,DRG (If Applicable),CPT/HCPCS (If Applicable),EAPG (If Applicable),APC (If Applicable),Rev Code (If Applicable),   Gross Charge   ,   Cash Price   ,   Minimum   ,   Maximum  ,  Blue Shield Select ",
            'Southwest Healthcare System,CARDIAC VALVE AND OTHER MAJOR CARDIOTHORACIC PROCEDURES WITH CARDIAC CATHETERIZATION WITH MCC,,MS-DRG,216,,,,,-1,-1,"25,676","155,120","   $3,622 Per Diem   "',
        ]
    )

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=3622.0,
            max_reimbursement=155120.0,
            min_reimbursement=25676.0,
            ms_drg_code="216",
            payer="Blue Shield Select",
            procedure_description="CARDIAC VALVE AND OTHER MAJOR CARDIOTHORACIC PROCEDURES WITH CARDIAC CATHETERIZATION WITH MCC",
            procedure_identifier="MS_DRG_216",
        )
    ]

    actual_result = list(
        parser.parse_artifacts(
            {
                SouthwestChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_input.encode("utf-8")
                )
            }
        )
    )

    assert sorted(expected_result) == sorted(actual_result)


def test_institution_name(parser):
    assert SouthwestChargeMasterParser.institution_name == "Southwest"
    assert parser.institution_name == "Southwest"


def test_artifact_urls(parser):
    assert (
        SouthwestChargeMasterParser.artifact_urls
        == SouthwestChargeMasterParser.ARTIFACT_URLS
    )
    assert parser.artifact_urls == SouthwestChargeMasterParser.ARTIFACT_URLS
