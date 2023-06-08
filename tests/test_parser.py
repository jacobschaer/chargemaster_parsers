from chargemaster_parsers.parsers import ChargeMasterEntry, ChargeMasterParser

from chargemaster_parsers.parsers import RadyChargeMasterParser

def test_inequality_by_value():
    a = ChargeMasterEntry(
            procedure_description = "ROOM & BOARD-CCU",
            in_patient = True,
            payer = 'COMMERCIAL',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        )
    b = ChargeMasterEntry(
            procedure_description = "ROOM & BOARD-CCU",
            in_patient = False,
            payer = 'COMMERCIAL',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        )

    assert a != b
    assert b < a

def test_inequality_by_key():
    a = ChargeMasterEntry(
            payer = 'COMMERCIAL',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        )
    b = ChargeMasterEntry(
            procedure_description = "ROOM & BOARD-CCU",
            payer = 'COMMERCIAL',
            plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
            gross_charge = 11834.0,
            location="San Diego"
        )

    assert a != b
    assert a < b

def test_equality():
    a = ChargeMasterEntry(
        payer = 'COMMERCIAL',
        plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
        gross_charge = 11834.0,
        location="San Diego"
    )

    b = ChargeMasterEntry(
        payer = 'COMMERCIAL',
        plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
        gross_charge = 11834.0,
        location="San Diego"
    )

    assert a == b
    assert not a < b

def test_repr():
    a = ChargeMasterEntry(
        payer = 'COMMERCIAL',
        plan = 'KAISER FOUNDATION HEALTH PLAN, INC.',
        gross_charge = 11834.0,
        location="San Diego"
    )
    assert repr(a) == 'ChargeMasterEntry(gross_charge=11834.0, location="San Diego", payer="COMMERCIAL", plan="KAISER FOUNDATION HEALTH PLAN, INC.")'

def test_rady():
    assert isinstance(ChargeMasterParser.build("rady"), RadyChargeMasterParser)