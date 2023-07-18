from chargemaster_parsers.parsers import ChargeMasterEntry, ChargeMasterParser

from chargemaster_parsers.parsers import RadyChargeMasterParser

import pytest


def test_inequality_by_value():
    a = ChargeMasterEntry(
        procedure_description="ROOM & BOARD-CCU",
        in_patient=True,
        payer="COMMERCIAL",
        plan="KAISER FOUNDATION HEALTH PLAN, INC.",
        gross_charge=11834.0,
        location="San Diego",
    )
    b = ChargeMasterEntry(
        procedure_description="ROOM & BOARD-CCU",
        in_patient=False,
        payer="COMMERCIAL",
        plan="KAISER FOUNDATION HEALTH PLAN, INC.",
        gross_charge=11834.0,
        location="San Diego",
    )

    assert a != b
    assert b < a


def test_inequality_by_key():
    a = ChargeMasterEntry(
        payer="COMMERCIAL",
        plan="KAISER FOUNDATION HEALTH PLAN, INC.",
        gross_charge=11834.0,
        location="San Diego",
    )
    b = ChargeMasterEntry(
        procedure_description="ROOM & BOARD-CCU",
        payer="COMMERCIAL",
        plan="KAISER FOUNDATION HEALTH PLAN, INC.",
        gross_charge=11834.0,
        location="San Diego",
    )

    assert a != b
    assert a < b


def test_equality():
    a = ChargeMasterEntry(
        payer="COMMERCIAL",
        plan="KAISER FOUNDATION HEALTH PLAN, INC.",
        gross_charge=11834.0,
        location="San Diego",
    )

    b = ChargeMasterEntry(
        payer="COMMERCIAL",
        plan="KAISER FOUNDATION HEALTH PLAN, INC.",
        gross_charge=11834.0,
        location="San Diego",
    )

    assert a == b
    assert not a < b


def test_repr():
    a = ChargeMasterEntry(
        payer="COMMERCIAL",
        plan="KAISER FOUNDATION HEALTH PLAN, INC.",
        gross_charge=11834.0,
        location="San Diego",
    )
    assert (
        repr(a)
        == 'ChargeMasterEntry(gross_charge=11834.0, location="San Diego", payer="COMMERCIAL", plan="KAISER FOUNDATION HEALTH PLAN, INC.")'
    )


def test_rady():
    assert isinstance(ChargeMasterParser.build("rady"), RadyChargeMasterParser)


def test_invalid():
    with pytest.raises(
        ValueError, match=r"No registered institution matched fake. Choices were.*"
    ):
        ChargeMasterParser.build("fake")


def test_parse_price():
    sut = ChargeMasterParser()
    assert sut.parse_price("NA") == None
    assert sut.parse_price("$1234.45 ") == 1234.45
    assert sut.parse_price(None) == None
    assert sut.parse_price(1) == 1.0
    assert sut.parse_price(" 1,234.5 ") == 1234.5
    assert sut.parse_price(" $1,234") == 1234
