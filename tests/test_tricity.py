from chargemaster_parsers.parsers import TriCityChargeMasterParser, ChargeMasterEntry

import tempfile
from openpyxl import Workbook
import pytest
import io
import os


@pytest.fixture
def parser():
    yield TriCityChargeMasterParser()


HEADER = "\n".join(
    [
        '"Price Transparency Machine Readable file as of July 1, 2022",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,',
        ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "To view file with all data in all columns visible perform the following steps. ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "1)Click on the triangle above row 1 and to the left of column A to highlight all cells.,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        "2)Double click on the column divider between column A and Column B,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",
        'Code Type,Code,Description,Patient Type,Rev Code,Gross Charge,Cash Price,Aetna HMO/PPO,"Anthem Blue Cross',
        'Anthem Covered California",Blue Shield of CA,Blue Shield Covered CA,Bright Health,Cigna HMO,Cigna PPO,Cigna Behavioral Health,Coventry First Health,HealthNet HMO/ PPO/Commercial,Kaiser Commercial,Magellan Comm / Medicare Advantage,Managed Health Network,Multiplan Commercial,Networks by Design,PHN / Oscar,"Sharp Health Plan (HMO,PPO,Covered California)",UHC,UHC Select,US Behavioral Health Plan (Optum),Coventry & Network by Design WC,Multiplan Workers Comp,Kaiser Medicare,"Anthem Blue Cross Snr Adv',
        "Blue Shield Senior Advantage",
        "Community Health Group Senior Advantage",
        "Easy Choice",
        "HealthNet Senior Advantage",
        "Humana",
        "Managed Health Network Advantage",
        "UHC Senior Advantage",
        'Imperial Health Plan","Astiva Health',
        'Clever Care of CA",Prospect Health, Aetna Sr Advantage ,"Central Health Plan',
        'Molina Sr Advantage",Molina Commercial Exchange,HN Bronze and Communitycare,Health Net Blue and Gold (UCSD), Min ($) , Max ($) ',
    ]
)


def test_ms_drg(parser):
    test_case = 'DRG,1,HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC,IP,NA , NA  , NA  , NA  , NA  , NA ,"$322,555.66 ", NA , NA , NA , NA , NA , NA , NA , NA , NA , 70% of gross charges , NA ,"$337,060.32 ", 55% of gross charges  ," $64,336 days 1-8, $4,843 days 9+ "," $60,182 days 1-8, $4,510 days 9+  ", NA ,"$337,397.38 ","$344,283.04 ","$240,757.37 ","$240,757.37 ","$240,757.37 ","$240,757.37 ","$240,757.37 ","$240,757.37 ","$325,022.45 ","$337,060.32 ","$361,136.05 ","$240,757.37 ","$361,136.05 "'
    test_case = HEADER + "\n" + test_case
    actual_result = list(
        parser.parse_artifacts(
            {
                TriCityChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_case.encode("utf-8")
                )
            }
        )
    )

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=322555.66,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Blue Shield Covered CA",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=337060.32,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="PHN / Oscar",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=64336.0,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="UHC",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=60182.0,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="UHC Select",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=337397.38,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Coventry & Network by Design WC",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=344283.04,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Multiplan Workers Comp",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Kaiser Medicare",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Anthem Blue Cross Snr Adv",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Blue Shield Senior Advantage",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Community Health Group Senior Advantage",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Easy Choice",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="HealthNet Senior Advantage",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Humana",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Managed Health Network Advantage",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="UHC Senior Advantage",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Imperial Health Plan",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Astiva Health",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Clever Care of CA",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Prospect Health",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Aetna Sr Advantage",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Central Health Plan",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=240757.37,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Molina Sr Advantage",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=325022.45,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Molina Commercial Exchange",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=337060.32,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="HN Bronze and Communitycare",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
        ChargeMasterEntry(
            expected_reimbursement=361136.05,
            max_reimbursement=361136.05,
            min_reimbursement=240757.37,
            ms_drg_code="001",
            payer="Health Net Blue and Gold (UCSD)",
            procedure_description="HEART TRANSPLANT OR IMPLANT OF HEART ASSIST SYSTEM WITH MCC",
            procedure_identifier="DRG_1",
            in_patient=True,
        ),
    ]

    assert sorted(expected_result) == sorted(actual_result)


def test_cpt_ip(parser):
    test_case = "CDM,51701,51701 INSERTION STRAIGHT CATHETERTECH FEE,IP,450,$306.00 ,$183.60 , NA , NA , NA  , NA , NA , NA , NA , NA , NA , NA , NA , NA , NA  ,$214.20 , NA , NA  ,$168.30 , NA , NA , NA , NA  , NA , NA  , NA  , NA  , NA  , NA  , NA  , NA  , NA  , NA ,$168.30 ,$214.20 "

    test_case = HEADER + "\n" + test_case
    actual_result = list(
        parser.parse_artifacts(
            {
                TriCityChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_case.encode("utf-8")
                )
            }
        )
    )

    expected_result = [
        ChargeMasterEntry(
            cpt_code="51701",
            expected_reimbursement=214.2,
            gross_charge=306.0,
            max_reimbursement=214.2,
            min_reimbursement=168.3,
            payer="Multiplan Commercial",
            procedure_description="51701 INSERTION STRAIGHT CATHETERTECH FEE",
            procedure_identifier="CDM_51701",
            in_patient=True,
            nubc_revenue_code="450",
        ),
        ChargeMasterEntry(
            cpt_code="51701",
            expected_reimbursement=168.3,
            gross_charge=306.0,
            max_reimbursement=214.2,
            min_reimbursement=168.3,
            payer="Sharp Health Plan (HMO,PPO,Covered California)",
            procedure_description="51701 INSERTION STRAIGHT CATHETERTECH FEE",
            procedure_identifier="CDM_51701",
            in_patient=True,
            nubc_revenue_code="450",
        ),
        ChargeMasterEntry(
            cpt_code="51701",
            gross_charge=183.6,
            payer="Cash",
            procedure_description="51701 INSERTION STRAIGHT CATHETERTECH FEE",
            procedure_identifier="CDM_51701",
            in_patient=True,
            nubc_revenue_code="450",
        ),
    ]

    assert sorted(expected_result) == sorted(actual_result)


def test_cpt_op(parser):
    test_case = "CDM,51701,51701 INSERTION STRAIGHT CATHETERTECH FEE,OP,450,$306.00 ,$183.60 , NA , NA , NA  , NA , NA , NA , NA , NA , NA , NA , NA , NA , NA  ,$214.20 , NA , NA  ,$168.30 , NA , NA , NA , NA  , NA , NA  , NA  , NA  , NA  , NA  , NA  , NA  , NA  , NA ,$168.30 ,$214.20 "

    test_case = HEADER + "\n" + test_case
    actual_result = list(
        parser.parse_artifacts(
            {
                TriCityChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_case.encode("utf-8")
                )
            }
        )
    )

    expected_result = [
        ChargeMasterEntry(
            cpt_code="51701",
            expected_reimbursement=214.2,
            gross_charge=306.0,
            max_reimbursement=214.2,
            min_reimbursement=168.3,
            payer="Multiplan Commercial",
            procedure_description="51701 INSERTION STRAIGHT CATHETERTECH FEE",
            procedure_identifier="CDM_51701",
            in_patient=False,
            nubc_revenue_code="450",
        ),
        ChargeMasterEntry(
            cpt_code="51701",
            expected_reimbursement=168.3,
            gross_charge=306.0,
            max_reimbursement=214.2,
            min_reimbursement=168.3,
            payer="Sharp Health Plan (HMO,PPO,Covered California)",
            procedure_description="51701 INSERTION STRAIGHT CATHETERTECH FEE",
            procedure_identifier="CDM_51701",
            in_patient=False,
            nubc_revenue_code="450",
        ),
        ChargeMasterEntry(
            cpt_code="51701",
            gross_charge=183.6,
            payer="Cash",
            procedure_description="51701 INSERTION STRAIGHT CATHETERTECH FEE",
            procedure_identifier="CDM_51701",
            in_patient=False,
            nubc_revenue_code="450",
        ),
    ]

    assert sorted(expected_result) == sorted(actual_result)


def test_hcpcs_code(parser):
    test_case = "CDM,P9021,E0262 RBC CP2D 500,IP,390,$285.00 ,$171.00 , NA , NA , NA  , NA , NA , NA , NA , NA , NA , NA , NA , NA , NA  ,$199.50 , NA , NA  ,$156.75 , NA , NA , NA , NA  , NA , NA  , NA  , NA  , NA  , NA  , NA  , NA  , NA  , NA ,$156.75 ,$199.50 "

    test_case = HEADER + "\n" + test_case
    actual_result = list(
        parser.parse_artifacts(
            {
                TriCityChargeMasterParser.ARTIFACT_URL: io.BytesIO(
                    test_case.encode("utf-8")
                )
            }
        )
    )

    expected_result = [
        ChargeMasterEntry(
            expected_reimbursement=199.5,
            gross_charge=285.0,
            hcpcs_code="P9021",
            in_patient=True,
            max_reimbursement=199.5,
            min_reimbursement=156.75,
            payer="Multiplan Commercial",
            procedure_description="E0262 RBC CP2D 500",
            procedure_identifier="CDM_P9021",
            nubc_revenue_code="390",
        ),
        ChargeMasterEntry(
            expected_reimbursement=156.75,
            gross_charge=285.0,
            hcpcs_code="P9021",
            in_patient=True,
            max_reimbursement=199.5,
            min_reimbursement=156.75,
            payer="Sharp Health Plan (HMO,PPO,Covered California)",
            procedure_description="E0262 RBC CP2D 500",
            procedure_identifier="CDM_P9021",
            nubc_revenue_code="390",
        ),
        ChargeMasterEntry(
            gross_charge=171.0,
            hcpcs_code="P9021",
            in_patient=True,
            payer="Cash",
            procedure_description="E0262 RBC CP2D 500",
            procedure_identifier="CDM_P9021",
            nubc_revenue_code="390",
        ),
    ]

    assert sorted(expected_result) == sorted(actual_result)


def test_institution_name(parser):
    assert TriCityChargeMasterParser.institution_name == "Tri-City"
    assert parser.institution_name == "Tri-City"


def test_artifact_urls(parser):
    assert (
        TriCityChargeMasterParser.artifact_urls
        == TriCityChargeMasterParser.ARTIFACT_URLS
    )
    assert parser.artifact_urls == TriCityChargeMasterParser.ARTIFACT_URLS
