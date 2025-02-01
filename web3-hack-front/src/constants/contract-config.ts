import ethosAbi from './abis/ethos-abi.json'
import seraphAbi from './abis/seraph-abi.json'

export const seraphContractConfig = {
  address: '0x4f81837C2f4A189A0B69370027cc2627d93785B4',
  abi: seraphAbi,
} as const

export const ethosContractConfig = {
  address: '0xc26f339f4e46c776853b1c190ec17173dbe059bf',
  abi: ethosAbi,
} as const
