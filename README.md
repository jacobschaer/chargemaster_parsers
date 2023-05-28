# chargemaster_parsers
Healthcare Chargemaster Parsers

# Goals
The primary objective for now is to process (where available) the outpatient data from chargemasters for healthcare institutions in California.
The output should be a collection of objects with a common interface to simplify bulk processing.

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

  # Create a parser for it
  parser = ChargeMasterParser(institution)

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

# Prior works to reference:
This is certainly not the first, nor will it be the last attempt at this.
Many have had similar ideas, though most are ultimately doomed to become out of date.

Some that I've found so far:
  * https://github.com/vsoch/hospital-chargemaster