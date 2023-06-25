# chargemaster_parsers
Healthcare Chargemaster Parsers

# Goals
The primary objective for now is to process (where available) the outpatient data from chargemasters for healthcare institutions in California.
The output should be a collection of objects with a common interface to simplify bulk processing.

# Requirements
Python 3.9+

# Running Unit tests
Unit tests are implemented in pytest and are located in the src/tests directory.
To run, you must first create a virtual environment and install the package (preferably in editable mode for local testing).
As an example using the venv module:

  ```bash
  cd src
  python -m venv venv
  venv/scripts/Activate
  pip install -e .
  ```

Next install pytest

  ```bash
  pip install pytest
  ```

Then to run the tests:

  ```bash
  python -m pytest
  ```

# Downloading and parsing
To utilize the library for a particular institution:

  ```python
  from chargemaster_parsers.parsers import ChargeMasterParser

  # Choose your institution
  institution = "scripps"

  # Create a parser for it - either use the factory method and give it an
  # institution name, or you can import the specific parser subclass you want
  #
  # from chargemaster_parsers.parsers import ScrippsChargeMasterParser
  # parser = ScrippsChargeMasterParser()

  parser = ChargeMasterParser.build(institution)

  # Download the artifacts however you see fit - note this way requires a lot of
  # RAM - you will likely need to store them off to disk. For now make a pretend
  # file in memory with io. Note that some institutions may require headers that
  # look like a browser or they will fail.
  import urllib.request
  import io

  artifacts = {}
  for artifact_url in parser.artifact_urls:
      with urllib.request.urlopen(artifact_url) as response:
          artifacts[artifact_url] = io.BytesIO(response.read())

  # Parse the downloaded artifacts into chargemaster entries
  for chargemaster_entry in parser.parse_artifacts(artifacts):
      print(chargemaster_entry)
  ```

# Quick overview of Medical Billing
Medical billing is far too complicated to go into detail here, but at a high level there's two options:

## Self/Cash Payer
In the event that one doesn't have or chooses not to use insurance, the cost of the procedure is simply the cost billed (the gross charge).
Traditionally, most institutions offer a discount of some kind since there's less paperwork.

## Insurance
Most insurance plans group providers into in-network or out-of-network.
In the case of HMO's (Health Maintanence Organizations), they will generally only reimburse for in-network (their own) facilities.
For Preferred Provider Organiztion (PPO) plans, the set of in-network providers tends to be much larger and there is often partial coverage for out-of-network providers.
The theory was that large insurers would negotiate reduced rates at in-network-providers (thus reducing their costs) in exchange for providing a guaranteed stream of patients to said providers.

The amount an insurer will pay a provider is often referred to as the "allowable amount" or "contract rate".
These are typically considered confidential between the provider and the insurer and are not shared with patients even when asked leading to a great deal of frustration.
The insured patient then accounts for their policies rules on co-insurance (cost sharing), co-pay (fixed fee for a class of services), and deductible and ultimately arrives at their final out-of-pocket cost.

The algorithm normally goes like this:

1) Provider bills the insurer their chargemaster gross fee
2) The insurer finds the contract rate and discounts the gross fee accordingly (there are odd situations where the billed amount is less than the contract rate but this is rare)
3) The insurer computes the patients portion based on their deductible, copay, and coinsurance and deducts this from the contract rate
4) The insurer pays the provider their portion
5) The provider bills the patient for the contract rate less the amount the insurance paid


# Fields

* location - Some providers have a different chargemaster per facility
* procedure_identifier - A unique identifer for the chargemaster entry. Typically this isn't useful beyond tracking over time
* procedure_description - The human readable name of the chargemaster etnry, though often riddled with abbreviations and shorthand
* ndc_code - National Drug Code. For medication/medical goods line-items.
* nubc_revenue_code - Some institutions also list a National Uniform Billing Code though it's rare and not super useful
* cpt_code: CPT&copy; (Current Procedural Terminology) Code - A subset of HCPCS codes that these are copyrighted and require licensing for use.
* hcpcs_code: Healthcare Common Procedure Coding System codes. These are provided by the National Institute of Health NIH and, with the exception of the CPT subset, free to use
* ms_drg_code: Medicare Severity Diagnosis Related Groups code. For hospitalizations rather than procedures.
* max_reimbursement: The maximum amount that the insurer(s) reimbursed the provider. Note this is less than or equal to the contract rate where applicable
* min_reimbursement: The minimum amount that the insurer(s) reimbursed the provider.
* expected_reimbursement: Presumably this is average amount that insurer(s) reimbursed the provider but it's not well defined and likely depends on the institution.
* in_patient: True/False if the chargemaster item was specifically for an in-patient procedure/MS-DRG
* payer: The insurance provider name or "Cash" for self payment (or None where the item is an aggregate)
* plan: Where known, the plan name under the payer
* gross_charge: The amount billed. For "Cash" payer, this often accounts for the discount
* charge_code: The providers internal charge code. Useless outside the organization
* quantity: Typically for drug line items
* in_patient_price: UCSD provides this though it's likely going to be deprecated soon

# Prior works to reference:
This is certainly not the first, nor will it be the last attempt at this.
Many have had similar ideas, though most are ultimately doomed to become out of date.

Some that I've found so far:
  * https://github.com/vsoch/hospital-chargemaster