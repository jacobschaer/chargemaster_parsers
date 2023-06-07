class ChargeMasterParser:
    def __new__(cls, institution):
        from .ucsd import UCSDChargeMasterParser
        from .scripps import ScrippsChargeMasterParser
        from .rady import RadyChargeMasterParser
        from .kaiser import KaiserChargeMasterParser
        from .sharp import SharpChargeMasterParser
        from .cedars_sinai import CedarsSinaiChargeMasterParser

        PARSERS = [UCSDChargeMasterParser, ScrippsChargeMasterParser, RadyChargeMasterParser, KaiserChargeMasterParser, SharpChargeMasterParser, CedarsSinaiChargeMasterParser]

        for parser_class in PARSERS:
            if institution.lower().strip() == parser_class.INSTITUTION_NAME.lower().strip():
                obj = super().__new__(cls)
                return parser_class()

class ChargeMasterEntry:
    __slots__ = sorted([
        "location",
        "procedure_identifier",
        "procedure_description",
        "ndc_code",
        "nubc_revenue_code",
        "cpt_code",
        "hcpcs_code",
        "ms_drg_code",
        "max_reimbursement",
        "min_reimbursement",
        "expected_reimbursement",
        "in_patient",
        "payer",
        "plan",
        "gross_charge",

        # Unused
        "charge_code",
        "quantity",
        "in_patient_price"
    ])

    def __init__(self, **kwargs):
        for key in self.__slots__:
            value = None
            try:
                value = kwargs.pop(key)
            except KeyError:
                pass
            setattr(self, key, value)

    def __eq__(self, other):
        return all(map(lambda x: getattr(self, x) == getattr(other, x), self.__slots__))

    def __str__(self):
        return "\n".join([f"{key} : {getattr(self, key)}" for key in self.__slots__])

    def __lt__(self, other):
        for key in self.__slots__:
            left = getattr(self, key)
            right = getattr(other, key)
            if left == right:
                continue
            elif left is not None and right is not None:
                return left < right
            elif left is None and right is not None:
                return True
            else:
                return False

    def __repr__(self):
        values = []
        for key in self.__slots__:
            value = getattr(self, key)
            if value is not None:
                if isinstance(value, str):
                    values.append((key,f"\"{value}\""))
                else:
                    values.append((key,value))
        params = ", ".join([f"{key}={value}" for key, value in values])
        return f"ChargeMasterEntry({params})"