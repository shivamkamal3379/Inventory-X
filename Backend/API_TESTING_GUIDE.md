# Inventory X — API Testing Guide

**Base URL**: `http://127.0.0.1:8000`
**Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Recommended Testing Flow

> Test in this order to verify the full business logic chain:
>
> Register → Login → Create Agent → Create Item → Set Price → Create Party → Rent Out → Verify Stock → Return → Verify Stock Restored → Dashboard

---

## 🔑 1. Auth

### Register

```
POST /auth/register
Content-Type: application/json
```

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Login (returns JWT token)

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

```
username=admin&password=admin123
```

> 💡 Save the `access_token` from the response for protected routes.

---

## 👤 2. Agents

### Create Agent

```
POST /agents/
Content-Type: application/json
```

```json
{
  "AgentName": "Agent Smith",
  "mobile": "9999999999",
  "aadhar": "1234-5678-9012",
  "email": "smith@example.com"
}
```

### List All Agents

```
GET /agents/
```

### Get Agent by ID

```
GET /agents/1
```

### Update Agent

```
PUT /agents/1
Content-Type: application/json
```

```json
{
  "AgentName": "Agent Smith Updated",
  "mobile": "8888888888"
}
```

### Delete Agent

```
DELETE /agents/1
```

---

## 📦 3. Items (Inventory)

### Create Item _(auto-creates stock entry)_

```
POST /items/
Content-Type: application/json
```

```json
{
  "name": "Heavy Duty Drill",
  "description": "Cordless power drill",
  "qty": 10,
  "size": "Medium",
  "weight": "2kg",
  "materialType": "Steel",
  "model": "HD-500"
}
```

### List All Items

```
GET /items/
```

### Get Item by ID

```
GET /items/1
```

### Update Item

```
PUT /items/1
Content-Type: application/json
```

```json
{
  "name": "Heavy Duty Drill v2",
  "description": "Updated model"
}
```

### Delete Item

```
DELETE /items/1
```

### Check Stock for Item

```
GET /items/1/stock
```

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

## 💰 4. Rental Prices

### Create Rental Price

```
POST /prices/
Content-Type: application/json
```

```json
{
  "itemId": 1,
  "itemName": "Heavy Duty Drill",
  "rent": 50.0,
  "rentFrequency": "daily"
}
```

### List All Prices

```
GET /prices/
```

### Get Price by Item ID

```
GET /prices/1
```

---

## 🤝 5. Parties (Customers)

### Create Party

```
POST /parties/
Content-Type: application/json
```

```json
{
  "id": "CUST001",
  "name": "John Doe",
  "mobile": "9876543210",
  "aadhaar": "9876-5432-1098",
  "address": "123 Main St",
  "email": "john@example.com",
  "agentId": 1,
  "siteAddress": "456 Site Ave"
}
```

### List All Parties

```
GET /parties/
```

### Get Party by ID

```
GET /parties/CUST001
Content-Type: application/json
```

```json
{
  "id": "CUST001",
  "name": "John Doe",
  "mobile": "9876543210",
  "aadhaar": "9876-5432-1098",
  "address": "123 Main St",
  "email": "john@example.com",
  "agentId": 1,
  "status" : "active",
  "siteAddress": "456 Site Ave"
}
```
### Update Party

```
PUT /parties/CUST001
Content-Type: application/json
```

```json
{
  "name": "John Doe Updated",
  "mobile": "9876543210"
}
```


---

## 📤 6. Rent Out

### Create Rental _(deducts stock, updates party balance & status)_

```
POST /rent/
Content-Type: application/json
```

```json
{
  "partyId": "CUST001",
  "agentId": 1,
  "contractId": 101,
  "itemId": 1,
  "itemQty": 3,    
}
```

**After this, verify:**

| Endpoint               | Expected Change                                              |
| ---------------------- | ------------------------------------------------------------ |
| `GET /items/1/stock`   | `availableQty` decreases by 3, `RentedOutQty` increases by 3 |
| `GET /parties/CUST001` |  `status` = "active"      |


### Get Rentals by Party

```
GET /rent/party/CUST001
```

---

## 📥 7. Returns

### Create Return _(restocks inventory, updates party balance & status)_

```
POST /returns/
Content-Type: application/json
```

```json
{
  "partyId": "CUST001",
  "agentId": 1,
  "itemId": 1,
  "itemQty": 2,
  "Return Date": timestamp 
}
```

**After this, verify:**

| Endpoint               | Expected Change                                                  |
| ---------------------- | ---------------------------------------------------------------- |
| `GET /items/1/stock`   | `availableQty` increases by 2, `RentedOutQty` decreases by 2     |
| `GET /parties/CUST001` | `status` may change |


### Get Returns by Party

```
GET /returns/party/CUST001
```

---

## 📊 8. Dashboard

### Get Aggregate Stats

```
GET /dashboard/stats
```

**Response:**

```json
{
  "totalItems": 1,
  "totalParties": 1,
  "activeParties": 1,
  "totalRentedOutQty": 1,
  "totalAvailableQty": 9,
  "totalRentals": 1,
  "totalReturns": 1
}
```

---

## 🏥 9. Health Check

```
GET /
```

**Response:**

```json
{
  "status": "running",
  "app": "Inventory X Backend"
}
```

---

## 📝 Notes

- **Swagger UI** at `/docs` lets you click **"Try it out"** on any endpoint and test interactively.
- **Login** uses `application/x-www-form-urlencoded` (OAuth2 standard), not JSON.
- **Party ID** is a custom string (`CUST001`), not auto-generated.
- **Stock** is auto-created when you create an item — no need to create it separately.
- Renting out **deducts** stock and **increases** party balance/activeItems.
- Returning **restocks** inventory and **decreases** party activeItems.
- Party **status** auto-updates: `active` → `payment_due` → `closed` based on balance and active items.
