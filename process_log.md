# RentalPro - Development Process Log

This file documents the steps taken to connect the Frontend to the Backend API and integrate JWT authentication. This is intended to help developers understand the logic behind the changes.

## Phase: Frontend to Backend Integration

### 1. Replacing Dummy JWT Auth with Real Backend Auth

- **File**: `Frontend/src/services/auth.js`
- **What was done**: We replaced the hardcoded `mock-jwt-token-12345` with a real API call to the backend. We use `axios` to make a `POST` request to `/auth/login` sending the `username` and `password` as `application/x-www-form-urlencoded` data (as required by OAuth2 with FastAPI).
- **Why**: To actually authenticate users against the backend database and obtain a real, securely signed JWT token for accessing protected routes.

### 2. Creating an API Client with Axios interceptors

- **File**: `Frontend/src/services/api.js` (NEW)
- **What was done**: Created an Axios instance configured with the base backend URL (`http://127.0.0.1:8000`). We added a request interceptor that automatically attaches the `Authorization: Bearer <token>` header to every outgoing request if a token is found in `localStorage`.
- **Why**: This prevents us from having to manually add the token header to every single API call we make from the frontend.

### 3. Rewriting Data Access Layer (db.js)

- **File**: `Frontend/src/services/db.js`
- **What was done**: We removed all the `localStorage` logic that was previously mocking the database on the frontend. We rewrote `items`, `parties`, and `transactions` functions to use the Axios `api` instance to make `GET`, `POST`, `PUT`, `DELETE` requests to the real backend endpoints (`/items`, `/parties`, `/rent`, `/returns`). The return formats were mapped closely to what the UI components already expect to minimize changes to React components.
- **Why**: So the frontend interacts with the persistent backend database. By keeping the `db` interface roughly the same, the UI components don't all need massive rewrites.

_Note: Work is ongoing to ensure all UI components correctly parse the data coming from the real backend._
