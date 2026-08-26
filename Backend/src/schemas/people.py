import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.models.people import PartyStatus

MOBILE_RE = re.compile(r"^[0-9+\-\s()]{6,20}$")


def _validate_mobile(v: str | None) -> str | None:
    if v is None:
        return v
    v = v.strip()
    if not MOBILE_RE.match(v):
        raise ValueError("Mobile must be 6-20 characters of digits, +, -, spaces or ()")
    return v


class AgentBase(BaseModel):
    AgentName: str = Field(min_length=1, max_length=100)
    mobile: str = Field(min_length=6, max_length=20)
    aadhar: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None

    _check_mobile = field_validator("mobile")(_validate_mobile)


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    """Every field optional — only what is sent gets written.

    Note there is no created_at here on purpose: the previous AgentUpdate/ItemUpdate
    carried a default_factory timestamp, so every PUT silently overwrote the
    record's creation date.
    """

    AgentName: str | None = Field(default=None, min_length=1, max_length=100)
    mobile: str | None = Field(default=None, min_length=6, max_length=20)
    aadhar: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None

    _check_mobile = field_validator("mobile")(_validate_mobile)


class AgentOut(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    agentId: int
    created_at: datetime | None = None


class PartyBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    mobile: str = Field(min_length=6, max_length=20)
    aadhaar: str | None = Field(default=None, max_length=20)
    secondaryMobile: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=255)
    agentId: int | None = None
    agentName: str | None = Field(default=None, max_length=100)
    siteAddress: str | None = Field(default=None, max_length=255)
    status: PartyStatus = PartyStatus.ACTIVE

    _check_mobile = field_validator("mobile", "secondaryMobile")(_validate_mobile)


class PartyCreate(PartyBase):
    id: str = Field(min_length=1, max_length=50)

    @field_validator("id")
    @classmethod
    def _clean_id(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9_-]+$", v):
            raise ValueError("Party id may contain only letters, digits, _ and -")
        return v


class PartyUpdate(BaseModel):
    """`id` is intentionally absent — it is the primary key and is not rewritable.

    `balance` and `activeItems` are also absent: they are derived from rental and
    return transactions, and letting a PUT set them directly would desynchronise
    them from the ledger.
    """

    name: str | None = Field(default=None, min_length=1, max_length=100)
    mobile: str | None = Field(default=None, min_length=6, max_length=20)
    aadhaar: str | None = Field(default=None, max_length=20)
    secondaryMobile: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=255)
    agentId: int | None = None
    agentName: str | None = Field(default=None, max_length=100)
    siteAddress: str | None = Field(default=None, max_length=255)
    status: PartyStatus | None = None

    _check_mobile = field_validator("mobile", "secondaryMobile")(_validate_mobile)


class PartyOut(PartyBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    balance: float = 0.0
    activeItems: int = 0
    dateCreated: datetime | None = None
