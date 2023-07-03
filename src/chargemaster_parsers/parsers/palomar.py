import re
import openpyxl

from .parsers import ChargeMasterEntry, ChargeMasterParser


class PalomarChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "Palomar"
    ARTIFACT_URL = "https://www.palomarhealth.org/wp-content/uploads/2023/06/Copy-of-05.22.2023-CDM-Extract-Distribution-002.xlsx"
    ARTIFACT_URLS = (ARTIFACT_URL,)

    def parse_artifacts(self, artifacts):
        wb = openpyxl.load_workbook(artifacts[PalomarChargeMasterParser.ARTIFACT_URL])
        cdm_column = None
        cdm_desc_column = None
        price_column = None
        found_headers = False
        for row in wb.worksheets[0].iter_rows():
            if not found_headers:
                for i, cell in enumerate(row[:3]):
                    if cell.value.strip() == "CDM":
                        cdm_column = i
                        found_headers = True
                    elif cell.value.strip() == "CDM_DESC":
                        cdm_desc_column = i
                        found_headers = True
                    elif cell.value.strip() == "PRICE":
                        price_column = i
                        found_headers = True
            else:
                cdm = row[cdm_column].value.strip()
                cdm_desc = row[cdm_desc_column].value.strip()
                price = float(
                    row[price_column].value.strip().replace("$", "").replace(",", "")
                )

                yield ChargeMasterEntry(
                    procedure_identifier=cdm,
                    procedure_description=cdm_desc,
                    gross_charge=price,
                )
