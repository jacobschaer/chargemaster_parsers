import re
import openpyxl

from .parsers import ChargeMasterEntry, ChargeMasterParser


class RadyChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "Rady"
    ARTIFACT_URL = "https://www.rchsd.org/documents/2022/07/chargemaster-2.xlsx/"
    ARTIFACT_URLS = (ARTIFACT_URL,)

    def parse_artifacts(self, artifacts):
        wb = openpyxl.load_workbook(artifacts[RadyChargeMasterParser.ARTIFACT_URL])
        itemcode_index = None
        description_index = None
        price_index = None
        for i, row in enumerate(wb.worksheets[0].iter_rows()):
            if i == 0:
                header = [x.value.strip() for x in row]
                try:
                    itemcode_index = header.index("Itemcode")
                except ValueError as ex:
                    pass

                try:
                    description_index = header.index("Item Description")
                except ValueError:
                    description_index = header.index("Procedure Name")

                try:
                    price_index = header.index("Load Price")
                except ValueError:
                    price_index = header.index("Price")
            else:
                procedure_identifier = i
                if itemcode_index is not None:
                    procedure_identifier = row[itemcode_index].value

                description = row[description_index].value[4:].strip()  # Remove "RCH "

                try:
                    price = row[price_index].value
                    if type(price) is str:
                        price = float(price.replace(",", ""))

                    yield ChargeMasterEntry(
                        procedure_identifier=procedure_identifier,
                        procedure_description=description,
                        gross_charge=price,
                    )
                except ValueError as ex:
                    pass
