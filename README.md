# Bitcoin Clone + Token Layer (FastAPI + MongoDB Atlas)

A simplified, educational blockchain implementation deployed on Vercel using FastAPI and MongoDB Atlas. This project mimics the core mechanics of Bitcoin (UTXO, Mining) and adds a Token Layer (like ERC-20) and a decentralized Marketplace.

**IMPORTANT:** This API strictly uses **GET** and **POST** methods only.

---

## 🚀 Deployment

### Prerequisites
1.  **MongoDB Atlas Account**: You need a connection string (URI).
2.  **Vercel Account**: For serverless deployment.

### Steps
1.  **Clone Repository**
    ```bash
    git clone <repo-url>
    cd <repo-name>
    ```

2.  **Install Dependencies** (Locally)
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment Variables**
    Create a `.env` file (or set in Vercel Dashboard):
    ```ini
    MONGODB_URI="mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority"
    ```
    *(Note: For this specific demo, the URI might be hardcoded in `api/core/database.py` per instructions, but using env vars is recommended).*

4.  **Run Locally**
    ```bash
    uvicorn api.index:app --reload
    ```

5.  **Deploy to Vercel**
    ```bash
    vercel
    ```

---

## 📖 API Documentation

All endpoints return JSON. Errors are returned with status codes (400, 404, 500) and a message.

### 1. Wallet & Auth (Anonymous)

#### `POST /wallet/new`
Generates a new ECDSA key pair and wallet address.
- **Request:** Empty body.
- **Response:**
  ```json
  {
    "private_key": "hex_string...",
    "public_key": "hex_string...",
    "address": "hash_string..."
  }
  ```

#### `GET /wallet/{address}`
Checks the balance and UTXOs of an address.
- **Response:**
  ```json
  {
    "address": "...",
    "balance": 50.0,
    "utxos": [ ... ]
  }
  ```

### 2. Blockchain Core

#### `GET /chain/state`
Get current blockchain height and last block hash.

#### `POST /mine`
Simulates mining a block. Rewards the miner with 50 coins (Coinbase).
- **Query Param:** `miner_address` (default: "miner1")
- **Response:**
  ```json
  {
    "message": "Block mined",
    "block": { ... }
  }
  ```

#### `GET /block/{hash}`
Retrieve a block by its hash (currently simplified to return last block if hash matches).

### 3. Token Layer (Layer 2)

#### `POST /token/create`
Create a new custom token.
- **Body:**
  ```json
  {
    "name": "My Token",
    "symbol": "MTK",
    "total_supply": 1000000,
    "owner_address": "wallet_address_here"
  }
  ```

#### `POST /token/transfer`
Transfer tokens between users.
- **Body:**
  ```json
  {
    "sender_address": "...",
    "sender_public_key": "...",
    "receiver_address": "...",
    "symbol": "MTK",
    "amount": 100,
    "signature": "hex_signature_of_tx_details"
  }
  ```

#### `GET /token/list`
List all created tokens.

#### `GET /token/{symbol}`
Get details of a specific token.

#### `GET /token/{symbol}/holders`
Get list of token holders and their balances.

### 4. Marketplace

#### `POST /market/order`
Place a Buy or Sell order. Matches immediately if a crossing order exists.
- **Body:**
  ```json
  {
    "user_address": "...",
    "order_type": "buy",   // or "sell"
    "pair": "MTK-BTC",
    "price": 10.5,
    "amount": 100,
    "signature": "..."
  }
  ```

#### `GET /market/orderbook`
Get the current bids and asks for a trading pair.
- **Query Param:** `pair` (e.g., `MTK-BTC`)
- **Response:**
  ```json
  {
    "bids": [ ... ],
    "asks": [ ... ]
  }
  ```

---

## 🛠 Tech Stack

*   **Language:** Python 3.9+
*   **Framework:** FastAPI
*   **Database:** MongoDB Atlas (Async `motor` driver)
*   **Server:** Uvicorn (ASGI)
*   **Platform:** Vercel Serverless Functions

## 📝 Notes & Assumptions

1.  **Consensus:** The Proof of Work is simulated (low difficulty) to ensure serverless execution times (<10s).
2.  **Security:** Signatures are checked, but nonce/replay protection is simplified.
3.  **Matching Engine:** Runs purely on-demand when an order is placed (no background loop).
4.  **Data Serialization:** All MongoDB `ObjectId`s are automatically converted to strings to prevent JSON errors.
