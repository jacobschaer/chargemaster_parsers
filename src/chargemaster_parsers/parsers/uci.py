from . import ChargeMasterEntry, ChargeMasterParser
import json

class UCIChargeMasterParser(ChargeMasterParser):
        INSTITUTION_NAME = "UCI"
        ARTIFACT_URL = "https://www.ucihealth.org/-/media/files/xlsx/patients-visitors/952226406-regentsoftheuniversityofcaliforniaatirvinehospital-standardcharges.json"
        ARTIFACT_URLS = (ARTIFACT_URL, )

        def parse_artifacts(self, artifacts):
            for artifact_url, artifact in artifacts.items():
                data_dict = json.load(artifact)
                

                for category, entries in data_dict.items():
                    # Currently only parsing the 'Gross Charges' entries. This could be extended to parse the 
                    # other cateogories, such as 'Outpatient De-identified Negotiated Charge', but would require 
                    # some more research.
                    if category == 'Gross Charges':
                        for entry in entries:
                            procedure_identifier = entry.get("Itemcode", None) 
                            procedure_description = entry.get("Description", None)
                            hcpcs_code = entry.get("CDM HCPCS", None)
                            uci_hb_full_price = entry.get("UCI HB OUTPATIENT", None)
                            cash_price = entry.get("UCI HB OUTPATIENT Discount Cash Price", None)
                            if uci_hb_full_price != 'N/A': # add UCI HB payer entry only if there's a price listed
                                yield ChargeMasterEntry(
                                    procedure_identifier = procedure_identifier,
                                    procedure_description = procedure_description,
                                    hcpcs_code = hcpcs_code,
                                    in_patient = False,
                                    payer = 'UCI HB',
                                    gross_charge = float(uci_hb_full_price.replace(',', '')))
                                
                            if cash_price != 'N/A': # add cash payer entry only if there's a price listed
                                yield ChargeMasterEntry(
                                    procedure_identifier = procedure_identifier.strip(),
                                    procedure_description = procedure_description,
                                    hcpcs_code = hcpcs_code,
                                    in_patient = False,
                                    payer = 'Cash',
                                    gross_charge = float(cash_price.replace(',', '')))
        
