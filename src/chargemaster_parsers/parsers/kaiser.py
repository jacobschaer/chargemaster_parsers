import csv
import zipfile
import io
import re

from .parsers import ChargeMasterEntry, ChargeMasterParser

class KaiserChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "Kaiser"
    # https://healthy.kaiserpermanente.org/southern-california/doctors-locations/standard-charges
    # For more
    # Note that 941105628 is the Kaiser EIN/TAX ID
    SAN_DIEGO_ARTIFACT_URL = "https://healthy.kaiserpermanente.org/content/dam/kporg/final/documents/health-plan-documents/coverage-information/machine-readable/941105628-san-diego-medical-center-standard-charges-scal-en.zip"
    ARTIFACT_URLS = (SAN_DIEGO_ARTIFACT_URL, )

    _LOCATION_FORMAL_NAMES = {
        "SanDiego": "San Diego",
    }

    def parse_artifacts(self, artifacts):
        with zipfile.ZipFile(artifacts[KaiserChargeMasterParser.SAN_DIEGO_ARTIFACT_URL]) as zip_file:
            for name in zip_file.namelist():
                match = re.match(r"(.+?)Kaiser(.+?)ChargeDescriptionMaster.csv$", name)
                if match:
                    location = self._LOCATION_FORMAL_NAMES[match.groups()[1]]

                    with zip_file.open(name) as csv_file:
                        for _ in range(4):
                            csv_file.readline()
                        for row in csv.DictReader(io.TextIOWrapper(csv_file)):
                            # Get rid of whitespace and garbage characters
                            filtered_row = {key.encode('ascii', 'ignore').decode().strip() : value.encode('ascii', 'ignore').decode().strip() for key, value in row.items()}
                            
                            charge_number = None
                            procedure_identifier = None
                            procedure_description = None
                            nubc_revenue_code = None
                            gross_charge = None
                            cpt_code = None
                            hcpcs_code = None

                            try:
                                charge_number = row.pop('Charge # \n(Px Code)')
                            except KeyError:
                                pass

                            try:
                                procedure_description = row.pop("Procedure Name")
                            except KeyError:
                                pass

                            try:
                                gross_charge = row.pop("Gross Charge").strip()
                                gross_charge = float(gross_charge.replace("$", "").replace(",",""))
                            except KeyError:
                                pass

                            try:
                                procedure_code = row.pop("Procedure Code (CPT / HCPCS)")
                                if len(procedure_code) == 5 and procedure_code[0].isnumeric():
                                    cpt_code = procedure_code
                                elif procedure_code:
                                    hcpcs_code = procedure_code
                            except KeyError:
                                pass

                            for key in row:
                                match = re.match(r"^(COMMERCIAL|MEDICAID) (INPATIENT|OUTPATIENT) - (.+?) PRICE$", key)
                                if match:
                                    payer, patient_classification, provider = match.groups()
                                    if patient_classification == "INPATIENT":
                                        in_patient = True
                                    elif patient_classification == "OUTPATIENT":
                                        in_patient = False
                                    plan = provider.strip()

                                    yield ChargeMasterEntry(
                                        charge_number = charge_number,
                                        procedure_description = procedure_description,
                                        gross_charge = gross_charge,
                                        cpt_code = cpt_code,
                                        hcpcs_code = hcpcs_code,
                                        payer = payer,
                                        plan = plan,
                                        in_patient = in_patient,
                                        location=location
                                    )