from . import ChargeMasterEntry, ChargeMasterParser
import json


class UCIChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "UCI"
    ARTIFACT_URL = "https://www.ucihealth.org/-/media/files/xlsx/patients-visitors/952226406-regentsoftheuniversityofcaliforniaatirvinehospital-standardcharges.json"
    ARTIFACT_URLS = (ARTIFACT_URL,)

    def parse_artifacts(self, artifacts):
            for artifact_url, artifact in artifacts.items():
                data_dict = json.load(artifact)
                prev_hcpcs = None

                for category, entries in data_dict.items():
                    if category == 'File Summary':
                        effective_date = entries[0]["Prices Posted And Effective"]
                        # "Hospital Name": "University of California Irvine Medical Center",
                        # "Prices Posted And Effective": "8/1/2022 12:00:00 AM",
                        # "File Disclaimer": "The information contained in this file is intended for informational purposes only and does not represent any obligation or agreement.",
                        # "Payer Disclaimer": "In the absence of payment rates by plan type (HMO vs PPO), unless otherwise noted, please assume all plans are contracted under the same payer specific negotiated charge.",
                        # "Gross Charge": "This section presents the standard gross charge for items And services.",
                        # "Discounted Cash Price": "This section presents information regarding discounted cash pricing for those patients who decide to pay without insurance coverage.",
                        # "Inpatient De-identified Negotiated Charge": "This section presents the de-identified minimum and maximum charge for items, services, and service packages that occur in the inpatient setting.",
                        # "Inpatient Payer Specific Charge": "This section presents the payer specific negotiated charge for items, services, and service packages that occur in the inpatient setting.",
                        # "Outpatient De-identified Negotiated Charge": "This section presents the de-identified minimum and maximum charge for items, services, and service packages that occur in the outpatient setting.",
                        # "Outpatient Payer Specific Charge": "This section presents the payer specific negotiated charge for items, services, and service packages that occur in the outpatient setting."
    
                    # Currently only parsing the 'Gross Charges' entries. This could be extended to parse the 
                    # other cateogories, such as 'Outpatient De-identified Negotiated Charge', but would require 
                    # some more research.
                    if category == 'Gross Charges':
                        for entry in entries:
                            procedure_identifier = entry.get("Itemcode", None) 
                            procedure_description = entry.get("Description", None)
                            hcpcs_code = entry.get("CDM HCPCS", None)
                            uci_hb_full_price = entry.get("UCI HB OUTPATIENT RATE Price", None)
                            cash_price = entry.get("UCI HB OUTPATIENT RATE Discounted Cash Price", None)
                            nubc_revenue_code = entry.get("CDM Revenue Code", None)

                            if uci_hb_full_price != 'N/A': # add UCI HB payer entry only if there's a price listed
                                if uci_hb_full_price is not None:
                                    yield ChargeMasterEntry(
                                        #procedure_identifier = procedure_identifier,
                                        procedure_description = procedure_description,
                                        hcpcs_code = hcpcs_code,
                                        in_patient = False,
                                        payer = 'UCI HB',
                                        gross_charge = float(uci_hb_full_price.replace(',', '')),
                                        extra_data = {'Itemcode': procedure_identifier},
                                        nubc_revenue_code = nubc_revenue_code,
                                    )

                            if cash_price != 'N/A': # add cash payer entry only if there's a price listed
                                if cash_price is not None:
                                    yield ChargeMasterEntry(
                                        #procedure_identifier = procedure_identifier,
                                        procedure_description = procedure_description,
                                        hcpcs_code = hcpcs_code,
                                        in_patient = False,
                                        payer = 'Cash',
                                        gross_charge = float(cash_price.replace(',', '')),
                                        extra_data = {'Itemcode': procedure_identifier},
                                        nubc_revenue_code = nubc_revenue_code,
                                    )
            
