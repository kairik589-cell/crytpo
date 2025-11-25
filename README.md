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

## 📖 API Reference

All endpoints accept/return JSON.

### 🔐 Wallet

#### `POST /wallet/new`
Create a new anonymous wallet.
**Response:**
```json
{
  "private_key": "hex...",
  "public_key": "hex...",
  "address": "hash..."
}
```

#### `GET /wallet/{address}`
Get balance (Native Coins & Tokens).

---

### 🪙 Tokens

#### `POST /token/create`
Mint a new custom token.
**Request:**
```json
{
  "name": "My Coin",
  "symbol": "MCN",
  "total_supply": 1000000,
  "owner_address": "your_address"
}
```

#### `POST /token/transfer`
Send tokens to another user.
**Request:**
```json
{
  "sender_address": "...",
  "sender_public_key": "...",
  "receiver_address": "...",
  "symbol": "MCN",
  "amount": 100,
  "timestamp": 1709880000,
  "signature": "hex..."
}
```

---

### 🏦 Marketplace (AMM)

#### `POST /market/pool/create`
Create a trading pair (e.g., BTC-MCN).
**Request:**
```json
{
  "token_symbol": "MCN",
  "initial_native": 1.0,   // 1 BTC
  "initial_token": 100.0,  // 100 MCN (Implies 1 BTC = 100 MCN)
  "creator_address": "...",
  "timestamp": 1709880000,
  "signature": "..."
}
```

#### `POST /market/liquidity/add`
Add funds to an existing pool to earn LP tokens.
**Request:**
```json
{
  "pair": "BTC-MCN",
  "user_address": "...",
  "amount_native": 0.5,
  "timestamp": 1709880000,
  "signature": "..."
}
```

#### `POST /market/swap`
Swap tokens immediately.
**Request:**
```json
{
  "user_address": "...",
  "pair": "BTC-MCN",
  "direction": "native_to_token", // or "token_to_native"
  "amount_in": 0.1,
  "min_amount_out": 9.0, // Slippage protection
  "timestamp": 1709880000,
  "signature": "..."
}
```

---

### ⛏️ Blockchain

#### `POST /mine`
Mine a new block to confirm transactions and earn Block Reward (50 BTC).
**Query Param:** `?miner_address=...`

#### `GET /chain/state`
Get current block height.

---

### 📈 Pricing & Charts

#### `GET /price/ticker`
Get current prices of all tokens in USD.

#### `GET /price/chart/{symbol}`
Get historical OHLC data (Candlestick chart).

---

## 🛠 Setup

1.  **Clone & Install**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Locally**:
    ```bash
    uvicorn api.index:app --reload
    ```
3.  **Deploy to Vercel**:
    ```bash
    vercel
    ```
