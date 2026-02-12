# Backend API Requirements & Structure

This document outlines the implemented API endpoints, data models, and operations.

## 1. Authentication Module

### Page: Login Page (`/login`)

| Operation        | Method | Endpoint      | Payload                         | Description                               |
| :--------------- | :----- | :------------ | :------------------------------ | :---------------------------------------- |
| **Login**        | `POST` | `/auth/login` | `{ username, password }`        | Authenticates user and returns JWT token. |
| **Verify Token** | `GET`  | `/auth/me`    | `Authorization: Bearer <token>` | Verifies session validity.                |

---

## 2. Dashboard Home Module

### Page: Dashboard Home (`/dashboard`)

| Operation               | Method | Endpoint              | Description                                      |
| :---------------------- | :----- | :-------------------- | :----------------------------------------------- |
| **Get Stats**           | `GET`  | `/dashboard/stats`    | Returns total sales, recent activity count, etc. |
| **Get Recent Activity** | `GET`  | `/dashboard/activity` | Returns list of recent transactions.             |

---

## 3. Agents Module

### Page: Agents Management

Manage agents who facilitate rentals.

| Operation        | Method   | Endpoint       | Payload                      | Description                 |
| :--------------- | :------- | :------------- | :--------------------------- | :-------------------------- |
| **List Agents**  | `GET`    | `/agents`      | -                            | Get all agents.             |
| **Create Agent** | `POST`   | `/agents`      | `{ AgentName, mobile, ... }` | Create a new agent.         |
| **Get Agent**    | `GET`    | `/agents/{id}` | -                            | Get specific agent details. |
| **Update Agent** | `PUT`    | `/agents/{id}` | `{ AgentName, mobile, ... }` | Update agent details.       |
| **Delete Agent** | `DELETE` | `/agents/{id}` | -                            | Remove an agent.            |

---

## 4. Inventory Module (Items)

### Page: Inventory (`/dashboard/inventory`)

Manage stock items.

| Operation          | Method   | Endpoint            | Payload              | Description                   |
| :----------------- | :------- | :------------------ | :------------------- | :---------------------------- |
| **List Items**     | `GET`    | `/items`            | `?skip=0&limit=100`  | Get all items.                |
| **Create Item**    | `POST`   | `/items`            | `{ name, qty, ... }` | Create a new stock item.      |
| **Get Item**       | `GET`    | `/items/{id}`       | -                    | Get item details.             |
| **Update Item**    | `PUT`    | `/items/{id}`       | `{ name, qty, ... }` | Update item details.          |
| **Delete Item**    | `DELETE` | `/items/{id}`       | -                    | Remove an item.               |
| **Get Item Stock** | `GET`    | `/items/{id}/stock` | -                    | Get available stock for item. |

---

## 5. Ledger Module (Parties)

### Page: Ledger (`/dashboard/ledger`)

Manage parties/clients.

| Operation        | Method   | Endpoint        | Payload                 | Description           |
| :--------------- | :------- | :-------------- | :---------------------- | :-------------------- |
| **List Parties** | `GET`    | `/parties`      | `?skip=0&limit=100`     | Get all parties.      |
| **Create Party** | `POST`   | `/parties`      | `{ name, mobile, ... }` | Register a new party. |
| **Get Party**    | `GET`    | `/parties/{id}` | -                       | Get party details.    |
| **Update Party** | `PUT`    | `/parties/{id}` | `{ name, mobile, ... }` | Update party details. |
| **Delete Party** | `DELETE` | `/parties/{id}` | -                       | Remove a party.       |

---

## 6. Rent & Returns Module

### Page: Transactions (`/dashboard/transactions`)

Process Rentals and Returns.

| Operation             | Method | Endpoint   | Payload                             | Description                         |
| :-------------------- | :----- | :--------- | :---------------------------------- | :---------------------------------- |
| **Rent Out (Create)** | `POST` | `/rent`    | `{ partyId, itemId, itemQty, ... }` | Rent out an item (Decreases Stock). |
| **List Rents**        | `GET`  | `/rent`    | `?skip=0&limit=100`                 | List rental history.                |
| **Return (Create)**   | `POST` | `/returns` | `{ partyId, itemId, itemQty, ... }` | Return an item (Increases Stock).   |
| **List Returns**      | `GET`  | `/returns` | `?skip=0&limit=100`                 | List return history.                |

### Business Logic

**1. Rent Out**

- **Trigger**: `POST /rent`
- **Logic**:
  - Check `AvailableStock` for `itemId`.
  - If `availableQty` >= `itemQty`:
    - Decrement `availableQty`.
    - Increment `RentedOutQty`.
    - Create `RentOutTxn` record.
  - Else: Return `400 Insufficient Stock`.

**2. Return**

- **Trigger**: `POST /returns`
- **Logic**:
  - Increment `availableQty`.
  - Decrement `RentedOutQty`.
  - Create `ReturnTxn` record.
