# Bitcoin Clone + DeFi (AMM & Staking)

A complete simulation of a crypto ecosystem featuring a Bitcoin-like blockchain, ERC-20 style Token Layer, Automated Market Maker (AMM), and Staking.

**Deployment:** Serverless on Vercel
**Database:** MongoDB Atlas

---

## 🌍 Economy & Pricing

### 1. Where do Dollars come from?
This system mimics a real crypto economy.
*   **USDT (Tether USD)**: Created automatically by the system (Admin Wallet) to represent Dollars.
*   **Price Anchoring**: On startup, the system creates a `BTC-USDT` Liquidity Pool.
    *   Initial Price: 1 BTC = 50,000 USDT.
*   **Valuation**: When you create a new Token (e.g., `MYCOIN`), it has no value until you add liquidity to a pool (e.g., `BTC-MYCOIN`). Its USD price is then derived:
    *   `Price(MYCOIN) = Price(BTC) * (Reserve_BTC / Reserve_MYCOIN)`

### 2. Fees
*   **Swap Fee**: 0.3% per transaction.
    *   **0.2%** goes to Liquidity Providers (increases pool size).
    *   **0.1%** goes to the **Owner/Admin Wallet** as revenue.

---

## 📖 Full API Reference

This section mirrors the Swagger UI documentation found at `/docs`.

### 🔐 Wallet & Auth

#### `POST /wallet/new`
Create a new anonymous wallet with ECDSA key pair.

*   **Request Body**: (Empty) `{}`
*   **Response**:
    ```json
    {
      "private_key": "string (hex)",
      "public_key": "string (hex)",
      "address": "string (hash)"
    }
    ```

#### `GET /wallet/{address}`
Get wallet details including Native Balance (Coins) and Unspent Transaction Outputs (UTXOs).

*   **Response**:
    ```json
    {
      "address": "string",
      "balance": 50.0,
      "utxos": [
        { "txid": "...", "vout": 0, "amount": 50.0, "address": "..." }
      ]
    }
    ```

#### `GET /wallet/{address}/history`
Get transaction history for a specific address (Token transfers).

*   **Response**:
    ```json
    {
      "history": [
        { "sender_address": "...", "receiver_address": "...", "amount": 10, "symbol": "TKN", "timestamp": 1709... }
      ]
    }
    ```

---

### 🪙 Token Layer

#### `POST /token/create`
Mint a new custom token.

*   **Request Body**:
    ```json
    {
      "name": "My Token",
      "symbol": "MTK",
      "total_supply": 1000000.0,
      "owner_address": "string"
    }
    ```
*   **Response**:
    ```json
    {
      "message": "Token created successfully",
      "token": { ... }
    }
    ```

#### `POST /token/transfer`
Transfer tokens between users. Requires signature.

*   **Request Body**:
    ```json
    {
      "sender_address": "string",
      "sender_public_key": "string",
      "receiver_address": "string",
      "symbol": "MTK",
      "amount": 100.0,
      "timestamp": 1709881234.0,
      "signature": "string (hex signature of: sender:receiver:symbol:amount:timestamp)"
    }
    ```

#### `POST /token/burn`
Burn tokens to reduce total supply.

*   **Request Body**:
    ```json
    {
      "symbol": "MTK",
      "amount": 50.0,
      "address": "string"
    }
    ```

#### `GET /token/list`
List all available tokens in the system.

#### `GET /token/{symbol}`
Get metadata for a specific token.

#### `GET /token/{symbol}/holders`
Get a list of all holders for a token.

#### `GET /token/{symbol}/richlist`
Get the top 10 holders by balance.

---

### 🏦 Marketplace (AMM)

#### `POST /market/pool/create`
Initialize a new Liquidity Pool (e.g., BTC-MTK). Requires providing initial liquidity for both sides.

*   **Request Body**:
    ```json
    {
      "token_symbol": "MTK",
      "initial_native": 1.0,   // Amount of BTC
      "initial_token": 100.0,  // Amount of MTK
      "creator_address": "string",
      "timestamp": 1709881234.0,
      "signature": "string"
    }
    ```

#### `POST /market/liquidity/add`
Add liquidity to an existing pool. Returns LP Tokens.

*   **Request Body**:
    ```json
    {
      "pair": "BTC-MTK",
      "user_address": "string",
      "amount_native": 0.5,
      "amount_token": 0.0, // Optional, usually calculated automatically
      "timestamp": 1709881234.0,
      "signature": "string"
    }
    ```

#### `POST /market/swap`
Swap tokens using the Constant Product Formula ($x \cdot y = k$).

*   **Request Body**:
    ```json
    {
      "user_address": "string",
      "pair": "BTC-MTK",
      "direction": "native_to_token", // OR "token_to_native"
      "amount_in": 0.1,
      "min_amount_out": 9.5, // Slippage protection
      "timestamp": 1709881234.0,
      "signature": "string"
    }
    ```

#### `GET /market/pools`
List all active liquidity pools.

#### `GET /market/stats`
Get global market statistics (e.g., 24h Volume).

---

### 💰 Staking

#### `POST /staking/deposit`
Lock assets to earn APY rewards.

*   **Request Body**:
    ```json
    {
      "user_address": "string",
      "symbol": "MTK", // or "BTC"
      "amount": 500.0,
      "duration_days": 30,
      "timestamp": 1709881234.0,
      "signature": "string"
    }
    ```

#### `POST /staking/withdraw`
Unstake assets and claim rewards.

*   **Request Body**:
    ```json
    {
      "stake_id": "string (ObjectId)",
      "signature": "string"
    }
    ```

---

### 📈 Pricing & Charts

#### `GET /price/ticker`
Get the current live price of BTC (in USD) and all Tokens (in BTC and USD).

*   **Response**:
    ```json
    {
      "BTC": { "price_usd": 50123.45 },
      "tokens": {
        "MTK": { "price_btc": 0.01, "price_usd": 501.23 }
      }
    }
    ```

#### `GET /price/chart/{symbol}`
Get historical OHLC (Open-High-Low-Close) data for charts (1-minute candles).

---

### ⛏️ Blockchain Core

#### `POST /mine`
Simulate Proof-of-Work mining to create a new block and earn rewards.

*   **Query Parameter**: `?miner_address=YOUR_WALLET_ADDRESS`
*   **Response**:
    ```json
    {
      "message": "Block mined",
      "block": { "index": 5, "hash": "000...", "transactions": [...] },
      "reward_breakdown": { "base": 50.0, "fees": 0.0, "total": 50.0 }
    }
    ```

#### `GET /chain/state`
Get the current block height and last block hash.

#### `GET /block/{hash}`
Get details of a specific block.

---

### 🛠 Extras

#### `POST /faucet`
Get free test coins for development.

*   **Request Body**: `{"address": "string"}`

#### `GET /network/stats`
Get total block count.

#### `GET /system/health`
Check API status.

---

## 📦 Setup & Deployment

1.  **Clone Repository**
    ```bash
    git clone <repo_url>
    ```
2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set Environment Variables**
    *   `MONGODB_URI`: Your MongoDB Atlas Connection String.
4.  **Run Locally**
    ```bash
    uvicorn api.index:app --reload
    ```
5.  **Deploy to Vercel**
    ```bash
    vercel
    ```
