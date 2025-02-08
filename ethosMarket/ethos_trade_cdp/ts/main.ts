import { Coinbase, Wallet } from "@coinbase/coinbase-sdk";
import dotenv from "dotenv";
import ethosAbi from "../abis/ethos-trade-abi.json";
import stakingAbi from "../abis/seraph-staking-abi.json";
import sttaoAbi from "../abis/sttao-abi.json";
import seraphAbi from "../abis/seraph-abi.json";

dotenv.config();

// Configuration
const CDP_API_KEY: string | undefined = process.env.CDP_API_KEY;
const CDP_API_KEY_SECRET: string | undefined = process.env.CDP_API_KEY_SECRET;
const MNEMONIC_PHRASE: string | undefined = process.env.MNEMONIC_PHRASE;

// Ethos trade contract
const CONTRACT_ADDRESS_ETHOS: string =
  "0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60";

// Staking contract
const CONTRACT_ADDRESS_STAKING: string =
  "0xD4b47EE9879470179bAC7BECf49d2755ce5a8ea0";

// Ethos trade
const AIXBT_MARKET_ID: number = 898;

// SERAPH & stTAO
const SERAPH_CONTRACT_ADDRESS: string =
  "0x4f81837C2f4A189A0B69370027cc2627d93785B4";
const STTAO_CONTRACT_ADDRESS: string =
  "0x806041B6473DA60abbe1b256d9A2749A151be6C6";

if (!CDP_API_KEY || !CDP_API_KEY_SECRET || !MNEMONIC_PHRASE) {
  throw new Error("Missing required environment variables.");
}

// Initialize CDP API
Coinbase.configure({ apiKeyName: CDP_API_KEY, privateKey: CDP_API_KEY_SECRET });

// Initialize Wallet
const wallet = await Wallet.import(
  { mnemonicPhrase: MNEMONIC_PHRASE },
  Coinbase.networks.BaseMainnet
);

// Ethos trade function
async function executeTrade(method: string, marketId: number) {
  try {
    const invocation = await wallet.invokeContract({
      contractAddress: CONTRACT_ADDRESS_ETHOS,
      method,
      args: { _marketId: marketId.toFixed() },
      abi: ethosAbi,
    });

    const tx = await invocation.wait();
    return tx;
  } catch (error) {
    console.error(`Error executing ${method}:`, error);
    return null;
  }
}

// Staking function
async function executeReward(
  method: string,
  rewardToken: string,
  rewardAmount: number
) {
  try {
    const invocation = await wallet.invokeContract({
      contractAddress: CONTRACT_ADDRESS_STAKING,
      method,
      args: {
        _rewardToken: rewardToken,
        _rewardAmount: rewardAmount.toFixed(),
      },
      abi: stakingAbi,
    });

    const tx = await invocation.wait();
    return tx;
  } catch (error) {
    console.error(`Error executing ${method}:`, error);
    return null;
  }
}

// stTAO approve function
async function executeApproveSttao(
  method: string,
  spender: string,
  amount: number
) {
  try {
    const invocation = await wallet.invokeContract({
      contractAddress: STTAO_CONTRACT_ADDRESS,
      method,
      args: { spender, amount: amount.toFixed() },
      abi: sttaoAbi,
    });

    const tx = await invocation.wait();
    return tx;
  } catch (error) {
    console.error(`Error executing ${method}:`, error);
    return null;
  }
}

// SERAPH approve function
async function executeApproveSeraph(
  method: string,
  spender: string,
  amount: number
) {
  try {
    const invocation = await wallet.invokeContract({
      contractAddress: SERAPH_CONTRACT_ADDRESS,
      method,
      args: { spender, amount: amount.toFixed() },
      abi: seraphAbi,
    });

    const tx = await invocation.wait();
    return tx;
  } catch (error) {
    console.error(`Error executing ${method}:`, error);
    return null;
  }
}

// --- Functions for export ---

// Get default wallet address
export async function getWalletAddress() {
  return await wallet.getDefaultAddress();
}

// Buy trust on ethos
export async function buyTrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade("longeetTrust", marketId);
}

// Buy distrust on ethos
export async function buyDistrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade("longeetDistrust", marketId);
}

// Sell trust on ethos
export async function sellTrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade("dumpeetTrust", marketId);
}

// Sell distrust on ethos
export async function sellDistrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade("dumpeetDistrust", marketId);
}

// Transfer SERAPH to another address
export async function transferSeraph(toAddress: string) {
  try {
    const transfer = await wallet.createTransfer({
      amount: 1,
      assetId: SERAPH_CONTRACT_ADDRESS,
      destination: toAddress,
    });

    const tx = await transfer.wait();
    return tx;
  } catch (error) {
    console.error("Error transferring SERAPH:", error);
    return null;
  }
}

// External function to approve and execute rewards for stTAO and SERAPH
export async function approveAndExecuteRewards() {
  // Approve stTAO
  const sttaoBalance = await wallet.getBalance(STTAO_CONTRACT_ADDRESS);
  const sttaoApproveTx = await executeApproveSttao(
    "approve",
    CONTRACT_ADDRESS_STAKING,
    sttaoBalance
  );
  if (!sttaoApproveTx) {
    console.error("Failed to approve stTAO");
    return null;
  }

  // Approve SERAPH
  const seraphBalance = await wallet.getBalance(SERAPH_CONTRACT_ADDRESS);
  const seraphApproveTx = await executeApproveSeraph(
    "approve",
    CONTRACT_ADDRESS_STAKING,
    seraphBalance
  );
  if (!seraphApproveTx) {
    console.error("Failed to approve SERAPH");
    return null;
  }

  // Execute reward for stTAO
  const rewardAmountSttao = sttaoBalance / 10;
  const sttaoRewardTx = await executeReward(
    "reward",
    STTAO_CONTRACT_ADDRESS,
    rewardAmountSttao
  );
  if (!sttaoRewardTx) {
    console.error("Failed to execute reward for stTAO");
    return null;
  }

  // Execute reward for SERAPH
  const rewardAmountSeraph = seraphBalance / 10;
  const seraphRewardTx = await executeReward(
    "reward",
    SERAPH_CONTRACT_ADDRESS,
    rewardAmountSeraph
  );
  if (!seraphRewardTx) {
    console.error("Failed to execute reward for SERAPH");
    return null;
  }

  return {
    sttaoApproveTx,
    seraphApproveTx,
    sttaoRewardTx,
    seraphRewardTx,
  };
}

// --- Functions for export ---
