# Web3 Coinbase Hackathon

This project provides a Python and TypeScript implementation for interacting with a smart contract on the Base Mainnet. It enables users to perform trust and distrust trades using predefined contract methods.

## Directory Structure

```
web3/
│── abis/                        # Directory for storing contract ABI files
│── py/                          # Python implementation
│   ├── .env                     # Environment variables for Python (ignored in version control)
│   ├── main.py                  # Python script for interacting with the contract
│── ts/                          # TypeScript implementation
│   ├── node_modules/            # Installed dependencies
│   ├── .env                     # Environment variables for TypeScript (ignored in version control)
│   ├── bun.lockb                # Bun package lock file
│   ├── main.ts                  # TypeScript script for interacting with the contract
│   ├── package.json             # Dependencies and scripts
│   ├── README.md                # Documentation (this file)
│   ├── tsconfig.json            # TypeScript configuration
│── .env.example                 # Example environment variables
│── .gitignore                   # Files to ignore in version control
```

## Implementation Details

- `py/main.py` is the Python implementation.
- `ts/main.ts` is the TypeScript implementation.
- For TypeScript to work, you need to install `dotenv` and `@coinbase/coinbase-sdk`.
- For Python, you need to install `dotenv`, `cdp-sdk`, and use Python 3.10.

## Environment Variables

Before running the scripts, set up the required environment variables in a `.env` file.

### Required Environment Variables:

```
CDP_API_KEY=<your-cdp-api-key>
CDP_API_KEY_SECRET=<your-cdp-api-key-secret>
MNEMONIC_PHRASE=<your-mnemonic-phrase>
```

- **CDP_API_KEY**: API key for accessing the CDP API.
- **CDP_API_KEY_SECRET**: Secret key for CDP API authentication.
- **MNEMONIC_PHRASE**: Mnemonic phrase for initializing the wallet.

## Functions Available

### Python (`main.py`)

The Python script provides the following functions for interacting with the contract:

- `buy_trust(market_id: int)`: Executes the `longeetTrust` contract method.
- `buy_distrust(market_id: int)`: Executes the `longeetDistrust` contract method.
- `sell_trust(market_id: int)`: Executes the `dumpeetTrust` contract method.
- `sell_distrust(market_id: int)`: Executes the `dumpeetDistrust` contract method.
- `transfer_seraph(to_address: str)`: Transfers SERAPH tokens to another address.

Each function interacts with the smart contract using the provided wallet.

### TypeScript (`main.ts`)

The TypeScript script provides equivalent functions:

- `getWalletAddress()`: Retrieves the default wallet address.
- `buyTrust(marketId: number)`: Executes the `longeetTrust` contract method.
- `buyDistrust(marketId: number)`: Executes the `longeetDistrust` contract method.
- `sellTrust(marketId: number)`: Executes the `dumpeetTrust` contract method.
- `sellDistrust(marketId: number)`: Executes the `dumpeetDistrust` contract method.
- `transferSeraph(toAddress: string)`: Transfers SERAPH tokens to another address.

## Notes

- Ensure you have the correct ABI file in `abis/ethos-trade-abi.json`.
- The contract address used: `0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60`.
- Transactions may take some time to complete, and results can be logged for debugging.
