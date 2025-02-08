import os
import json
from cdp import Cdp, Wallet, MnemonicSeedPhrase  
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CDP_API_KEY = os.getenv("CDP_API_KEY")
CDP_API_KEY_SECRET = os.getenv("CDP_API_KEY_SECRET")
MNEMONIC_PHRASE = os.getenv("MNEMONIC_PHRASE")

# Load ethos-trade contract ABI
ABI_PATH_ETHOS = "../abis/ethos-trade-abi.json"
CONTRACT_ADDRESS_ETHOS = "0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60"

# Load seraph-staking contract ABI
ABI_PATH_STAKING = "../abis/seraph-staking-abi.json"
CONTRACT_ADDRESS_STAKING = "0xD4b47EE9879470179bAC7BECf49d2755ce5a8ea0"

# Ethos market
AIXBT_MARKET_ID = 898

# Load SERAPH
ABI_PATH_SERAPH = "../abis/seraph-abi.json"
SERAPH_CONTRACT_ADDRESS = "0x4f81837C2f4A189A0B69370027cc2627d93785B4"
# Load stTAO
ABI_PATH_STTAO = "../abis/sttao-abi.json"
STTAO_CONTRACT_ADDRESS = "0x806041B6473DA60abbe1b256d9A2749A151be6C6"

# Validate environment variables
if not all([CDP_API_KEY, CDP_API_KEY_SECRET, MNEMONIC_PHRASE]):
    raise ValueError("Missing required environment variables.")

# Initialize CDP API
Cdp.configure(CDP_API_KEY, CDP_API_KEY_SECRET)

# Initialize Wallet
wallet = Wallet.import_wallet(
    MnemonicSeedPhrase(MNEMONIC_PHRASE), network_id="base-mainnet"
)

# Load contract ABI-ETHOS
try:
    with open(ABI_PATH_ETHOS, "r") as file:
        abi_ethos = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"ABI file not found at {ABI_PATH_ETHOS}")
except json.JSONDecodeError:
    raise ValueError("Error decoding ABI JSON file.")

# Load contract ABI-STAKING
try:
    with open(ABI_PATH_STAKING, "r") as file:
        abi_staking = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"ABI file not found at {ABI_PATH_STAKING}")
except json.JSONDecodeError:
    raise ValueError("Error decoding ABI JSON file.")

# Load contract ABI-STTAO
try:
    with open(ABI_PATH_STTAO, "r") as file:
        abi_sttao = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"ABI file not found at {ABI_PATH_STTAO}")
except json.JSONDecodeError:
    raise ValueError("Error decoding ABI JSON file.")

# Load contract ABI-SERAPH
try:
    with open(ABI_PATH_SERAPH, "r") as file:
        abi_seraph = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"ABI file not found at {ABI_PATH_SERAPH}")
except json.JSONDecodeError:
    raise ValueError("Error decoding ABI JSON file.")

# Ethos trade function
def execute_trade(method: str, market_id: int):
    """
    Executes a contract method with optional profile ID.
    
    :param method: Name of the contract method to invoke.
    :param profile_id: Optional profile ID to pass as an argument.
    :return: Transaction result.
    """
    try:
        invocation = wallet.invoke_contract(
            CONTRACT_ADDRESS_ETHOS=CONTRACT_ADDRESS_ETHOS,
            abi=abi_ethos,
            method=method,
            args={"_marketId": str(market_id)}
        )
        tx = invocation.wait()
        return tx
    except Exception as e:
        print(f"Error executing {method}: {e}")
        return None
    
# Staking function
def execute_reward(method: str, rewardToken: str, rewardAmount: int):
    try:
        invocation = wallet.invoke_contract(
            CONTRACT_ADDRESS_STAKING=CONTRACT_ADDRESS_STAKING,
            abi=abi_staking,
            method=method,
            args={"_rewardToken": str(rewardToken), "_rewardAmount": str(rewardAmount)}
        )
        tx = invocation.wait()
        return tx
    except Exception as e:
        print(f"Error executing {method}: {e}")
        return None

# stTAO approve function
def execute_approve_sttao(method: str, spender: str, amount: int):
    try:
        invocation = wallet.invoke_contract(
            STTAO_CONTRACT_ADDRESS=STTAO_CONTRACT_ADDRESS,
            abi=abi_sttao,
            method=method,
            args={"spender": spender, "amount": str(amount)}
        )
        tx = invocation.wait()
        return tx
    except Exception as e:
        print(f"Error executing {method}: {e}")
        return None
    
# SERAPH approve function
def execute_approve_seraph(method: str, spender: str, amount: int):
    try:
        invocation = wallet.invoke_contract(
            SERAPH_CONTRACT_ADDRESS=SERAPH_CONTRACT_ADDRESS,
            abi=abi_seraph,
            method=method,
            args={"spender": spender, "amount": str(amount)}
        )
        tx = invocation.wait()
        return tx
    except Exception as e:
        print(f"Error executing {method}: {e}")
        return None

# --- Functions for export ---

# Get default wallet address
def get_wallet_address():
    return wallet.default_address.address_id

# Buy trust on ethos
def buy_trust(market_id: int = AIXBT_MARKET_ID):
    return execute_trade("longeetTrust", market_id)

# Buy distrust on ethos
def buy_distrust(market_id: int = AIXBT_MARKET_ID):
    return execute_trade("longeetDistrust", market_id)

# Sell trust on ethos
def sell_trust(market_id: int = AIXBT_MARKET_ID):
    return execute_trade("dumpeetTrust", market_id)

# Sell distrust on ethos
def sell_distrust(market_id: int = AIXBT_MARKET_ID):
    return execute_trade("dumpeetDistrust", market_id)

# Transfer seraph to another address
def transfer_seraph(to_address: str):
    try:
        tx = wallet.transfer(
            1,
            SERAPH_CONTRACT_ADDRESS,
            to_address
        )
        return tx
    except Exception as e:
        print(f"Error transferring SERAPH: {e}")
        return None

# External function to approve and execute rewards for stTAO and SERAPH
def approve_and_execute_rewards():
    # Approve stTAO
    sttao_approve_tx = execute_approve_sttao("approve", str(CONTRACT_ADDRESS_STAKING), wallet.balance(STTAO_CONTRACT_ADDRESS))
    if sttao_approve_tx is None:
        print("Failed to approve stTAO")
        return None

    # Approve SERAPH
    seraph_approve_tx = execute_approve_seraph("approve", str(CONTRACT_ADDRESS_STAKING), wallet.balance(SERAPH_CONTRACT_ADDRESS))
    if seraph_approve_tx is None:
        print("Failed to approve SERAPH")
        return None

    # Execute reward for stTAO
    rewardAmount = wallet.balance(STTAO_CONTRACT_ADDRESS)/10
    sttao_reward_tx = execute_reward("reward", str(STTAO_CONTRACT_ADDRESS), rewardAmount)
    if sttao_reward_tx is None:
        print("Failed to execute reward for stTAO")
        return None

    # Execute reward for SERAPH
    rewardAmount = wallet.balance(SERAPH_CONTRACT_ADDRESS)/10
    seraph_reward_tx = execute_reward("reward", str(SERAPH_CONTRACT_ADDRESS), rewardAmount)
    if seraph_reward_tx is None:
        print("Failed to execute reward for SERAPH")
        return None

    return {
        "sttao_approve_tx": sttao_approve_tx,
        "seraph_approve_tx": seraph_approve_tx,
        "sttao_reward_tx": sttao_reward_tx,
        "seraph_reward_tx": seraph_reward_tx
    }

# --- Functions for export ---
