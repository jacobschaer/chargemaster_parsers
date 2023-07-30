from .parsers import ChargeMasterEntry, ChargeMasterParser
import csv
import re
import io


class TriCityChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "Tri-City"
    ARTIFACT_URL = "https://www.tricitymed.org/wp-content/uploads/2022/11/952126937_Tri-City-Medical-Center_standardcharges.csv"
    ARTIFACT_URLS = (ARTIFACT_URL,)

    def parse_artifacts(self, artifacts):
        KEY_COLUMNS = (
            "Code Type",
            "Code",
            "Description",
            "Patient Type",
            "Rev Code",
            "Gross Charge",
            "Cash Price",
            "Min ($)",
            "Max ($)",
        )

        reader = csv.reader(
            io.TextIOWrapper(
                artifacts[self.ARTIFACT_URL], encoding="cp1252", newline=""
            )
        )
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
                max_reimbursement = None
                min_reimbursement = None
                expected_reimbursement = None
                in_patient = None
                gross_charge = None
                nubc_revenue_code = None
                extra_data = {}

                expected_reimbursement = {}

                for key, value in row_dict_values.items():
                    if key not in KEY_COLUMNS:
                        for payer in key.split("\n"):
                            # These are contract rates - "-1" means N/A for that institution so skip
                            if value and value != "NA":
                                value = value.replace("$", "")
                                value = value.split(" ")[0]
                                try:
                                    expected_reimbursement[payer.strip()] = float(
                                        value.replace(",", "")
                                    )
                                except ValueError:
                                    pass

                procedure_description = row_dict_values["Description"]

                code_type = row_dict_values["Code Type"]
                code = row_dict_values["Code"]
                procedure_identifier = code_type + "_" + code

                if procedure_description:
                    match = re.match(rf'^\s*({code})?[^a-zA-Z0-9()]*(.+?)\s*$', procedure_description)
                    procedure_description = match.groups()[1]

                if code_type == "DRG":
                    ms_drg_code = str(int(code)).rjust(3, "0")
                elif code_type == "CDM":
                    if re.match(r"^[0-9]{4}[0-9A-Za-z]$", code):
                        cpt_code = code
                    elif "|" in code:
                        # These are likely two HCPCs combined with | but rare
                        extra_data["Code Type"] = code_type
                        extra_data["Code"] = code
                    else:
                        hcpcs_code = code
                elif code_type in ("ICD10", "ICD9", "Softcoded", "Pharmacy"):
                    extra_data["Code Type"] = code_type
                    extra_data["Code"] = code

                temp = row_dict_values["Rev Code"]
                if temp and temp != "NA":
                    nubc_revenue_code = temp
                in_patient = row_dict_values["Patient Type"] == "IP"

                gross_charge = self.parse_price(row_dict_values["Gross Charge"])
                cash_price = self.parse_price(row_dict_values["Cash Price"])
                if cash_price is not None:
                    expected_reimbursement["Cash"] = cash_price

                min_reimbursement = self.parse_price(row_dict_values["Min ($)"])
                max_reimbursement = self.parse_price(row_dict_values["Max ($)"])

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
                            nubc_revenue_code=nubc_revenue_code,
                            payer="Cash",
                            in_patient=in_patient,
                        )
                    else:
                        yield ChargeMasterEntry(
                            procedure_identifier=procedure_identifier,
                            procedure_description=procedure_description,
                            gross_charge=gross_charge,
                            ms_drg_code=ms_drg_code,
                            hcpcs_code=hcpcs_code,
                            nubc_revenue_code=nubc_revenue_code,
                            cpt_code=cpt_code,
                            extra_data=extra_data,
                            min_reimbursement=min_reimbursement,
                            max_reimbursement=max_reimbursement,
                            expected_reimbursement=expected,
                            payer=payer,
                            in_patient=in_patient,
                        )
