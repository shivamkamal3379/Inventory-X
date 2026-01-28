# Backend API Requirements & Structure

This document outlines the required API endpoints, data models, and user operations derived from the current frontend implementation.

## 1. Authentication Module

### Page: Login Page (`/login`)

User authenticates to access the dashboard.

| Operation        | Method | Endpoint          | Payload                         | Description                                         |
| :--------------- | :----- | :---------------- | :------------------------------ | :-------------------------------------------------- |
| **Login**        | `POST` | `/api/auth/login` | `{ username, password }`        | Authenticates user and returns JWT token.           |
| **Verify Token** | `GET`  | `/api/auth/me`    | `Authorization: Bearer <token>` | Verifies if current session is valid (on app load). |

---

## 2. Dashboard Home Module

### Page: Dashboard Home (`/dashboard`)

Overview of activities and quick actions.

| Operation               | Method | Endpoint                  | Description                                       |
| :---------------------- | :----- | :------------------------ | :------------------------------------------------ |
| **Get Stats**           | `GET`  | `/api/dashboard/stats`    | Returns total sales, recent activity count, etc.  |
| **Get Recent Activity** | `GET`  | `/api/dashboard/activity` | Returns list of recent transactions (limit 5-10). |

---

## 3. Inventory Module

### Page: Inventory (`/dashboard/inventory`)

Manage stock items (Printers, Chairs, etc.).

| Operation       | Method   | Endpoint             | Payload                                  | Description                              |
| :-------------- | :------- | :------------------- | :--------------------------------------- | :--------------------------------------- |
| **List Items**  | `GET`    | `/api/inventory`     | `?search=<term>`                         | Get all items. Support search filtering. |
| **Add Item**    | `POST`   | `/api/inventory`     | `{ name, description, quantity, price }` | Create a new stock item.                 |
| **Update Item** | `PUT`    | `/api/inventory/:id` | `{ name, description, quantity, price }` | Update item details.                     |
| **Delete Item** | `DELETE` | `/api/inventory/:id` | -                                        | Remove an item from stock.               |

**Data Model (Item):**

```json
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "quantity": "integer (current stock)",
  "totalQuantity": "integer (total owned)",
  "price": "number (rental price per unit)"
}
```

---

## 4. Ledger (Party Management) Module

### Page: Ledger (`/dashboard/ledger`)

Manage clients/parties and track their balances.

| Operation             | Method | Endpoint           | Payload                            | Description                                        |
| :-------------------- | :----- | :----------------- | :--------------------------------- | :------------------------------------------------- |
| **List Parties**      | `GET`  | `/api/parties`     | `?search=<term>`                   | Get all parties with current balance and status.   |
| **Add Party**         | `POST` | `/api/parties`     | `{ name, contact, email, status }` | Register a new client.                             |
| **Update Party**      | `PUT`  | `/api/parties/:id` | `{ name, contact, email, status }` | Update client details or manual status override.   |
| **Get Party Details** | `GET`  | `/api/parties/:id` | -                                  | Get full history and details for a specific party. |

**Data Model (Party):**

```json
{
  "id": "uuid",
  "name": "string",
  "contact": "string",
  "email": "string",
  "balance": "number (positive = they owe us)",
  "activeItems": "integer (items currently with them)",
  "status": "enum('active', 'inactive', 'payment_due', 'default')",
  "createdAt": "timestamp"
}
```

---

## 5. Transaction (Billing) Module

### Page: Transactions (`/dashboard/transactions`)

Process Rentals and Returns. This is the core logic engine.

| Operation              | Method | Endpoint            | Payload                                                 | Description                            |
| :--------------------- | :----- | :------------------ | :------------------------------------------------------ | :------------------------------------- |
| **Create Transaction** | `POST` | `/api/transactions` | `{ partyId, items: [{itemId, qty}], type, paidAmount }` | Create a Rental or Return transaction. |
| **List Transactions**  | `GET`  | `/api/transactions` | `?partyId=<id>`                                         | Get transaction history.               |

### Business Logic Requirements (Backend Service)

**1. Rental Transaction (`type: 'RENTAL'`)**

- Create Transaction Record.
- **Inventory Update**: Decrease `quantity` of selected items by transaction `qty`.
- **Party Update**:
  - Increase `balance` by `(Total Value - Paid Amount)`.
  - Increase `activeItems` count.
  - Set Status to `open` or `payment_due`.

**2. Return Transaction (`type: 'RETURN'`)**

- Create Transaction Record.
- **Inventory Update**: Increase `quantity` of returned items.
- **Party Update**:
  - Decrease `balance` by `Paid Amount` (if settling checks/cash) or just log return if paying later? _Current UI assumes 'Settlement Amount' reduces balance._
  - Decrease `activeItems` count.
  - Recalculate Status (e.g., if `activeItems == 0` and `balance == 0` -> `closed`).

**Data Model (Transaction):**

```json
{
  "id": "uuid",
  "partyId": "uuid",
  "type": "enum('RENTAL', 'RETURN')",
  "items": [{ "itemId": "uuid", "qty": "int", "price": "number" }],
  "totalAmount": "number",
  "paidAmount": "number",
  "date": "timestamp"
}
```
