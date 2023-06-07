import re
import openpyxl

from .parsers import ChargeMasterEntry


class SharpChargeMasterParser:
    INSTITUTION_NAME = "Sharp"

    _LOCATION_FORMAL_NAMES = {
        "grossmont": "Grossmont",
        "chula-vista": "Chula Vista",
        "coronado": "Coronado",
        "memorial": "Memorial", 
    }

    # Sharp kinda sucks - they only give gross/average charges and they spread out
    # their charge masters across a bazillion files with only somewhat deterministic
    # names. So, we just brute forced this list of URL's

    @property
    def institution_name(self):
        return SharpChargeMasterParser.INSTITUTION_NAME

    @property
    def artifact_urls(self):
        return [
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3011.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3012.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3016.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3030.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3031.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3033.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3082.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3084.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3085.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3086.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3089.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3140.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3150.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3156.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3157.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3158.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3162.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3163.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3171.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3172.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3181.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3200.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3201.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3205.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3342.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH3360.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4011.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4012.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4014.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4016.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4018.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4019.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4021.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4029.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4035.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4041.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4052.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4058.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4062.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4063.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4065.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4066.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4070.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4073.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4091.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4102.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4112.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4113.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4116.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4130.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4140.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4142.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4143.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4144.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4152.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4160.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4162.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4171.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4175.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4176.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4178.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4179.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4180.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4181.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4185.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4190.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4200.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4201.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4210.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4211.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4221.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4231.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4234.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4238.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4260.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4273.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4290.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4332.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4349.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4411.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4417.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4418.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4420.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4421.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4424.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4425.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4440.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4442.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4443.xlsx",
            "https://www.sharp.com/chargemaster/grossmont/upload/SGH4801.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3010.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3011.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3012.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3030.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3031.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3032.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3086.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3156.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3157.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3158.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3161.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3165.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3171.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3172.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3200.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV3210.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4011.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4012.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4014.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4016.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4018.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4019.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4021.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4029.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4035.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4041.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4052.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4058.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4062.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4063.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4065.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4066.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4070.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4073.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4091.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4102.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4112.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4113.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4116.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4130.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4142.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4143.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4144.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4152.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4160.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4162.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4171.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4175.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4176.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4180.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4190.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4200.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4201.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4211.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4212.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4215.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4221.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4231.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4332.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4417.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4421.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4425.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4440.xlsx",
            "https://www.sharp.com/chargemaster/chula-vista/upload/SCV4801.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO3011.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO3083.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO3202.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO3206.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO3207.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4021.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4029.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4041.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4052.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4058.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4062.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4063.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4065.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4066.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4070.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4073.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4076.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4091.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4102.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4112.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4113.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4130.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4142.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4143.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4144.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4165.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4171.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4175.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4176.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4180.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4190.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4201.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4211.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4221.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4231.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4273.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4332.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4421.xlsx",
            "https://www.sharp.com/chargemaster/coronado/upload/SCO4425.xlsx",
            "https://www.sharp.com/chargemaster/memorial/upload/SMH3011.xlsx",
            "https://www.sharp.com/chargemaster/memorial/upload/SMH3012.xlsx",
            "https://www.sharp.com/chargemaster/memorial/upload/SMH3015.xlsx",
            "https://www.sharp.com/chargemaster/memorial/upload/SMH3030.xlsx",
            "https://www.sharp.com/chargemaster/memorial/upload/SMH3031.xlsx",
            "https://www.sharp.com/chargemaster/memorial/upload/SMH3033.xlsx",
            "https://www.sharp.com/chargemaster/memorial/upload/SMH3082.xlsx",
        ]

    ARTIFACT_URL_LOCATION_REGEX = re.compile(r".+?chargemaster/(.+?)/upload.+?")

    @staticmethod
    def find_artifacts():
        options = [
            ("grossmont", "SGH"),
            ("chula-vista", "SCV"),
            ("coronado", "SCO"),
            ("memorial", "SMH"),
        ]

        import requests
        import time
        for center, abbr in options:
            for i in range(3000, 5000):
                url = f"https://www.sharp.com/chargemaster/{center}/upload/{abbr}{i}.xlsx"
                request = requests.get(url)
                time.sleep(1)
                try:
                    request.raise_for_status()
                    print(url)
                except requests.HTTPError:
                    pass

    def parse_artifacts(self, artifacts):
        for artifact_url, artifact in artifacts.items():
            if artifact_url in self.artifact_urls:
                matcher = self.ARTIFACT_URL_LOCATION_REGEX.match(artifact_url)
                if matcher:
                    location = self._LOCATION_FORMAL_NAMES[matcher.groups()[0]]
                    wb = openpyxl.load_workbook(artifact)
                    charge_code_column, charge_code_description_column, charge_column = None, None, None
                    for i, row in enumerate(wb.worksheets[0].iter_rows()):
                        values = []
                        for cell in row[:3]:
                            if type(cell.value) in (int, float):
                                values.append(cell.value)
                            elif cell.value:
                                values.append(cell.value.strip())
                            else:
                                values.append(None)

                        if (charge_code_column, charge_code_description_column, charge_column) == (None, None, None):
                            if ["ChargeCode","ChargeCode Description", "Charge"] == values:
                                charge_code_column, charge_code_description_column, charge_column = 0, 1, 2
                        else:
                            charge_code = row[charge_code_column].value
                            charge_code_description = row[charge_code_description_column].value
                            charge = row[charge_column].value
                            if charge_code:
                                try:
                                    charge = float(charge.replace('$', '').replace(',',''))
                                    yield ChargeMasterEntry(
                                        location = location,
                                        procedure_identifier = charge_code,
                                        procedure_description = charge_code_description,
                                        gross_charge = charge)
                                except ValueError:
                                    pass