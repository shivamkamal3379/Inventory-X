# RentalPro / Inventory X

## Project Overview

**RentalPro (Inventory X)** is a comprehensive full-stack application designed to manage rental inventory, track stock availability, and handle customer transactions efficiently.

Ideally suited for rental businesses, it provides functionalities for:

- Managing Rental Agents
- Inventory Item Tracking (with Stock Management)
- Customer/Party Registration
- Processing Rentals (Rent Out) & Returns

## Technology Stack

### Backend

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: SQL Database (SQLite for development, MySQL ready) via [SQLAlchemy](https://www.sqlalchemy.org/)
- **Validation**: [Pydantic](https://docs.pydantic.dev/)

### Frontend

- **Framework**: [React](https://react.dev/) via [Vite](https://vitejs.dev/)
- **Styling**: (Check Frontend directory for specific styling libraries)

---

## Features

- **Agent Management**: Register and manage agents who facilitate rentals.
- **Inventory Control**:
  - Add new items with rental rates.
  - Track total vs. available stock quantities. (In Progress)
- **Customer Database**: Maintain records of parties (customers) renting equipment.
- **Transaction Processing**:
  - **Rent Out**: Assign items to customers, linked to agents.
  - **Returns**: Process returned items and update inventory status.

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js & npm

### Backend Setup

1.  Navigate to the `Backend` directory:
    ```bash
    cd Backend
    ```
2.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure Environment Variables:
    - Create a `.env` file in the `Backend` root.
    - Add your database URL (Example for SQLite):
      ```env
      DATABASE_URL=sqlite:///./inventory.db
      ```
5.  Run the server:
    ```bash
    uvicorn src.main:app --reload
    ```
    The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
    Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Frontend Setup

1.  Navigate to the `Frontend` directory:
    ```bash
    cd Frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    The application will typically run at [http://localhost:5173](http://localhost:5173) (check terminal output).

---

## API Documentation

### 1. Agents

**Endpoint**: `/agents/`
**Method**: `POST`
**Description**: Create a new rental agent.

**Request Body (JSON):**

```json
{
  "AgentName": "John Doe",
  "mobile": "9876543210",
  "aadhar": "1234-5678-9012", // Optional
  "email": "john@example.com" // Optional
}
```

---

### 2. Items (Inventory)

**Endpoint**: `/items/`
**Method**: `POST`
**Description**: Create a new inventory item. This automatically initializes stock for the item.

**Request Body (JSON):**

```json
{
  "name": "Heavy Duty Drill",
  "description": "Cordless power drill", // Optional
  "qty": 10,
  "rent": 500.0, // Daily rent amount
  "rentFrequency": "daily", // Optional
  "size": "Medium", // Optional
  "weight": "2kg", // Optional
  "materialType": "Steel" // Optional
}
```

**Endpoint**: `/items/{item_id}/stock`
**Method**: `GET`
**Description**: Check available stock for an item.

**Response:**

```json
{
  "itemId": 1,
  "qty": 10,
  "RentedOutQty": 0,
  "availableQty": 10
}
```

---

### 3. Parties (Customers)

**Endpoint**: `/parties/`
**Method**: `POST`
**Description**: Register a new customer/party.

**Request Body (JSON):**

```json
{
  "id": "CUST001", // Custom ID string
  "name": "Jane Smith",
  "mobile": "9123456780",
  "aadhaar": "9876-5432-1098", // Optional
  "address": "123 Main St", // Optional
  "email": "jane@example.com" // Optional
}
```

---

### 4. Rent (Transactions)

**Endpoint**: `/rent/`
**Method**: `POST`
**Description**: Create a rental transaction.

**Request Body (JSON):**

```json
{
  "partyId": "CUST001",
  "agentId": 1, // Optional
  "itemQty": 2,
  "Item": "Heavy Duty Drill", // Optional name
  "contractId": 101 // Optional
}
```

---

### 5. Returns (Transactions)

**Endpoint**: `/returns/`
**Method**: `POST`
**Description**: Create a return transaction.

**Request Body (JSON):**

```json
{
  "partyId": "CUST001",
  "itemQty": 2,
  "Item": "Heavy Duty Drill", // Optional
  "agentId": 1 // Optional
}
```
