import { Coinbase, Wallet } from '@coinbase/coinbase-sdk'
import dotenv from 'dotenv'
import ethosAbi from '../abis/ethos-trade-abi.json'
import seraphAbi from '../abis/seraph-abi.json'
import stakingAbi from '../abis/seraph-staking-abi.json'
import sttaoAbi from '../abis/sttao-abi.json'

dotenv.config()

// --- Configuration & Setup ---

const CDP_API_KEY: string | undefined = process.env.CDP_API_KEY
const CDP_API_KEY_SECRET: string | undefined = process.env.CDP_API_KEY_SECRET
const MNEMONIC_PHRASE: string | undefined = process.env.MNEMONIC_PHRASE

const CONTRACT_ADDRESS_ETHOS: string =
  '0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60'
const CONTRACT_ADDRESS_STAKING: string =
  '0xD4b47EE9879470179bAC7BECf49d2755ce5a8ea0'
const SERAPH_CONTRACT_ADDRESS: string =
  '0x4f81837C2f4A189A0B69370027cc2627d93785B4'
const STTAO_CONTRACT_ADDRESS: string =
  '0x806041B6473DA60abbe1b256d9A2749A151be6C6'

const AIXBT_MARKET_ID: number = 898

if (!CDP_API_KEY || !CDP_API_KEY_SECRET || !MNEMONIC_PHRASE) {
  throw new Error('Missing required environment variables.')
}

// --- Initialization ---

Coinbase.configure({ apiKeyName: CDP_API_KEY, privateKey: CDP_API_KEY_SECRET })

const wallet = await Wallet.import(
  { mnemonicPhrase: MNEMONIC_PHRASE },
  Coinbase.networks.BaseMainnet
)

// --- Helper Functions ---

interface InvokeContractParams {
  contractAddress: string
  method: string
  args: Record<string, string>
  abi: any // Consider defining a type for your ABIs
}

async function invokeContract(params: InvokeContractParams) {
  try {
    const invocation = await wallet.invokeContract({
      contractAddress: params.contractAddress,
      method: params.method,
      args: params.args,
      abi: params.abi,
    })

    const tx = await invocation.wait()
    return tx
  } catch (error) {
    console.error(`Error executing ${params.method}:`, error)
    return null
  }
}

// --- Contract Specific Functions ---

async function executeTrade(method: string, marketId: number) {
  const args = { _marketId: marketId.toString() }
  return invokeContract({
    contractAddress: CONTRACT_ADDRESS_ETHOS,
    method,
    args,
    abi: ethosAbi,
  })
}

async function executeReward(
  method: string,
  rewardToken: string,
  rewardAmount: number
) {
  const args = {
    _rewardToken: rewardToken,
    _rewardAmount: rewardAmount.toString(),
  }
  return invokeContract({
    contractAddress: CONTRACT_ADDRESS_STAKING,
    method,
    args,
    abi: stakingAbi,
  })
}

async function executeApproveSttao(
  method: string,
  spender: string,
  amount: number
) {
  const args = { spender, amount: amount.toString() }
  return invokeContract({
    contractAddress: STTAO_CONTRACT_ADDRESS,
    method,
    args,
    abi: sttaoAbi,
  })
}

async function executeApproveSeraph(
  method: string,
  spender: string,
  amount: number
) {
  const args = { spender, amount: amount.toString() }
  return invokeContract({
    contractAddress: SERAPH_CONTRACT_ADDRESS,
    method,
    args,
    abi: seraphAbi,
  })
}

// --- Public API Functions ---

export async function getWalletAddress() {
  return await wallet.getDefaultAddress()
}

export async function buyTrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('longeetTrust', marketId)
}

export async function buyDistrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('longeetDistrust', marketId)
}

export async function sellTrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('dumpeetTrust', marketId)
}

export async function sellDistrust(marketId: number = AIXBT_MARKET_ID) {
  return await executeTrade('dumpeetDistrust', marketId)
}

export async function transferSeraph(toAddress: string) {
  try {
    const transfer = await wallet.createTransfer({
      amount: 1,
      assetId: SERAPH_CONTRACT_ADDRESS,
      destination: toAddress,
    })

    const tx = await transfer.wait()
    return tx
  } catch (error) {
    console.error('Error transferring SERAPH:', error)
    return null
  }
}

export async function approveAndExecuteRewards() {
  // Approve stTAO
  const sttaoBalance = (
    await wallet.getBalance(STTAO_CONTRACT_ADDRESS)
  ).toNumber()
  const sttaoApproveTx = await executeApproveSttao(
    'approve',
    CONTRACT_ADDRESS_STAKING,
    sttaoBalance
  )
  if (!sttaoApproveTx) {
    console.error('Failed to approve stTAO')
    return null
  }

  // Approve SERAPH
  const seraphBalance = (
    await wallet.getBalance(SERAPH_CONTRACT_ADDRESS)
  ).toNumber()
  const seraphApproveTx = await executeApproveSeraph(
    'approve',
    CONTRACT_ADDRESS_STAKING,
    seraphBalance
  )
  if (!seraphApproveTx) {
    console.error('Failed to approve SERAPH')
    return null
  }

  // Execute reward for stTAO
  const rewardAmountSttao = sttaoBalance / 10
  const sttaoRewardTx = await executeReward(
    'updateRewardIndex',
    STTAO_CONTRACT_ADDRESS,
    rewardAmountSttao
  )
  if (!sttaoRewardTx) {
    console.error('Failed to execute reward for stTAO')
    return null
  }

  // Execute reward for SERAPH
  const rewardAmountSeraph = seraphBalance / 10
  const seraphRewardTx = await executeReward(
    'updateRewardIndex',
    SERAPH_CONTRACT_ADDRESS,
    rewardAmountSeraph
  )
  if (!seraphRewardTx) {
    console.error('Failed to execute reward for SERAPH')
    return null
  }

  return {
    sttaoApproveTx,
    seraphApproveTx,
    sttaoRewardTx,
    seraphRewardTx,
  }
}
