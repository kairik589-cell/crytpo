# Bitcoin Clone + DeFi (AMM & Staking)

A comprehensive blockchain simulation featuring a Bitcoin-like native chain, a custom Token Layer (Layer 2), an Automated Market Maker (AMM) for decentralized trading, and a Staking system.

**Deployment:** Serverless on Vercel
**Database:** MongoDB Atlas

## 🌟 New Features (v2.0)

1.  **Automated Market Maker (AMM)**:
    *   Replaces the old Orderbook.
    *   Create Liquidity Pools (`Token` <-> `Native Coin`).
    *   Swap tokens using the $x * y = k$ formula.
    *   Earn LP tokens by adding liquidity.
2.  **Staking System**:
    *   Lock tokens or coins to earn APY (simulated 5%).
    *   Time-based reward calculation.
3.  **Miner Fee Distribution**:
    *   0.1% of every swap is collected in a "Fee Pot".
    *   Miners receive these accumulated fees + block reward when mining a block.
4.  **10+ Extra Features**:
    *   Faucet, Wallet History, Token Burn, Rich List, Market Stats, Charts, Leaderboards, etc.

## 🚀 API Endpoints

### 🏦 Market (AMM)
*   `POST /market/pool/create`: Initialize a new trading pair.
*   `POST /market/liquidity/add`: Add liquidity to a pool.
*   `POST /market/swap`: Swap tokens immediately.
*   `GET /market/pools`: List all active pools.

### 💰 Staking
*   `POST /staking/deposit`: Stake assets.
*   `POST /staking/withdraw`: Unstake and claim rewards.

### 🛠 Extras
*   `POST /faucet`: Get free test coins.
*   `GET /wallet/{address}/history`: View transaction history.
*   `POST /token/burn`: Burn tokens to reduce supply.
*   `GET /token/{symbol}/richlist`: Top holders.
*   `GET /market/stats`: Global volume metrics.
*   `GET /market/chart/{pair}`: Historical price data.

### 🔗 Blockchain & Tokens
*   `POST /mine`: Mine a block (includes fee rewards).
*   `POST /token/create`: Mint new tokens.
*   `POST /token/transfer`: Send tokens.

## 📦 Installation

1.  Clone repo.
2.  `pip install -r requirements.txt`
3.  Set `MONGODB_URI`.
4.  `uvicorn api.index:app --reload`
