class ChargeMasterParser:
    def __new__(cls, institution):
        from .ucsd import UCSDChargeMasterParser
        from .scripps import ScrippsChargeMasterParser
        from .rady import RadyChargeMasterParser
        from .kaiser import KaiserChargeMasterParser
        from .sharp import SharpChargeMasterParser

        PARSERS = [UCSDChargeMasterParser, ScrippsChargeMasterParser, RadyChargeMasterParser, KaiserChargeMasterParser, SharpChargeMasterParser]

        for parser_class in PARSERS:
            if institution.lower().strip() == parser_class.INSTITUTION_NAME.lower().strip():
                obj = super().__new__(cls)
                return parser_class()

class ChargeMasterEntry:
    __slots__ = (
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
    )

    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs.get(key, None))

    def __eq__(self, other):
        return self.__dict__() == other.__dict__()

    def __str__(self):
        return "\n".join([f"{key} : {value}" for key, value in self.__dict__().items()])

    def __dict__(self):
        result = {}
        for key in self.__slots__:
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        return result

    def __lt__(self, other):
        self_dict = self.__dict__()
        other_dict = other.__dict__()

        keys = set(self_dict.keys()) & set(other_dict.keys())
        for key in keys:
            a, b = getattr(self, key) , getattr(other, key)
            if a == b:
                continue
            else:
                return a < b
        return self_dict.keys() < other_dict.keys()

    def __repr__(self):
        return str(self.__dict__())