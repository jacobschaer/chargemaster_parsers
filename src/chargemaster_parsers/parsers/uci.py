from . import ChargeMasterEntry, ChargeMasterParser
import json

class UCIChargeMasterParser(ChargeMasterParser):
        INSTITUTION_NAME = "UCI"
        ARTIFACT_URL = "https://www.ucihealth.org/-/media/files/xlsx/patients-visitors/952226406-regentsoftheuniversityofcaliforniaatirvinehospital-standardcharges.json?la=en&hash=0C51B7235E101EB9E6FA133A2D3AC5C7F297EB5C"
        ARTIFACT_URLS = (ARTIFACT_URL, )

        def parse_artifacts(self, artifacts):
            for artifact_url, artifact in artifacts.items():
                data_dict = json.load(artifact)
                

                for category, entries in data_dict.items():
                    # Currently only parsing the 'Gross Charges' entries. This could be extended to parse the 
                    # other cateogories, such as 'Outpatient De-identified Negotiated Charge', but would require 
                    # some more research.
                    if category == 'Gross Charges':
                        location = None
                        procedure_identifier = None
                        procedure_description = None
                        hcpcs_code = None
                        in_patient = None
                        payer = None
                        cash_price = None
                        uci_hb_full_price = None
                        for entry in entries:
                            procedure_identifier = entry.get("Itemcode", None) 
                            procedure_description = entry.get("Description", None)
                            hcpcs_code = entry.get("CDM HCPCS", None)
                            uci_hb_full_price = entry.get("UCI HB OUTPATIENT", None)
                            cash_price = entry.get("UCI HB OUTPATIENT Discount Cash Price", None)

                            if uci_hb_full_price != 'N/A':
                                yield ChargeMasterEntry(
                                    location = 'standard',
                                    procedure_identifier = procedure_identifier,
                                    procedure_description = procedure_description,
                                    hcpcs_code = int(hcpcs_code),
                                    in_patient = False,
                                    payer = 'UCI HB',
                                    gross_charge = float(uci_hb_full_price.replace(',', '')))
                                
                            if cash_price != 'N/A':
                                yield ChargeMasterEntry(
                                    location = 'standard',
                                    procedure_identifier = procedure_identifier,
                                    procedure_description = procedure_description,
                                    hcpcs_code = int(hcpcs_code),
                                    in_patient = False,
                                    payer = 'Cash',
                                    gross_charge = float(cash_price.replace(',', '')))
        
