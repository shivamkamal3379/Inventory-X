# 🚀 Build the RentalPro Backend from Scratch — Fresher Developer Guide

> **Who is this for?** A developer who has never built a FastAPI backend. Follow each step in order. Don't skip ahead — each step depends on the previous one.

---

## 📋 What You'll Build

A **Rental Inventory Management API** with:

- User registration & JWT login
- CRUD for Agents, Parties (customers), Items
- Rent-out & Return transactions with automatic stock tracking
- Dashboard analytics

**Tech Stack:** Python 3.10+ · FastAPI · SQLAlchemy · SQLite · Pydantic · JWT

---

## Step 0 — Project Setup

**Create the folder structure first. Don't write any code yet.**

```
RentalPro/
└── Backend/
    ├── .env                    ← secret config (Step 1)
    ├── requirements.txt        ← dependencies (Step 0)
    └── src/
        ├── __init__.py         ← empty file (makes src a package)
        ├── main.py             ← app entry point (Step 10 — LAST)
        ├── core/
        │   ├── __init__.py
        │   ├── config.py       ← Step 1
        │   ├── database.py     ← Step 2
        │   └── security.py     ← Step 7
        ├── models/
        │   ├── __init__.py
        │   ├── auth.py         ← Step 3a
        │   ├── people.py       ← Step 3b
        │   ├── inventory.py    ← Step 3c
        │   └── transactions.py ← Step 3d
        ├── schemas/
        │   ├── __init__.py
        │   ├── auth.py         ← Step 4a
        │   ├── people.py       ← Step 4b
        │   ├── inventory.py    ← Step 4c
        │   └── transactions.py ← Step 4d
        ├── services/
        │   ├── __init__.py
        │   ├── base.py         ← Step 5
        │   ├── people.py       ← Step 6a
        │   ├── inventory.py    ← Step 6b
        │   └── transactions.py ← Step 6c
        └── routers/
            ├── __init__.py
            ├── auth.py         ← Step 8a
            ├── agents.py       ← Step 8b
            ├── items.py        ← Step 8c
            ├── parties.py      ← Step 8d
            ├── prices.py       ← Step 8e
            ├── rent.py         ← Step 8f
            ├── returns.py      ← Step 8g
            └── dashboard.py    ← Step 9
```

**Install dependencies:**

```bash
pip install fastapi uvicorn sqlalchemy python-dotenv pydantic python-jose[cryptography] passlib[bcrypt] python-multipart bcrypt
```

> [!TIP]
> Save these to `requirements.txt` with `pip freeze > requirements.txt` so anyone can reinstall with `pip install -r requirements.txt`.

---

## Step 1 — Config (`src/core/config.py`)

**WHY FIRST?** Every file will need the database URL and secret key. Build this before anything else.

```python
import os
from dotenv import load_dotenv

load_dotenv()   # reads the .env file and puts values into os.environ


class Settings:
    # Where is the database? Default: SQLite file in current folder
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")

    # Used to sign JWT tokens — CHANGE THIS in production!
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-change-me-in-production")

    # JWT algorithm
    ALGORITHM: str = "HS256"

    # How long a login token stays valid (minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )


settings = Settings()   # one global instance everyone imports
```

**Also create `.env`:**

```
DATABASE_URL=sqlite:///./inventory.db
SECRET_KEY=my-dev-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> [!IMPORTANT]
> **What to understand:** `load_dotenv()` reads `.env` → `os.getenv()` pulls values → `settings` object becomes the single source of truth for the entire app.

---

## Step 2 — Database Connection (`src/core/database.py`)

**WHY NEXT?** This creates the database engine. Every model you write next will inherit from `Base` defined here.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Engine = the connection to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}   # needed for SQLite only
    if "sqlite" in SQLALCHEMY_DATABASE_URL
    else {},
)

# SessionLocal = a factory that creates new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = every model class will inherit from this
Base = declarative_base()


def get_db():
    """FastAPI dependency: opens a DB session, gives it to the route, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

> [!IMPORTANT]
> **What to understand:**
>
> - `engine` = the actual connection to SQLite
> - `SessionLocal()` = creates a fresh "conversation" with the DB for each API request
> - `Base` = the parent class for all your table definitions
> - `get_db()` = FastAPI will call this automatically via `Depends(get_db)` to inject a DB session into your routes

**✅ Checkpoint:** You can't test yet, but `config.py` → `database.py` is your complete foundation.

---

## Step 3 — Database Models (Tables)

**WHY NEXT?** Before you can validate data (schemas) or write logic (services), you need to define what your database tables look like.

> [!NOTE]
> Each model class = one database table. Each `Column()` = one column in that table.

### Step 3a — User Model (`src/models/auth.py`)

```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)   # NEVER store plain text!
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())       # auto-timestamp
```

### Step 3b — Agent & Party Models (`src/models/people.py`)

```python
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base
import enum


class Agent(Base):
    __tablename__ = "t_Agents"

    agentId = Column(Integer, primary_key=True, autoincrement=True)
    AgentName = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=False)
    aadhar = Column(String(20))
    email = Column(String(100))

    parties = relationship("Party", back_populates="agent")
    #         ↑ tells SQLAlchemy: "I have many Parties linked to me"


class PartyStatus(str, enum.Enum):
    """A Party can be in one of these states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAYMENT_DUE = "payment_due"
    DEFAULT = "default"
    CLOSED = "closed"


class Party(Base):
    __tablename__ = "t_party"

    id = Column(String(50), primary_key=True)   # party ID is a string (e.g. "P001")
    name = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=False)
    aadhaar = Column(String(20))
    secondaryMobile = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    agentId = Column(Integer, ForeignKey("t_Agents.agentId"))  # FK → Agent table
    agentName = Column(String(100))
    siteAddress = Column(String(255))
    status = Column(Enum(PartyStatus), default=PartyStatus.ACTIVE)
    balance = Column(Float, default=0.0)        # how much the party owes
    activeItems = Column(Integer, default=0)    # how many items currently rented
    dateCreated = Column(DateTime, default=func.now())

    agent = relationship("Agent", back_populates="parties")
    #       ↑ tells SQLAlchemy: "My agentId points to this Agent"
```

### Step 3c — Inventory Models (`src/models/inventory.py`)

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class Item(Base):
    __tablename__ = "t_Item"

    itemId = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    qty = Column(Integer, default=0)            # master quantity
    created_at = Column(DateTime, default=func.now())
    size = Column(String(50))
    weight = Column(String(50))
    ManufactureYr = Column(DateTime)
    materialType = Column(String(50))
    model = Column(String(100))
    additionalParam1 = Column(String(255))

    # 1:1 relationships — each item has exactly one stock record and one price
    stock = relationship("AvailableStock", back_populates="item", uselist=False)
    price = relationship("RentalPrice", back_populates="item", uselist=False)


class AvailableStock(Base):
    """Tracks how many of an item are available vs rented out."""
    __tablename__ = "t_AvaiableStock"

    itemId = Column(Integer, ForeignKey("t_Item.itemId"), primary_key=True)
    qty = Column(Integer)                   # total quantity (mirrors Item.qty)
    RentedOutQty = Column(Integer, default=0)
    availableQty = Column(Integer, default=0)

    item = relationship("Item", back_populates="stock")


class RentalPrice(Base):
    """What's the rental rate for an item?"""
    __tablename__ = "RentalPrice"

    itemId = Column(Integer, ForeignKey("t_Item.itemId"), primary_key=True)
    itemName = Column(String(100))
    rent = Column(Float, nullable=False)        # e.g. 500.0
    rentFrequency = Column(String(50))          # e.g. "daily", "monthly"

    item = relationship("Item", back_populates="price")
```

### Step 3d — Transaction Models (`src/models/transactions.py`)

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class RentOutTxn(Base):
    """When someone rents items FROM us."""
    __tablename__ = "rentoutTxn"

    id = Column(Integer, primary_key=True, autoincrement=True)
    partyId = Column(String(50), ForeignKey("t_party.id"))
    contractId = Column(Integer)
    PartyName = Column(String(100))
    agentId = Column(Integer, ForeignKey("t_Agents.agentId"))
    AgentName = Column(String(100))
    itemId = Column(Integer, ForeignKey("t_Item.itemId"))
    Item = Column(String(100))
    itemQty = Column(Integer)
    rentAmount = Column(Float, default=0.0)
    paidAmount = Column(Float, default=0.0)
    TxnDate = Column(DateTime, default=func.now())

    party = relationship("src.models.people.Party")
    agent = relationship("src.models.people.Agent")


class ReturnTxn(Base):
    """When someone returns items TO us."""
    __tablename__ = "returnTxn"

    id = Column(Integer, primary_key=True, autoincrement=True)
    partyId = Column(String(50), ForeignKey("t_party.id"))
    contractId = Column(Integer)
    PartyName = Column(String(100))
    agentId = Column(Integer, ForeignKey("t_Agents.agentId"))
    AgentName = Column(String(100))
    itemId = Column(Integer, ForeignKey("t_Item.itemId"))
    Item = Column(String(100))
    itemQty = Column(Integer)
    refundAmount = Column(Float, default=0.0)
    TxnDate = Column(DateTime, default=func.now())

    party = relationship("src.models.people.Party")
    agent = relationship("src.models.people.Agent")
```

> [!IMPORTANT]
> **What to understand:**
>
> - `relationship()` doesn't create a column — it creates a Python shortcut (e.g. `party.agent` gives you the Agent object)
> - `ForeignKey("table.column")` creates an actual database link between tables
> - `func.now()` auto-fills the current timestamp when a new row is created

**✅ Checkpoint:** You now have 7 database tables defined. Still can't run anything — that's okay.

---

## Step 4 — Schemas (Input/Output Validation)

**WHY NEXT?** Your API needs to know: "What data does the client send me?" and "What data do I send back?" Pydantic schemas enforce this.

> [!NOTE]
> **Pattern for every entity:**
>
> - `Base` = the common fields
> - `Create(Base)` = what the client sends to create a new record
> - `Update(Base)` = same but all fields optional (partial updates)
> - `Out(Base)` = what you return, includes `id` and `Config.from_attributes = True`

### Step 4a — Auth Schemas (`src/schemas/auth.py`)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str       # plain text from client — we'll hash it in the router


class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # allows Pydantic to read SQLAlchemy model objects


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### Step 4b — People Schemas (`src/schemas/people.py`)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.models.people import PartyStatus


class AgentBase(BaseModel):
    AgentName: str
    mobile: str
    aadhar: Optional[str] = None
    email: Optional[str] = None

class AgentCreate(AgentBase):       # for POST — same fields as Base
    pass

class AgentUpdate(AgentBase):       # for PUT — everything optional
    AgentName: Optional[str] = None
    mobile: Optional[str] = None

class AgentOut(AgentBase):          # for response — adds the ID
    agentId: int
    class Config:
        from_attributes = True


class PartyBase(BaseModel):
    name: str
    mobile: str
    aadhaar: Optional[str] = None
    secondaryMobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    agentId: Optional[int] = None
    agentName: Optional[str] = None
    siteAddress: Optional[str] = None
    status: PartyStatus = PartyStatus.ACTIVE
    balance: Optional[float] = 0.0
    activeItems: Optional[int] = 0

class PartyCreate(PartyBase):
    id: str                         # party ID is user-provided (e.g. "P001")

class PartyUpdate(PartyBase):
    name: Optional[str] = None
    mobile: Optional[str] = None
    id: Optional[str] = None

class PartyOut(PartyBase):
    id: str
    dateCreated: datetime
    class Config:
        from_attributes = True
```

### Step 4c — Inventory Schemas (`src/schemas/inventory.py`)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    qty: int = 0
    size: Optional[str] = None
    weight: Optional[str] = None
    ManufactureYr: Optional[datetime] = None
    materialType: Optional[str] = None
    model: Optional[str] = None
    additionalParam1: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None

class ItemOut(ItemBase):
    itemId: int
    created_at: datetime
    class Config:
        from_attributes = True


class AvailableStockBase(BaseModel):
    qty: Optional[int] = 0
    RentedOutQty: Optional[int] = 0
    availableQty: Optional[int] = 0

class AvailableStockOut(AvailableStockBase):
    itemId: int
    class Config:
        from_attributes = True


class RentalPriceBase(BaseModel):
    itemName: Optional[str] = None
    rent: float
    rentFrequency: Optional[str] = None

class RentalPriceCreate(RentalPriceBase):
    itemId: int

class RentalPriceOut(RentalPriceBase):
    itemId: int
    class Config:
        from_attributes = True
```

### Step 4d — Transaction Schemas (`src/schemas/transactions.py`)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RentOutTxnBase(BaseModel):
    partyId: str
    itemId: int
    contractId: Optional[int] = None
    PartyName: Optional[str] = None
    agentId: Optional[int] = None
    AgentName: Optional[str] = None
    Item: Optional[str] = None
    itemQty: int
    rentAmount: Optional[float] = None
    paidAmount: Optional[float] = 0.0

class RentOutTxnCreate(RentOutTxnBase):
    pass

class RentOutTxnOut(RentOutTxnBase):
    id: int
    TxnDate: datetime
    class Config:
        from_attributes = True


class ReturnTxnBase(BaseModel):
    partyId: str
    itemId: int
    contractId: Optional[int] = None
    PartyName: Optional[str] = None
    agentId: Optional[int] = None
    AgentName: Optional[str] = None
    Item: Optional[str] = None
    itemQty: int
    refundAmount: Optional[float] = 0.0

class ReturnTxnCreate(ReturnTxnBase):
    pass

class ReturnTxnOut(ReturnTxnBase):
    id: int
    TxnDate: datetime
    class Config:
        from_attributes = True
```

**✅ Checkpoint:** Models = DB tables. Schemas = API contracts. They look similar but serve different purposes.

---

## Step 5 — Generic CRUD Service (`src/services/base.py`)

**WHY THIS STEP?** Every entity needs Create, Read, Update, Delete. Instead of writing the same code 6 times, write it **once** as a generic class.

```python
from typing import Generic, Type, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session
from src.core.database import Base
from pydantic import BaseModel

# These are "type variables" — think of them as placeholders
ModelType = TypeVar("ModelType", bound=Base)             # any SQLAlchemy model
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  # any Pydantic create schema
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)  # any Pydantic update schema


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Reusable CRUD operations. Any entity service inherits from this.
    Usage: class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentBase]): pass
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model      # e.g. Agent, Item, Party

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get one record by its primary key."""
        return db.query(self.model).get(id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get a paginated list of records."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record from Pydantic schema."""
        obj_data = obj_in.dict()                # convert Pydantic → dict
        db_obj = self.model(**obj_data)          # create SQLAlchemy object
        db.add(db_obj)                           # stage it
        db.commit()                              # save to DB
        db.refresh(db_obj)                       # reload with auto-generated fields (id, etc.)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType | dict) -> ModelType:
        """Update an existing record — only changes fields that were sent."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)   # only fields client actually sent

        for field, value in update_data.items():
            setattr(db_obj, field, value)       # set each field on the DB object

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: Any) -> ModelType:
        """Delete a record by ID."""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
```

> [!IMPORTANT]
> **Why this matters:** After writing this ONE file, creating CRUD for any new entity is just 2 lines:
>
> ```python
> class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentBase]):
>     pass
> ```

---

## Step 6 — Domain Services (Business Logic)

### Step 6a — People Service (`src/services/people.py`)

**Simple — just inherits base CRUD, no custom logic needed.**

```python
from src.services.base import CRUDBase
from src.models.people import Agent, Party
from src.schemas.people import AgentCreate, AgentBase, PartyCreate, PartyBase


class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentBase]):
    pass    # all 5 CRUD methods inherited automatically!


class CRUDParty(CRUDBase[Party, PartyCreate, PartyBase]):
    pass


# Create singleton instances — routers will import these
agent_service = CRUDAgent(Agent)
party_service = CRUDParty(Party)
```

### Step 6b — Inventory Service (`src/services/inventory.py`)

**Custom logic: When you create an Item, automatically create its AvailableStock row.**

```python
from src.services.base import CRUDBase
from src.models.inventory import Item, AvailableStock, RentalPrice
from sqlalchemy.orm import Session
from src.schemas.inventory import ItemCreate, ItemBase, AvailableStockBase, RentalPriceCreate, RentalPriceBase


class CRUDItem(CRUDBase[Item, ItemCreate, ItemBase]):
    def create(self, db: Session, *, obj_in: ItemCreate) -> Item:
        # Step 1: create the item using parent's create
        db_obj = super().create(db, obj_in=obj_in)

        # Step 2: auto-create a stock entry (all qty available, 0 rented)
        stock = AvailableStock(
            itemId=db_obj.itemId,
            qty=db_obj.qty,
            availableQty=db_obj.qty,
            RentedOutQty=0,
        )
        db.add(stock)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDAvailableStock(CRUDBase[AvailableStock, AvailableStockBase, AvailableStockBase]):
    pass


class CRUDRentalPrice(CRUDBase[RentalPrice, RentalPriceCreate, RentalPriceBase]):
    pass


item_service = CRUDItem(Item)
stock_service = CRUDAvailableStock(AvailableStock)
price_service = CRUDRentalPrice(RentalPrice)
```

### Step 6c — Transaction Service (`src/services/transactions.py`)

**This is the MOST COMPLEX file — it has real business logic.**

```python
from typing import List
from sqlalchemy.orm import Session
from src.services.base import CRUDBase
from src.models.transactions import RentOutTxn, ReturnTxn
from src.models.people import Party, PartyStatus
from src.models.inventory import AvailableStock
from src.schemas.transactions import RentOutTxnCreate, RentOutTxnBase, ReturnTxnCreate, ReturnTxnBase
from fastapi import HTTPException


def _recalculate_party_status(party: Party) -> None:
    """
    Business Rule: Automatically determine party status.
    - Has rented items? → ACTIVE
    - No items but owes money? → PAYMENT_DUE
    - No items, no balance? → CLOSED
    - Manually set to DEFAULT? → Don't touch it (manual override)
    """
    if party.status == PartyStatus.DEFAULT:
        return  # manual override — skip

    if (party.activeItems or 0) > 0:
        party.status = PartyStatus.ACTIVE
    elif (party.balance or 0) > 0:
        party.status = PartyStatus.PAYMENT_DUE
    elif party.activeItems == 0 and (party.balance or 0) <= 0:
        party.status = PartyStatus.CLOSED
    else:
        party.status = PartyStatus.INACTIVE


class CRUDRentOutTxn(CRUDBase[RentOutTxn, RentOutTxnCreate, RentOutTxnBase]):
    def create(self, db: Session, *, obj_in: RentOutTxnCreate) -> RentOutTxn:
        #
        # STEP 1: Check stock availability
        #
        stock = db.query(AvailableStock).filter(AvailableStock.itemId == obj_in.itemId).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock info not found for this item")
        if stock.availableQty < obj_in.itemQty:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {stock.availableQty}, Requested: {obj_in.itemQty}",
            )

        #
        # STEP 2: Deduct from available, add to rented
        #
        stock.availableQty -= obj_in.itemQty
        stock.RentedOutQty += obj_in.itemQty
        db.add(stock)

        #
        # STEP 3: Update party balance & status
        #
        party = db.query(Party).filter(Party.id == obj_in.partyId).first()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")

        rent_amount = obj_in.rentAmount or 0.0
        paid_amount = obj_in.paidAmount or 0.0
        party.balance = (party.balance or 0) + rent_amount - paid_amount
        party.activeItems = (party.activeItems or 0) + obj_in.itemQty
        _recalculate_party_status(party)
        db.add(party)

        #
        # STEP 4: Create the transaction record
        #
        return super().create(db, obj_in=obj_in)

    def get_by_party(self, db: Session, *, party_id: str) -> List[RentOutTxn]:
        return db.query(self.model).filter(self.model.partyId == party_id).all()


class CRUDReturnTxn(CRUDBase[ReturnTxn, ReturnTxnCreate, ReturnTxnBase]):
    def create(self, db: Session, *, obj_in: ReturnTxnCreate) -> ReturnTxn:
        # STEP 1: Add back to available stock
        stock = db.query(AvailableStock).filter(AvailableStock.itemId == obj_in.itemId).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock info not found for this item")

        stock.availableQty += obj_in.itemQty
        stock.RentedOutQty = max(0, stock.RentedOutQty - obj_in.itemQty)
        db.add(stock)

        # STEP 2: Update party balance (subtract refund)
        party = db.query(Party).filter(Party.id == obj_in.partyId).first()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")

        refund = obj_in.refundAmount or 0.0
        party.balance = (party.balance or 0) - refund
        party.activeItems = max(0, (party.activeItems or 0) - obj_in.itemQty)
        _recalculate_party_status(party)
        db.add(party)

        # STEP 3: Create the return transaction record
        return super().create(db, obj_in=obj_in)

    def get_by_party(self, db: Session, *, party_id: str) -> List[ReturnTxn]:
        return db.query(self.model).filter(self.model.partyId == party_id).all()


rentout_service = CRUDRentOutTxn(RentOutTxn)
return_service = CRUDReturnTxn(ReturnTxn)
```

> [!CAUTION]
> **Study this file carefully.** This is where "just CRUD" becomes real business logic:
>
> - Renting out → stock goes DOWN, party balance goes UP
> - Returning → stock goes UP, party balance goes DOWN
> - Party status auto-updates based on items & balance

**✅ Checkpoint:** You now have ALL the logic. But no way to call it yet — you need routers (HTTP endpoints).

---

## Step 7 — Security (`src/core/security.py`)

**WHY NOW?** The auth router (next step) needs password hashing and JWT tokens.

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.core.config import settings
from src.core.database import get_db
from src.models.auth import User

# Password hashing setup (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This tells FastAPI: "look for a Bearer token, and the login URL is /auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Turn plain text → hashed password (one-way)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extracts the user from the JWT token.
    Usage in any route: current_user: User = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user
```

---

## Step 8 — Routers (API Endpoints)

**Build in this order:** auth → agents → items → parties → prices → rent → returns

> [!NOTE]
> **Every router follows this pattern:**
>
> 1. Create an `APIRouter(prefix="/...", tags=["..."])`
> 2. Write endpoint functions decorated with `@router.get/post/put/delete`
> 3. Inject `db: Session = Depends(get_db)` into each function
> 4. Call the corresponding service

### Step 8a — Auth Router (`src/routers/auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.security import hash_password, verify_password, create_access_token
from src.models.auth import User
from src.schemas.auth import UserCreate, UserOut, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password),  # hash before storing!
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)
```

### Step 8b — Agents Router (`src/routers/agents.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.people import AgentCreate, AgentOut, AgentUpdate
from src.services.people import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentOut)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    return agent_service.create(db, obj_in=agent)

@router.get("/", response_model=List[AgentOut])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return agent_service.get_multi(db, skip=skip, limit=limit)

@router.get("/{agent_id}", response_model=AgentOut)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_service.update(db, db_obj=agent, obj_in=agent_in)

@router.delete("/{agent_id}", response_model=AgentOut)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_service.remove(db, id=agent_id)
```

> [!TIP]
> **Items Router** (`8c`) and **Parties Router** (`8d`) follow the exact same pattern as Agents. Items adds a bonus `GET /{item_id}/stock` endpoint. Prices Router (`8e`) has `POST`, `GET /`, `GET /{item_id}`.

### Step 8f — Rent Router (`src/routers/rent.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.transactions import RentOutTxnCreate, RentOutTxnOut
from src.services.transactions import rentout_service

router = APIRouter(prefix="/rent", tags=["rent"])

@router.post("/", response_model=RentOutTxnOut)
def create_rent_out(txn: RentOutTxnCreate, db: Session = Depends(get_db)):
    return rentout_service.create(db, obj_in=txn)   # all the stock/balance logic happens in the service!

@router.get("/", response_model=List[RentOutTxnOut])
def read_rent_outs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return rentout_service.get_multi(db, skip=skip, limit=limit)

@router.get("/{txn_id}", response_model=RentOutTxnOut)
def read_rent_out(txn_id: int, db: Session = Depends(get_db)):
    txn = rentout_service.get(db, id=txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Rental transaction not found")
    return txn

@router.get("/party/{party_id}", response_model=List[RentOutTxnOut])
def read_rent_outs_by_party(party_id: str, db: Session = Depends(get_db)):
    return rentout_service.get_by_party(db, party_id=party_id)
```

> **Returns Router** (`8g`) is the same shape — just uses `return_service` and `ReturnTxn` schemas.

---

## Step 9 — Dashboard Router (`src/routers/dashboard.py`)

**WHY LAST among routers?** It reads from ALL tables — it depends on everything existing.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import get_db
from src.models.inventory import Item, AvailableStock
from src.models.people import Party, PartyStatus
from src.models.transactions import RentOutTxn, ReturnTxn
from pydantic import BaseModel


class DashboardStats(BaseModel):
    totalItems: int = 0
    totalParties: int = 0
    activeParties: int = 0
    totalRentedOutQty: int = 0
    totalAvailableQty: int = 0
    totalRentals: int = 0
    totalReturns: int = 0


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return DashboardStats(
        totalItems=db.query(func.count(Item.itemId)).scalar() or 0,
        totalParties=db.query(func.count(Party.id)).scalar() or 0,
        activeParties=db.query(func.count(Party.id)).filter(Party.status == PartyStatus.ACTIVE).scalar() or 0,
        totalRentedOutQty=db.query(func.coalesce(func.sum(AvailableStock.RentedOutQty), 0)).scalar() or 0,
        totalAvailableQty=db.query(func.coalesce(func.sum(AvailableStock.availableQty), 0)).scalar() or 0,
        totalRentals=db.query(func.count(RentOutTxn.id)).scalar() or 0,
        totalReturns=db.query(func.count(ReturnTxn.id)).scalar() or 0,
    )
```

---

## Step 10 — The Entry Point (`src/main.py`)

**THE FINAL FILE — assembles everything.**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import engine, Base
from src.routers import agents, items, parties, rent, returns, prices, dashboard, auth
from src.core.config import settings

# Import all models so SQLAlchemy knows about them when creating tables
from src.models import auth as auth_models, people, inventory, transactions

# Create all database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI(
    title="Inventory X API",
    version="1.0.0",
    description="Backend API for Inventory X / RentalPro",
)

# Allow frontend to talk to backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # in production, list your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(items.router)
app.include_router(parties.router)
app.include_router(rent.router)
app.include_router(returns.router)
app.include_router(prices.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "running", "app": "Inventory X Backend"}
```

---

## 🏃 Run It!

```bash
cd Backend
uvicorn src.main:app --reload
```

Open **http://127.0.0.1:8000/docs** → interactive Swagger UI to test every endpoint.

---

## 📊 Visual Summary: What Depends on What

```
Step 1  config.py           ← reads .env
Step 2  database.py         ← imports config
Step 3  models/*            ← imports database.Base
Step 4  schemas/*           ← imports model enums
Step 5  services/base.py    ← imports database.Base + pydantic
Step 6  services/*          ← imports base + models + schemas
Step 7  core/security.py    ← imports config + database + models/auth
Step 8  routers/*           ← imports services + schemas + database
Step 9  routers/dashboard   ← imports models directly (aggregation queries)
Step 10 main.py             ← imports EVERYTHING, starts the app
```

> [!CAUTION]
> **Golden Rule:** Never import a later step from an earlier step. The dependency arrow always points **downward** in this list. If you break this rule, you'll get circular import errors.
