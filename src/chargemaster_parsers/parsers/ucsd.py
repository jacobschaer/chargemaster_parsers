import re
import json

from .parsers import ChargeMasterEntry, ChargeMasterParser

NDC_REGEX = r"^(\d{4}-\d{4}-\d{2}|\d{5}-(?:\d{3}-\d{2}|\d{4}-\d{1,2}))"
NUBC_REV_CODE_REGEX = r'(^[0-9]{4})\s*-\s*'
CODE_MATCHERS = (
    ("CPT", r'^CPT.+?([0-9]{4}[0-9A-Z])$'),
    ("HCPCS", r'^HCPCS\s+(.+)$'),
    ("DRG", r"^MS-DRG\s+V[0-9]+\s+\(FY [0-9]+\)\s+(.+?)$")
)

class UCSDChargeMasterParser(ChargeMasterParser):
    INSTITUTION_NAME = "UCSD"
    ARTIFACT_URL = "http://hsfiles.ucsd.edu/patientBilling/UC-San-Diego-Standard-Charges-956006144.json"
    ARTIFACT_URLS = (ARTIFACT_URL, )

    def parse_artifacts(self, artifacts):
        # What a disaster - instead of being able to just stream the binary contents with json.load as a utf-8
        # encoded file, UCSD appears to have included some unescaped quotes and bad UTF-8 sequences. But the default
        # codecs decode error functions end up leaving behind the quote, and registering a new one would lack sufficient
        # context to find the weird sequences
        decoded = artifacts[self.ARTIFACT_URL].read().decode('utf-8', errors='replace').replace('�"�', "").replace('"Where "Variable" exists,', '"Where \'Variable\' exists,')
        for row in json.loads(decoded):
            # Deal with non-ascii stuff and whitespace
            filtered_row = {}
            for key, value in row.items():
                filtered_key = key.encode('ascii', errors='ignore').decode().replace("_", " ").strip().upper()
                filtered_value = None
                if value:
                    filtered_value = value.encode('ascii', errors='ignore').decode().strip()
                filtered_row[filtered_key] = filtered_value

            location = None
            procedure_identifier = None
            procedure_description = None
            ndc_code = None
            nubc_revenue_code = None
            cpt_code = None
            hcpcs_code = None
            ms_drg_code = None
            max_reimbursement = None
            min_reimbursement = None
            expected_reimbursement = None
            in_patient = None
            payer = None
            plan = None
            gross_charge = None
            
            quantity = None
            in_patient_price = None

            try:
                # This can be "Variable" - which we'll treat as None
                min_reimbursement = float(filtered_row.pop('REIMB MIN'))
            except (KeyError, ValueError, TypeError):
                pass

            try:
                # This can be "Variable" - which we'll treat as None
                max_reimbursement = float(filtered_row.pop('REIMB MAX'))
            except (KeyError, ValueError, TypeError):
                pass

            if min_reimbursement and max_reimbursement:
                # Handle case where they're swapped for.. who knows what reason
                min_reimbursement, max_reimbursement = sorted((min_reimbursement, max_reimbursement))


            try:
                # This should only occur when "Code Type" == "ERX"
                ndc = filtered_row.pop('NDC')
                ndc_match = re.match(NDC_REGEX, ndc)
                if ndc_match:
                    ndc_code = ndc_match.groups()[0]
                else:
                    nubc_revenue_code_match = re.match(NUBC_REV_CODE_REGEX, ndc)
                    if nubc_revenue_code_match:
                        nubc_revenue_code = nubc_revenue_code_match.groups()[0]

            except (KeyError, ValueError, TypeError):
                pass

            try:
                # This field isn't very useful - sometimes a float, sometimes a string like "1 pill"
                quantity = filtered_row.pop('QUANTITY')
            except KeyError:
                pass

            # This is usually "Variable", sometimes "OP_PRICE" almost useless espeicallys since we have min/max and insurance rates
            try:
                in_patient_price = float(filtered_row.pop("IP PRICE"))
            except (KeyError, ValueError, TypeError):
                pass

            try:
                code = filtered_row.pop("CODE")
                if code is not None:
                    for candidate_code_type, code_matcher in CODE_MATCHERS:
                        match = re.match(code_matcher, code)
                        if match:
                            if candidate_code_type == "CPT":
                                cpt_code = match.groups()[0]
                            elif candidate_code_type == "HCPCS":
                                hcpcs_code = match.groups()[0]
                            elif candidate_code_type == "DRG":
                                ms_drg_code = match.groups()[0]
                            break
            except KeyError:
                pass

            try:
                procedure_identifier = filtered_row.pop("PROCEDURE")
            except (KeyError, ValueError):
                pass

            # If we didn't already figure out the NUBC code, try to find in the Rev Code field
            try:
                rev_code = filtered_row.pop("REV CODE")
                if rev_code is not None:
                    matched = False
                    if nubc_revenue_code is None:
                        nubc_revenue_code_match = re.match(NUBC_REV_CODE_REGEX, rev_code)
                        if nubc_revenue_code_match:
                            nubc_revenue_code = nubc_revenue_code_match.groups()[0]
                            matched = True
                    if not matched:
                        procedure_description = rev_code
            except KeyError:
                pass


            # Ignore this field - it's
            # ERX for NDC
            # SUP for Supplies will have an NUBC Rev Code
            # .. etc
            try:
                filtered_row.pop("CODE TYPE")
            except KeyError:
                pass

            # Almost always garbage - what does an integer here even mean?!
            try:
                description = filtered_row.pop("PROCEDURE DESCRIPTION")
                if description != "1" and procedure_description is None:
                    procedure_description = description

            except KeyError:
                pass


            # Any remaining fields will be insurance fields which have keys that are compound by semicolon
            # TODO: These are grouped by "payer" but payer isn't specified directly. I guess it can usually
            # be guessed by the common suffix though
            for insurance_provders, value in filtered_row.items():
                for insurance_provder in insurance_provders.split(';'):
                    plan = insurance_provder.strip()
                    try:
                        expected_reimbursement = float(value)
                    except (ValueError, TypeError):
                        continue

                    yield ChargeMasterEntry(
                        location = location,
                        procedure_identifier = procedure_identifier,
                        procedure_description = procedure_description,
                        ndc_code = ndc_code,
                        nubc_revenue_code = nubc_revenue_code,
                        cpt_code = cpt_code,
                        hcpcs_code = hcpcs_code,
                        ms_drg_code = ms_drg_code,
                        max_reimbursement = max_reimbursement,
                        min_reimbursement = min_reimbursement,
                        expected_reimbursement = expected_reimbursement,
                        in_patient = in_patient,
                        payer = payer,
                        plan = plan,
                        gross_charge = gross_charge,
                        quantity = quantity
                    )