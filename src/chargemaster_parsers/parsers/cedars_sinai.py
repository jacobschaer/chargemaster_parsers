from .parsers import ChargeMasterEntry, ChargeMasterParser
import openpyxl


class CedarsSinaiChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "Cedars-Sinai"
    ARTIFACT_URL = "https://www.cedars-sinai.org/content/dam/cedars-sinai/billing-insurance/documents/cedars-sinai-changemaster-july-2022.xlsx"
    ARTIFACT_URLS = (ARTIFACT_URL,)

    def parse_artifacts(self, artifacts):
        for artifact_url, artifact in artifacts.items():
            wb = openpyxl.load_workbook(artifact)
            charge_code_column = None
            charge_code_description_column = None
            cpt_hcpcs_code_column = None
            op_charge_column = None
            ip_charge_column = None

            for row in wb.worksheets[0].iter_rows(min_row=5):
                values = []
                for cell in row[:5]:
                    if type(cell.value) in (int, float):
                        values.append(cell.value)
                    elif cell.value:
                        values.append(cell.value.strip())
                    else:
                        values.append(None)
                if (
                    charge_code_column,
                    charge_code_description_column,
                    cpt_hcpcs_code_column,
                    op_charge_column,
                    ip_charge_column,
                ) == (None, None, None, None, None):
                    if values == [
                        "EAP PROC CODE",
                        "EAP PROC NAME",
                        "DEFAULT CPT/ HCPCS CODE",
                        "DEFAULT OP FEE SCHEDULE",
                        "IP/ED FEE SCHEDULE",
                    ]:
                        (
                            charge_code_column,
                            charge_code_description_column,
                            cpt_hcpcs_code_column,
                            op_charge_column,
                            ip_charge_column,
                        ) = (0, 1, 2, 3, 4)
                else:
                    charge_code = values[charge_code_column]
                    charge_code_desc = values[charge_code_description_column]
                    charge = values[op_charge_column]
                    if charge is not None:
                        charge = float(str(charge).replace("$", "").replace(",", ""))

                    yield ChargeMasterEntry(
                        location="all",
                        procedure_identifier=charge_code,
                        procedure_description=charge_code_desc,
                        gross_charge=charge,
                        in_patient=False,
                    )

                    cpt_hcps_code = values[cpt_hcpcs_code_column]
                    cpt_code = None
                    hcpcs_code = None
                    if cpt_hcps_code != None:
                        if (
                            isinstance(cpt_hcps_code, int)
                            and len(str(cpt_hcps_code)) == 5
                        ):
                            cpt_code = cpt_hcps_code
                        else:
                            if len(cpt_hcps_code) == 5 and cpt_hcps_code[0].isnumeric():
                                cpt_code = cpt_hcps_code
                            else:
                                hcpcs_code = cpt_hcps_code

                        if values[ip_charge_column] != None:
                            charge = values[ip_charge_column]
                            if charge is not None:
                                charge = float(
                                    str(charge).replace("$", "").replace(",", "")
                                )

                        yield ChargeMasterEntry(
                            location="all",
                            procedure_identifier=charge_code,
                            procedure_description=charge_code_desc,
                            gross_charge=charge,
                            in_patient=True,
                            cpt_code=cpt_code,
                            hcpcs_code=hcpcs_code,
                        )
