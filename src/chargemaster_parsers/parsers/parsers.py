class ChargeMasterParser:
    registered_parsers = {}

    # Register imported derived classes - requires Python 3.6+
    # https://python.readthedocs.io/en/stable/reference/datamodel.html#object.__init_subclass__
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registered_parsers[cls.institution_name.strip()] = cls

    # Requries Python 3.9+ to nest classmethod and property
    # https://docs.python.org/3.11/library/functions.html#classmethod
    @classmethod
    @property
    def institution_name(cls):
        return cls.INSTITUTION_NAME

    @classmethod
    @property
    def artifact_urls(cls):
        return cls.ARTIFACT_URLS

    def parse_artifacts(self, artifacts):
        raise NotImplemented("Only implemented on derived classes.")

    @classmethod
    def build(cls, institution):
        for candidate_institution in cls.registered_parsers:
            if candidate_institution.lower() == institution.lower():
                return cls.registered_parsers[candidate_institution]()
        raise ValueError(
            f"No registered institution matched {institution}. Choices were {', '.join(cls.registered_parsers)}"
        )

    # Helpers
    def parse_price(self, price):
        if price is None:
            return None
        elif type(price) is str:
            try:
                price = price.strip()
                if price[0] == "$":
                    price = price[1:]
                return float(price.replace(",", ""))
            except ValueError:
                return None
        else:
            return float(price)


class ChargeMasterEntry:
    __slots__ = sorted(
      [
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
        "extra_data",
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
                    values.append((key, f'"{value}"'))
                else:
                    values.append((key, value))
        params = ", ".join([f"{key}={value}" for key, value in values])
        return f"ChargeMasterEntry({params})"
