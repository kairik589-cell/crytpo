# Bitcoin Clone + Token Layer (FastAPI + MongoDB Atlas)

This is a simplified blockchain implementation designed for educational purposes, deployed as a serverless application on Vercel. It includes a native UTXO-based chain, a custom Token Layer (similar to ERC-20), and a decentralized Marketplace simulation.

**NOTE:** All endpoints strictly use **GET** and **POST** methods.

## Features

1.  **Blockchain Core**
    *   UTXO Model
    *   Proof of Work (Simplified Mining)
    *   Block & Transaction structures
2.  **Token Layer**
    *   Create custom tokens
    *   Transfer tokens (recorded in DB)
    *   Query holders
3.  **Marketplace**
    *   Orderbook for Token/Coin pairs
    *   Simple matching engine

## Deployment to Vercel

1.  Clone this repository.
2.  Install Vercel CLI: `npm i -g vercel`
3.  Run `vercel` to deploy.

**Environment Variables:**
Ensure you have your MongoDB connection string ready.

## API Documentation

Once deployed, visit `/docs` for the interactive Swagger UI.

### Key Endpoints

*   `POST /wallet/new`: Create a new wallet
*   `POST /mine`: Mine a new block
*   `POST /token/create`: Create a new token
*   `POST /token/transfer`: Transfer tokens
*   `POST /market/order`: Place a buy/sell order
