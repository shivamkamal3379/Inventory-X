from src.services.base import CRUDBase
from src.models.transactions import RentOutTxn, ReturnTxn
from src.schemas.transactions import (
    RentOutTxnCreate,
    RentOutTxnBase,
    ReturnTxnCreate,
    ReturnTxnBase,
)


class CRUDRentOutTxn(CRUDBase[RentOutTxn, RentOutTxnCreate, RentOutTxnBase]):
    pass


class CRUDReturnTxn(CRUDBase[ReturnTxn, ReturnTxnCreate, ReturnTxnBase]):
    pass


rentout_service = CRUDRentOutTxn(RentOutTxn)
return_service = CRUDReturnTxn(ReturnTxn)
