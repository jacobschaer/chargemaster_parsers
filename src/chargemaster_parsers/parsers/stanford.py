import re
import json
import pprint

from .parsers import ChargeMasterEntry, ChargeMasterParser

class StanfordChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "Stanford"
    ARTIFACT_URL = "https://stanfordhealthcare.org/content/dam/SHC/patientsandvisitors/pricingtransparency/946174066_stanford-health-care_standardcharges.json"
    ARTIFACT_URLS = (ARTIFACT_URL, )

    def parse_artifacts(self, artifacts):
        hcpcs_gross_charges = dict()

        for section_name, section in json.load(artifacts[self.ARTIFACT_URL]).items():
            if section_name.strip() == "File Summary":
                effective_date = section[0]["Prices Posted And Effective"]
                print(f"Effective Date: {effective_date}")
                # [{'Discounted Cash Price': 'This section presents information regarding '
                #                            'discounted cash pricing for those patients who '
                #                            'decide to pay without insurance coverage.',
                #   'File Disclaimer': 'The information contained in this file is intended for '
                #                      'informational purposes only and does not represent any '
                #                      'obligation or agreement.',
                #   'Gross Charges': 'Gross Charges',
                #   'Hospital Name': 'Stanford Health Care',
                #   'Inpatient De-identified Negotiated Charge': 'This section presents the '
                #                                                'de-identified minimum and '
                #                                                'maximum charge for items, '
                #                                                'services, and service packages '
                #                                                'that occur in the inpatient '
                #                                                'setting.',
                #   'Inpatient Payer Specific Charge': 'This section presents the payer specific '
                #                                      'negotiated charge for items, services, '
                #                                      'and service packages that occur in the '
                #                                      'inpatient setting.',
                #   'Outpatient De-identified Negotiated Charge': 'This section presents the '
                #                                                 'de-identified minimum and '
                #                                                 'maximum charge for items, '
                #                                                 'services, and service '
                #                                                 'packages that occur in the '
                #                                                 'outpatient setting.',
                #   'Outpatient Payer Specific Charge': 'This section presents the payer '
                #                                       'specific negotiated charge for items, '
                #                                       'services, and service packages that '
                #                                       'occur in the outpatient setting.',
                #   'Payer Disclaimer': 'In the absence of payment rates by plan type (HMO vs '
                #                       'PPO), unless otherwise noted, please assume all plans '
                #                       'are contracted under the same payer specific negotiated '
                #                       'charge.',
                #   'Prices Posted And Effective': '12/22/2022 12:00:00 AM',
                #   'Professional Charges': 'This section presents the standard gross charge, '
                #                           'payer specific negotiated charge, and de-identified '
                #                           'minimum and maximum charge for items and services.'}]

            elif section_name.strip() == "Gross Charges":
                # Valid keys per row are ['Procedure', 'Code', 'Rev Code', 'Procedure Description', 'Quantity', 'Price', 'Discount Cash Price', 'NDC']
                # Example:
                # {'Code': 'HCPCS C1713',
                #  'Discount Cash Price': 266.56,
                #  'Price': 666.4,
                #  'Procedure': 317184,
                #  'Procedure Description': 'SCREW MATRIXMIDFACE 1.55MM',
                #  'Quantity': 'N/A'},
                codes = set()
                for entry in section:
                    cpt_code = None
                    hcpcs_code = None
                    try:
                        procedure_description = entry["Procedure Description"]
                        procedure_identifier = entry["Procedure"]
                        gross_charge = entry["Price"]
                        quantity = entry["Quantity"]
                        cash_price = entry["Discount Cash Price"]
                    except KeyError:
                        # Some rows are empty for some reason
                        continue

                    code = entry.get('Code', None)
                    if code:
                        if code.lower().strip().startswith("hcpcs"):
                            _, hcpcs_code = code.split(" ")
                        elif code.lower().strip().startswith("cpt"):
                            _, cpt_code = code.split(" ")

                    # Always yield the cash rates - HCPCS codes will get payer
                    # specific values in a later section
                    yield ChargeMasterEntry(
                        procedure_identifier = procedure_identifier,
                        procedure_description = procedure_description,
                        gross_charge = cash_price,
                        cpt_code = cpt_code,
                        hcpcs_code = hcpcs_code,
                        payer = "Cash",
                        quantity = quantity
                    )

            elif section_name.strip() == "Discounted Cash Pricing Policy":
                # Descriptive text only
                pass

            elif section_name.strip() == "Professional Charges":
                # Valid Keys: ['Item Code', 'Description', 'HCPCS', 'Facility', 'Location', 'Payer Source', 'CDM - Standard Gross Charge', 'Payer', 'Payer Specific Negotiated Charge', 'Payer Specific Negotiated Charge - Min', 'Payer Specific Negotiated Charge - Max', 'Discounted Cash Price', 'Specialty']
                # Example:
                # {'CDM - Standard Gross Charge': 1931.0,
                #  'Description': 'SPINE FUSION EXTRA SEGMENT',
                #  'Discounted Cash Price': 965.5,
                #  'Facility': 'FACILITY',
                #  'HCPCS': '22634',
                #  'Item Code': '22634_8',
                #  'Location': 'Stanford Hospital Clinics',
                #  'Payer': 'Anthem_Blue_Cross',
                #  'Payer Source': 'Fee Schedule',
                #  'Payer Specific Negotiated Charge': 1607.18,
                #  'Payer Specific Negotiated Charge - Max': 1852.55,
                #  'Payer Specific Negotiated Charge - Min': 99.03},
                for entry in section:
                    if not entry:
                        continue

                    gross_charge = entry["CDM - Standard Gross Charge"]
                    procedure_identifier = entry["Item Code"]
                    procedure_description = entry["Description"]
                    payer = entry["Payer"].replace("_", " ")
                    expected_reimbursement = entry["Payer Specific Negotiated Charge"]
                    hcpcs_code = entry["HCPCS"]
                    max_reimbursement = entry["Payer Specific Negotiated Charge - Max"]
                    min_reimbursement = entry["Payer Specific Negotiated Charge - Min"]
                    location = entry["Location"]


                    yield ChargeMasterEntry(
                        procedure_identifier = procedure_identifier,
                        procedure_description = procedure_description,
                        gross_charge = gross_charge,
                        hcpcs_code = hcpcs_code,
                        payer = payer,
                        location = location,    
                        expected_reimbursement = expected_reimbursement,
                        min_reimbursement = min_reimbursement,
                        max_reimbursement = max_reimbursement,
                    )

            elif section_name.strip() == "Professional Charges Exceptions":
                # Not useful - presently mostly anesthesia rates and descriptive text
                pass
            elif section_name.strip() == "Inpatient De-identified Minimum Negotiated Charge":
                # Valid keys: ['MS-DRG', 'Description', 'De-Identified Minimum Negotiated Charge']
                # Example:
                #  {'De-Identified Minimum Negotiated Charge': 64864.0,
                #   'Description': 'Other Multiple Significant Trauma With Cc',
                #   'MS-DRG': '964'},
                pass
            elif section_name.strip() == "Inpatient De-identified Maximum Negotiated Charge":
                # Valid keys: ['MS-DRG', 'Description', 'De-Identified Maximum Negotiated Charge']
                # {'De-Identified Maximum Negotiated Charge': 315865.0,
                #  'Description': 'Non-Extensive O.R. Procedures Unrelated To Principal '
                #                 'Diagnosis With Cc',
                #  'MS-DRG': '988'},
                pass
            elif section_name.strip().startswith("Inpatient Payer Specific Charge"):
                # Valid keys: ['Payer', 'MS-DRG', 'Description', 'Payer Specific Negotiated Charge']
                # Example:
                #  {'Description': 'Other Multiple Significant Trauma Without Cc/Mcc',
                #   'MS-DRG': '965',
                #   'Payer': 'HealthNet',
                #   'Payer Specific Negotiated Charge': 159516.0}
                pass
            elif section_name.strip() == "Outpatient De-identified Minimum Negotiated Charge":
                # Valid keys: ['APC', 'Description', 'De-Identified Minimum Negotiated Charge']
                # Example:
                # {'APC': 'N905',
                #  'De-Identified Minimum Negotiated Charge': 4.0,
                #  'Description': 'Not Recognized by OPPS'}
                pass
            elif section_name.strip() == "Outpatient De-identified Maximum Negotiated Charge":
                # Valid keys: ['APC', 'Description', 'De-Identified Maximum Negotiated Charge']
                # Example:
                # {'APC': 'N905',
                #  'De-Identified Maximum Negotiated Charge': 4.0,
                #  'Description': 'Not Recognized by OPPS'}
                pass
            elif section_name.strip().startswith("Outpatient Payer Specific Charge"):
                # Valid keys:  ['Payer', 'APC', 'Description', 'Payer Specific Negotiated Charge']
                # Example:
                #  {'APC': 'N902',
                #   'Description': 'Packaged Services',
                #   'Payer': 'MultiPlan/PHCS/Beech Street',
                #   'Payer Specific Negotiated Charge': 179.0}
                pass

        return []
