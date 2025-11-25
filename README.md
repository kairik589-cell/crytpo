# Bitcoin Clone + DeFi (AMM & Staking)

A comprehensive blockchain simulation featuring a Bitcoin-like native chain, a custom Token Layer (Layer 2), an Automated Market Maker (AMM) for decentralized trading, a Staking system, and a dynamic Pricing system.

**Deployment:** Serverless on Vercel
**Database:** MongoDB Atlas

## 🌟 New Features (v2.1)

1.  **Dynamic Pricing System**:
    *   **Native Coin (BTC) Price**: Starts at $1.00 USD.
    *   **Market Pressure**: Buying BTC (swapping Token->Native) pushes price UP. Selling BTC pushes price DOWN.
    *   **Token Pricing**: Calculated dynamically based on AMM pool ratios ($Price_{Token} = Ratio \times Price_{BTC}$).
2.  **OHLC Charts**:
    *   Minute-by-minute candlestick data tracking for all tokens and BTC.
3.  **Automated Market Maker (AMM)**:
    *   Constant Product Formula ($x \cdot y = k$).
    *   Liquidity Pools & Swap logic.
4.  **Staking & Mining**:
    *   Earn APY by staking.
    *   Earn Swap Fees by mining blocks.

## 🚀 API Endpoints

### 📈 Pricing & Charts
*   `GET /price/ticker`: Get current prices for BTC (USD) and all Tokens (BTC & USD).
*   `GET /price/chart/{symbol}`: Get OHLC chart data (1-minute candles).

### 🏦 Market (AMM)
*   `POST /market/pool/create`: Initialize a new trading pair.
*   `POST /market/liquidity/add`: Add liquidity to a pool.
*   `POST /market/swap`: Swap tokens immediately (Updates Price).
*   `GET /market/pools`: List all active pools.

### 💰 Staking
*   `POST /staking/deposit`: Stake assets.
*   `POST /staking/withdraw`: Unstake and claim rewards.

### 🔗 Blockchain & Tokens
*   `POST /mine`: Mine a block.
*   `POST /token/create`: Mint new tokens.
*   `POST /token/transfer`: Send tokens.

## 📦 Installation

1.  Clone repo.
2.  `pip install -r requirements.txt`
3.  Set `MONGODB_URI`.
4.  `uvicorn api.index:app --reload`
