# EthosTrade Contract Guide

## Overview

The `EthosTrade` contract interacts with `IEthosMarket` to buy and sell trust/distrust votes in a decentralized voting market.

## Contract Information

- **EthosTrade Address:** `0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60`
- **CDP Wallet:** `0xe2F3B3129b33A535f1Bf9c8EDaC50D3BdeE420Cc`

**not important**

- **Market Contract Address:** `0xC26F339F4E46C776853b1c190eC17173DBe059Bf`
- **Voting Asset ID:** `898`

## Function Guide & Integration

### 1. Buying Trust Votes

#### `longeetTrust(uint256 _marketId)`

**Description:**
Buys 1 trust vote in the market.

**Inputs:**

- `_marketId` (`uint256`): The ID of the market.

**Outputs:**

- Emits `AyeHeresOneTrustForYou(uint256 marketId)` event.

**Integration Steps:**

1. Call `longeetTrust(_marketId)`.
2. The contract queries `simulateBuy()` to estimate costs.
3. Executes `buyVotes()` with the correct price.
4. Listen for the emitted event.

---

### 2. Buying Distrust Votes

#### `longeetDistrust(uint256 _marketId)`

**Description:**
Buys 1 distrust vote in the market.

**Inputs:**

- `_marketId` (`uint256`): The ID of the market.

**Outputs:**

- Emits `AyeHeresOneDistrustForYou(uint256 marketId)` event.

**Integration Steps:**

1. Call `longeetDistrust(_marketId)`.
2. Contract estimates the required ETH via `simulateBuy()`.
3. Executes `buyVotes()`.
4. Listen for the emitted event.

---

### 3. Selling Trust Votes

#### `dumpeetTrust(uint256 _marketId)`

**Description:**
Sells 1 trust vote from the market.

**Inputs:**

- `_marketId` (`uint256`): The ID of the market.

**Outputs:**

- Emits `BogdanoffDampitTrust(uint256 marketId)` event.

**Integration Steps:**

1. Call `dumpeetTrust(_marketId)`.
2. The contract estimates proceeds using `simulateSell()`.
3. Executes `sellVotes()`.
4. Listen for the emitted event.

---

### 4. Selling Distrust Votes

#### `dumpeetDistrust(uint256 _marketId)`

**Description:**
Sells 1 distrust vote from the market.

**Inputs:**

- `_marketId` (`uint256`): The ID of the market.

**Outputs:**

- Emits `BogdanoffDampitDistrust(uint256 marketId)` event.

**Integration Steps:**

1. Call `dumpeetDistrust(_marketId)`.
2. The contract estimates the expected proceeds.
3. Executes `sellVotes()`.
4. Listen for the emitted event.

---

### 5. Managing Allowed Users

#### `allowedSwitcheroo(address _address)`

**Description:**
Toggles permission for an address in the `allowed` mapping.

**Inputs:**

- `_address` (`address`): The user to toggle.

**Outputs:**

- Updates the `allowed` mapping.

**Integration Steps:**

1. Call `allowedSwitcheroo(userAddress)`.
2. The user's permission status will be switched.

---

### 6. Recovering ETH

#### `recoverETH()`

**Description:**
Withdraws all ETH from the contract to the owner.

**Inputs:**

- None

**Outputs:**

- Sends contract ETH balance to the owner.

**Integration Steps:**

1. Call `recoverETH()`.
2. ETH is transferred to the contract owner.
