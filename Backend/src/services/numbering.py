"""Human-facing invoice numbers.

Derived from the contract's own primary key rather than a separate counter, so
there is no second sequence to fall out of step and no race between two
concurrent rentals picking the same number.
"""

INVOICE_PREFIX = "INV"


def format_contract_no(contract_id: int) -> str:
    return f"{INVOICE_PREFIX}-{contract_id:06d}"
