import re
import openpyxl

from .parsers import ChargeMasterEntry


class RadyChargeMasterParser:
    INSTITUTION_NAME = "Rady"
    ARTIFACT_URL = "https://www.rchsd.org/documents/2022/07/chargemaster-2.xlsx/"

    @property
    def institution_name(self):
        return RadyChargeMasterParser.INSTITUTION_NAME

    @property
    def artifact_urls(self):
        return [RadyChargeMasterParser.ARTIFACT_URL]

    def parse_artifacts(self, artifacts):
        wb = openpyxl.load_workbook(artifacts[RadyChargeMasterParser.ARTIFACT_URL])
        for i, row in enumerate(wb.worksheets[0].iter_rows()):
            if i == 0:
                continue
            else:
                yield ChargeMasterEntry(
                    procedure_identifier = i,
                    procedure_description = row[0].value[4:].strip(), # Remove "RCH "
                    gross_charge = float(row[1].value),
                )