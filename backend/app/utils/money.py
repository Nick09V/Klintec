from decimal import Decimal, ROUND_HALF_UP
from typing import Union

TWOPLACES = Decimal('0.01')

def to_decimal(v: Union[str, int, float, Decimal]) -> Decimal:
    if isinstance(v, Decimal):
        return v.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    return Decimal(str(v)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def to_money(v: Union[str, int, float, Decimal]) -> str:
    return f"{to_decimal(v):.2f}"