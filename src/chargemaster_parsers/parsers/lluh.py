from .parsers import ChargeMasterEntry, ChargeMasterParser
import csv
import re
import io


class LLUHChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "LLUH"
    URL_TO_INSTITUTION = {
        "https://lluh.org/sites/lluh.org/files/953522679_lomalindauniversitymedicalcenter_standardcharges.csv": "Medical Center",
        "https://lluh.org/sites/lluh.org/files/463214504_lomalindauniversitychildrenshospital_standardcharges.csv": "Children's Hospital",
        "https://lluh.org/sites/lluh.org/files/330245579_lomalindauniversitybehavioralmedicalcenter_standardcharges.csv": "Behavioral Medicine Center",
        "https://lluh.org/sites/lluh.org/files/371705906_lomalindauniversitymedicalcenter-murrieta_standardcharges.csv": "Medical Center – Murrieta",
    }
    ARTIFACT_URLS = (url for url in URL_TO_INSTITUTION.keys())

    def parse_artifacts(self, artifacts):
        KEY_COLUMNS = (
            "procedure",
            "code",
            "description",
            "gross_pay",
            "cash_pay",
            "minimum",
            "maximum",
        )

        for artifact in artifacts:
            location = self.URL_TO_INSTITUTION[artifact]
            reader = csv.reader(io.TextIOWrapper(artifacts[artifact], encoding='cp1252', newline=''))
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
                    gross_charge = None
                    extra_data = {}

                    expected_reimbursement = {}

                    for key, value in row_dict_values.items():
                        if key not in KEY_COLUMNS:
                            price = self.parse_price(value)
                            if price is not None:
                                expected_reimbursement[key.replace("_", " ")] = price

                    procedure_description = row_dict_values["description"]
                    procedure_identifier = row_dict_values["procedure"]

                    temp = row_dict_values["code"]
                    if temp:
                        known_code = False
                        for code_type, code_regex in (
                            ("ms_drg", r"MS-DRG V37 \(FY2020\) (.+?)$"),
                            ("cpt", r"CPT.+? (.+?)$"),
                            ("hcpcs", r"HCPCS (.+?)$"),
                        ):
                            match = re.match(code_regex, temp)
                            if match:
                                value = match.groups()[0].upper().strip()
                                if code_type == "ms_drg":
                                    ms_drg_code = value
                                elif code_type == "cpt":
                                    cpt_code = value
                                elif code_type == "hcpcs":
                                    hcpcs_code = value
                                known_code = True
                                break
                        if not known_code:
                            extra_data["code"] = temp

                    gross_charge = self.parse_price(row_dict_values["gross_pay"])
                    cash_price = self.parse_price(row_dict_values["cash_pay"])
                    if cash_price:
                        expected_reimbursement["Cash"] = cash_price
                    min_reimbursement = self.parse_price(row_dict_values["minimum"])
                    max_reimbursement = self.parse_price(row_dict_values["maximum"])

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
                                location=location,
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
                                location=location,
                            )
