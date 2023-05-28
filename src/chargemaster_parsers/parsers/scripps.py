import re
import csv
import io

from .parsers import ChargeMasterEntry

NDC_REGEX = r"^(\d{4}-\d{4}-\d{2}|\d{5}-(?:\d{3}-\d{2}|\d{4}-\d{1,2}))"
NUBC_REV_CODE_REGEX = r'(^[0-9]{4})\s*-\s*'
CODE_MATCHERS = (
    ("CPT", r'^CPT.+?([0-9]+)$'),
    ("HCPCS", r'^HCPCS\s+(.+)$'),
    ("DRG", r"^MS-DRG\s+V[0-9]+\s+\(FY [0-9]+\)\s+(.+?)$")
)

class ScrippsChargeMasterParser:
    INSTITUTION_NAME = "Scripps"
    SCRIPPS_GREEN_HOSPITAL_ARTIFACT_URL = "https://apps.scripps.org/pricetransparency/951684089_ScrippsGreenHospital_standardcharges.csv"
    SCRIPPS_MEMORIAL_HOSPITAL_ENCINITAS_ARTIFACT_URL = "https://apps.scripps.org/pricetransparency/951684089_ScrippsMemorialHospitalEncinitas_standardcharges.csv"
    SCRIPPS_MEMORIAL_HOSPITAL_LA_JOLLA_ARTIFACT_URL = "https://apps.scripps.org/pricetransparency/951684089_ScrippsMemorialHospitalLaJolla_standardcharges.csv"
    SCRIPPS_MERCY_HOSPITAL_SAN_DIEGO_ARTIFACT_URL = "https://apps.scripps.org/pricetransparency/951684089_ScrippsMercyHospitalSanDiego_standardcharges.csv"
    SCRIPPS_MERCY_HOSPITAL_CHULA_VISTA_ARTIFACT_URL = "https://apps.scripps.org/pricetransparency/951684089_ScrippsMercyHospitalChulaVista_standardcharges.csv"

    @property
    def institution_name(self):
        return ScrippsChargeMasterParser.INSTITUTION_NAME

    @property
    def artifact_urls(self):
        return [
            ScrippsChargeMasterParser.SCRIPPS_GREEN_HOSPITAL_ARTIFACT_URL,
            ScrippsChargeMasterParser.SCRIPPS_MEMORIAL_HOSPITAL_ENCINITAS_ARTIFACT_URL,
            ScrippsChargeMasterParser.SCRIPPS_MEMORIAL_HOSPITAL_LA_JOLLA_ARTIFACT_URL,
            ScrippsChargeMasterParser.SCRIPPS_MERCY_HOSPITAL_SAN_DIEGO_ARTIFACT_URL,
            ScrippsChargeMasterParser.SCRIPPS_MERCY_HOSPITAL_CHULA_VISTA_ARTIFACT_URL,
        ]

    def parse_artifacts(self, artifacts):
        for artifact_url in self.artifact_urls:
            reader = csv.DictReader(io.TextIOWrapper(artifacts[artifact_url]), delimiter="|")
            for row in reader:
                location = None
                procedure_identifier = None
                procedure_description = None
                ndc_code = None
                nubc_revenue_code = None
                cpt_code = None
                hcpcs_code = None
                ms_drg_code = None
                max_reimbursement = None
                min_reimbursement = None
                expected_reimbursement = None
                in_patient = None
                payer = None
                plan = None
                gross_charge = None

                gross_charges_outpatient = None
                gross_charges_inpatient = None
                expected_inpatient_reimbursement = None
                expected_outpatient_reimbursement = None

                location = row["LOCATION"].strip()
                procedure_identifier = row["PROCEDURE CODE"]

                if procedure_identifier.startswith('MS'):
                    ms_drg_code = procedure_identifier[2:]
                procedure_description = row["PROCEDURE DESCRIPTION"]

                payer = row["PAYER"].split("[")[0].strip()
                plan = row["PLAN"].split("[")[0].strip()

                try:
                    cash = float(row["CASH/SELF PAY"])
                except ValueError:
                    pass

                try:
                    gross_charges_inpatient = float(row["GROSS CHARGES IP"])
                except ValueError:
                    pass

                try:
                    expected_inpatient_reimbursement = float(row["IP_EXPECTED_REIMBURSMENT"])
                except ValueError:
                    pass

                try:
                    gross_charges_outpatient = float(row["GROSS CHARGES OP"])
                except ValueError:
                    pass

                try:
                    expected_outpatient_reimbursement = float(row["OP_EXPECTED_REIMBURSMENT"])
                except ValueError:
                    pass

                # TODO: CASH
                # TODO: Avoid duplicates


                for plan in plan.split(','):
                    if gross_charges_inpatient:
                        yield ChargeMasterEntry(
                            location = location,
                            procedure_identifier = procedure_identifier,
                            procedure_description = procedure_description,
                            ndc_code = ndc_code,
                            nubc_revenue_code = nubc_revenue_code,
                            cpt_code = cpt_code,
                            hcpcs_code = hcpcs_code,
                            ms_drg_code = ms_drg_code,
                            max_reimbursement = max_reimbursement,
                            min_reimbursement = min_reimbursement,
                            expected_reimbursement = expected_inpatient_reimbursement,
                            in_patient = True,
                            payer = payer,
                            plan = plan.strip(),
                            gross_charge = gross_charges_inpatient,
                        )
                    if gross_charges_outpatient:
                        yield ChargeMasterEntry(
                            location = location,
                            procedure_identifier = procedure_identifier,
                            procedure_description = procedure_description,
                            ndc_code = ndc_code,
                            nubc_revenue_code = nubc_revenue_code,
                            cpt_code = cpt_code,
                            hcpcs_code = hcpcs_code,
                            ms_drg_code = ms_drg_code,
                            max_reimbursement = max_reimbursement,
                            min_reimbursement = min_reimbursement,
                            expected_reimbursement = expected_outpatient_reimbursement,
                            in_patient = False,
                            payer = payer,
                            plan = plan.strip(),
                            gross_charge = gross_charges_outpatient,
                        )