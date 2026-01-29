# Project Onboarding: RentalPro (Inventory-X) Theoretical Guide

## 1. Introduction: The Big Picture

**Goal:** We are building a digital system for a rental business (like a camera gear rental shop). They need to track **Item Stock** (what they own), **Parties** (customers), and **Transactions** (who borrowed what and for how much).

### The Architecture (How it works together)

Imagine a restaurant:

1.  **The Customer (User)**: Sits at the table and looks at the menu.
2.  **The Waiter (Frontend)**: Takes the order and brings it to the kitchen.
3.  **The Kitchen (Backend/API)**: Cooks the food (processes data) and checks the pantry (Database).

In **RentalPro**:

- **Frontend (The Waiter)**: What you see on the screen. It doesn't "know" anything permanently; it just displays what it's told and asks for things.
- **Backend (The Kitchen)**: In our theoretical model, this is the API that saves data, calculates bills, and ensures we don't rent out an item we don't have.

---

## 2. Frontend Concepts (The "Waiter")

_Technology Stack: React 19, Vite, Tailwind CSS_

### A. Components (The Lego Bricks)

Instead of writing one giant HTML file, we break the UI into small, reusable **Components**.

- **Example**: A `Button` component is written once. We can use it for "Login", "Save", and "Delete" just by changing its label.
- **In Our Project**:
  - `StatCard`: Used on the Dashboard to show "Total Sales" and "Active Returns". Same code, different data.
  - `Layout`: The sidebar and top bar that stay the same on every page.

### B. Props (Passing Instructions)

How do we tell the `StatCard` to say "Sales" vs "Returns"? We pass **Props** (short for properties).

- **Analogy**: Telling the waiter, "I want the burger _medium-rare_." "Medium-rare" is the prop.
- **Code Concept**: `<StatCard title="Total Sales" amount="$500" />`

### C. State (Short-term Memory)

The Frontend needs to remember things temporarily, like what you are typing in the search bar. This is **State**.

- **Analogy**: The waiter remembering your order while walking to the kitchen. If he trips (refresh the page), he forgets it (unless we save it elsewhere).
- **Hook**: `useState`
  - `const [search, setSearch] = useState('')`
  - Meaning: "Create a memory box called 'search'. Initially, it's empty."

### D. Effects (Doing things when something happens)

Sometimes we need to do something _after_ the page loads, like fetching data.

- **Hook**: `useEffect`
  - "When this component appears on screen, go fetch the Inventory list from the API."

---

## 3. Backend Concepts (The "Kitchen")

_Technology: REST API_

### A. The API (The Menu)

The Frontend can't just touch the Database directly (that's dangerous). It must ask the API politely.
The API has a specific "Menu" of allowed actions, called **Endpoints**.

| Action (Method) | Meaning           | Example for RentalPro                                      |
| :-------------- | :---------------- | :--------------------------------------------------------- |
| **GET**         | "Give me data"    | `GET /api/inventory` (Show me all items)                   |
| **POST**        | "Create new data" | `POST /api/transactions` (Create a new rental)             |
| **PUT**         | "Update data"     | `PUT /api/parties/123` (Update client #123's phone number) |
| **DELETE**      | "Remove data"     | `DELETE /api/inventory/55` (Delete item #55)               |

### B. Authentication (The VIP Wristband)

We don't want strangers seeing our business data.

1.  **Login**: You send `username` & `password`.
2.  **Token (JWT)**: If correct, the Backend gives you a secret text string (Token).
3.  **Access**: For every future request (like "Get Inventory"), the Frontend shows this Token (like a VIP wristband) to get in.

---

## 4. Application Flow Examples

### Scenario 1: The Login Flow

1.  **User** types credentials into `LoginPage.jsx`.
2.  **Frontend** (React) captures typing in `useState`.
3.  **User** clicks "Login".
4.  **Frontend** sends `POST /api/auth/login` to Backend.
5.  **Backend** checks password.
    - _Success_: Returns a Token.
    - _Fail_: Returns an error ("Wrong password").
6.  **Frontend** saves the Token (in LocalStorage - essentially the browser's pocket) and moves the user to the Dashboard.

### Scenario 2: Creating a Rental

1.  **User** goes to `Transactions` page.
2.  **Frontend** uses `useEffect` to `GET /api/inventory` so it knows what items are available.
3.  **User** selects "Canon Camera" and "Client: John Doe".
4.  **User** clicks "Submit".
5.  **Frontend** packages this into a JSON object:
    ```json
    {
      "partyId": "john-doe-id",
      "items": [{ "itemId": "canon-id", "qty": 1 }]
    }
    ```
6.  **Backend** receives this. It subtracts 1 Canon Camera from stock and adds a debt to John Doe's ledger.

---

## 5. Key Terms for Juniors

- **DOM**: The browser's internal map of the webpage. React updates this efficiently.
- **JSON**: The language of data. Text that looks like Javascript objects. Used to talk between Frontend and Backend.
- **Hot Reload** (Vite): When you change code, the browser updates instantly without a full refresh.
- **Responsive**: The layout adjusts (using Tailwind classes like `md:flex`) so it looks good on both Phones and Laptops.
