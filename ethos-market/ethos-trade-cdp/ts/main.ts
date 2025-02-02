import { Coinbase, Wallet } from '@coinbase/coinbase-sdk'
import dotenv from 'dotenv'
import abi from '../abis/ethos-trade-abi.json'

dotenv.config()

// Configuration
const CDP_API_KEY: string | undefined = process.env.CDP_API_KEY
const CDP_API_KEY_SECRET: string | undefined = process.env.CDP_API_KEY_SECRET
const MNEMONIC_PHRASE: string | undefined = process.env.MNEMONIC_PHRASE

// Ethos trade contract address
const CONTRACT_ADDRESS: string = '0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60'

// Ethos trade
const AIXBT_MARKET_ID: number = 898

// SERAPH
const SERAPH_CONTRACT_ADDRESS: string =
  '0x4f81837C2f4A189A0B69370027cc2627d93785B4'

if (!CDP_API_KEY || !CDP_API_KEY_SECRET || !MNEMONIC_PHRASE) {
  throw new Error('Missing required environment variables.')
}

// Initialize CDP API
Coinbase.configure({ apiKeyName: CDP_API_KEY, privateKey: CDP_API_KEY_SECRET })

// Initialize Wallet
const wallet = await Wallet.import(
  { mnemonicPhrase: MNEMONIC_PHRASE },
  Coinbase.networks.BaseMainnet
)

// Ethos trade function
async function executeTrade(method: string, marketId: number) {
  try {
    const invocation = await wallet.invokeContract({
      contractAddress: CONTRACT_ADDRESS,
      method,
      args: { _marketId: marketId.toFixed() },
      abi,
    })

    const tx = await invocation.wait()

    return tx
  } catch (error) {
    console.error(`Error executing ${method}:`, error)
    return null
  }
}

// --- Functions for export ---

// Get default wallet address
export async function getWalletAddress() {
  return await wallet.getDefaultAddress()
}

// Buy trust on ethos
export async function buyTrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('longeetTrust', marketId)
}

// Buy distrust on ethos
export async function buyDistrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('longeetDistrust', marketId)
}

// Sell trust on ethos
export async function sellTrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('dumpeetTrust', marketId)
}

// Sell distrust on ethos
export async function sellDistrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('dumpeetDistrust', marketId)
}

// Transfer seraph to another address
export async function transferSeraph(toAddress: string) {
  const transfer = await wallet.createTransfer({
    amount: 1,
    assetId: SERAPH_CONTRACT_ADDRESS,
    destination: toAddress,
  })

  const tx = await transfer.wait()

  return tx
}

// --- Functions for export ---
