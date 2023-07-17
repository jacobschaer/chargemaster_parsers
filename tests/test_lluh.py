from chargemaster_parsers.parsers import LLUHChargeMasterParser, ChargeMasterEntry

import tempfile
from openpyxl import Workbook
import pytest
import io
import os


@pytest.fixture
def parser():
    yield LLUHChargeMasterParser()


def test_ms_drg(parser):
    test_case = "\n".join(
        [
            "procedure,code,description,gross_pay,cash_pay,aetna,healthnet,cigna,united_healthcare,blue_cross,tricare,managed_health_network,molina_medicare,inland_empire_health_plan,risk_management,blue_shield,minimum,maximum",
            "MS883,MS-DRG V37 (FY2020) 883,Disorders Of Personality And Impulse Control,18805.00,18805.00,221345.12,NA,177076.09,221345.12,221345.12,221345.12,221345.12,NA,NA,221345.12,221345.12,177076.09,221345.12",
        ]
    )
    actual_result = list(
        parser.parse_artifacts(
            {
                list(LLUHChargeMasterParser.URL_TO_INSTITUTION.keys())[0]: io.BytesIO(
                    test_case.encode("utf-8")
                )
            }
        )
    )

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=221345.12,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="aetna",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            expected_reimbursement=177076.09,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="cigna",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            expected_reimbursement=221345.12,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="united healthcare",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            expected_reimbursement=221345.12,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="blue cross",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            expected_reimbursement=221345.12,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="tricare",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            expected_reimbursement=221345.12,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="managed health network",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            expected_reimbursement=221345.12,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="risk management",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            expected_reimbursement=221345.12,
            gross_charge=18805.0,
            location="Medical Center",
            max_reimbursement=221345.12,
            min_reimbursement=177076.09,
            ms_drg_code="883",
            payer="blue shield",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
        ChargeMasterEntry(
            gross_charge=18805.0,
            location="Medical Center",
            ms_drg_code="883",
            payer="Cash",
            procedure_description="Disorders Of Personality And Impulse Control",
            procedure_identifier="MS883",
        ),
    ]

    assert sorted(actual_result) == sorted(expected_result)


def test_hcpcs(parser):
    test_case = "\n".join(
        [
            "procedure,code,description,gross_pay,cash_pay,minimum,maximum",
            "50119,HCPCS V2632,LENS TORIC SYMFONY ZXT300 15.0 DIOPTER,3842.00,3842.00,365.18,2881.13",
        ]
    )

    actual_result = list(
        parser.parse_artifacts(
            {
                list(LLUHChargeMasterParser.URL_TO_INSTITUTION.keys())[0]: io.BytesIO(
                    test_case.encode("utf-8")
                )
            }
        )
    )

    expected_result = [
        ChargeMasterEntry(
            gross_charge=3842.0,
            hcpcs_code="V2632",
            location="Medical Center",
            payer="Cash",
            procedure_description="LENS TORIC SYMFONY ZXT300 15.0 DIOPTER",
            procedure_identifier="50119",
        )
    ]
    assert sorted(actual_result) == sorted(expected_result)


def test_cpt(parser):
    test_case = "\n".join(
        [
            "procedure,code,description,gross_pay,cash_pay,aetna,healthnet,cigna,united_healthcare,blue_cross,tricare,managed_health_network,molina_medicare,inland_empire_health_plan,risk_management,blue_shield,minimum,maximum",
            "907804356,CPT« 90847,Hc Php Youth Iop Family Therapy,312.00,312.00,NA,NA,249.60,NA,NA,NA,NA,NA,NA,NA,312.00,249.60,312.00",
        ]
    )
    actual_result = list(
        parser.parse_artifacts(
            {
                list(LLUHChargeMasterParser.URL_TO_INSTITUTION.keys())[0]: io.BytesIO(
                    test_case.encode("utf-8")
                )
            }
        )
    )

    expected_result = [
        ChargeMasterEntry(
            cpt_code="90847",
            expected_reimbursement=249.6,
            gross_charge=312.0,
            location="Medical Center",
            max_reimbursement=312.0,
            min_reimbursement=249.6,
            payer="cigna",
            procedure_description="Hc Php Youth Iop Family Therapy",
            procedure_identifier="907804356",
        ),
        ChargeMasterEntry(
            cpt_code="90847",
            expected_reimbursement=312.0,
            gross_charge=312.0,
            location="Medical Center",
            max_reimbursement=312.0,
            min_reimbursement=249.6,
            payer="blue shield",
            procedure_description="Hc Php Youth Iop Family Therapy",
            procedure_identifier="907804356",
        ),
        ChargeMasterEntry(
            cpt_code="90847",
            gross_charge=312.0,
            location="Medical Center",
            payer="Cash",
            procedure_description="Hc Php Youth Iop Family Therapy",
            procedure_identifier="907804356",
        ),
    ]

    assert sorted(actual_result) == sorted(expected_result)


def test_institution_name(parser):
    assert LLUHChargeMasterParser.institution_name == "LLUH"
    assert parser.institution_name == "LLUH"


def test_artifact_urls(parser):
    assert LLUHChargeMasterParser.artifact_urls == LLUHChargeMasterParser.ARTIFACT_URLS
    assert parser.artifact_urls == LLUHChargeMasterParser.ARTIFACT_URLS
