from .parsers import ChargeMasterEntry, ChargeMasterParser
import csv
import re
import io


class SouthwestChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "Southwest"
    ARTIFACT_URL = "https://uhsfilecdn.eskycity.net/ac/233059262_southwest-healthcare-system_standardcharges.csv"
    ARTIFACT_URLS = (ARTIFACT_URL,)

    def parse_artifacts(self, artifacts):
        KEY_COLUMNS = (
            "Facility",
            "Description",
            "CDM",
            "Code Type",
            "DRG (If Applicable)",
            "CPT/HCPCS (If Applicable)",
            "EAPG (If Applicable)",
            "APC (If Applicable)",
            "Rev Code (If Applicable)",
            "Gross Charge",
            "Cash Price",
            "Minimum",
            "Maximum",
        )

        reader = csv.reader(io.TextIOWrapper(artifacts[self.ARTIFACT_URL]))
        headers = None
        for row in reader:
            if headers is None:
                # We're hunting for the header row - if we find at least five of the candidate columns it's good
                count_good_columns = 0
                temp_headers = {}
                for i, value in enumerate(row):
                    # Note the position of the candidate column header
                    temp_headers[i] = value.strip()

                    # Check to see if we recognize this colum header
                    if temp_headers[i] in KEY_COLUMNS:
                        count_good_columns += 1

                # We found a good header row, keep it and start collecting data
                if count_good_columns > 5:
                    headers = temp_headers

            else:
                row_dict_values = {}
                for index, column in headers.items():
                    value = row[index].strip()
                    row_dict_values[column] = value

                procedure_identifier = None
                procedure_description = None
                ms_drg_code = None
                cpt_code = None
                hcpcs_code = None
                ndc_code = None
                max_reimbursement = None
                min_reimbursement = None
                expected_reimbursement = None
                in_patient = None
                payer = None
                plan = None
                gross_charge = None
                nubc_revenue_code = None
                extra_data = {}

                expected_reimbursement = {}

                for key, value in row_dict_values.items():
                    if key not in KEY_COLUMNS:
                        # These are contract rates - "-1" means N/A for that institution so skip
                        if value and value != "-1":
                            value = value.replace("$", "")
                            value = value.split(" ")[0]
                            expected_reimbursement[key] = float(value.replace(",", ""))

                procedure_description = row_dict_values["Description"]
                procedure_identifier = row_dict_values["CDM"]

                temp = row_dict_values["CPT/HCPCS (If Applicable)"]
                if temp:
                    if re.match(r"[0-9]{4}[0-9A-Za-z]$", temp):
                        cpt_code = temp
                    else:
                        hcpcs_code = temp

                temp = row_dict_values["DRG (If Applicable)"]
                if temp:
                    if temp.isnumeric():
                        # MS-DRG < 999 - to be formally correct pad to 3
                        temp = str(temp).zfill(3)
                    ms_drg_code = temp

                temp = row_dict_values["EAPG (If Applicable)"]
                if temp:
                    extra_data["EAPG (If Applicable)"] = temp

                temp = row_dict_values["APC (If Applicable)"]
                if temp:
                    extra_data["APC (If Applicable)"] = temp

                temp = row_dict_values["Rev Code (If Applicable)"]
                if temp:
                    nubc_revenue_code = temp

                temp = row_dict_values["Gross Charge"]
                if temp:
                    if temp != "-1":
                        gross_charge = float(temp.replace(",", ""))

                temp = row_dict_values["Cash Price"]
                if temp:
                    if temp != "-1":
                        temp = float(temp.replace(",", ""))
                        expected_reimbursement["Cash"] = temp

                temp = row_dict_values["Minimum"]
                if temp:
                    min_reimbursement = float(temp.replace(",", ""))

                temp = row_dict_values["Maximum"]
                if temp:
                    max_reimbursement = float(temp.replace(",", ""))

                if not procedure_identifier:
                    # Make up a unique identifier
                    if cpt_code:
                        procedure_identifier = f"CPT_{cpt_code}"
                    elif hcpcs_code:
                        procedure_identifier = f"HCPCS_{hcpcs_code}"
                    elif ms_drg_code:
                        procedure_identifier = f"MS_DRG_{ms_drg_code}"

                if not extra_data:
                    extra_data = None

                for payer, expected in expected_reimbursement.items():
                    if payer == "Cash":
                        yield ChargeMasterEntry(
                            procedure_identifier=procedure_identifier,
                            procedure_description=procedure_description,
                            gross_charge=expected,
                            ms_drg_code=ms_drg_code,
                            hcpcs_code=hcpcs_code,
                            cpt_code=cpt_code,
                            extra_data=extra_data,
                            payer="Cash",
                        )
                    else:
                        yield ChargeMasterEntry(
                            procedure_identifier=procedure_identifier,
                            procedure_description=procedure_description,
                            gross_charge=gross_charge,
                            ms_drg_code=ms_drg_code,
                            hcpcs_code=hcpcs_code,
                            cpt_code=cpt_code,
                            extra_data=extra_data,
                            min_reimbursement=min_reimbursement,
                            max_reimbursement=max_reimbursement,
                            expected_reimbursement=expected,
                            payer=payer,
                        )
