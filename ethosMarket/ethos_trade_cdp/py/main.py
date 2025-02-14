import os
import json
from cdp import Cdp, Wallet, MnemonicSeedPhrase
from dotenv import load_dotenv

# --- Configuration & Setup ---

# Load environment variables
load_dotenv()

CDP_API_KEY = os.getenv("CDP_API_KEY")
CDP_API_KEY_SECRET = os.getenv("CDP_API_KEY_SECRET")
MNEMONIC_PHRASE = os.getenv("MNEMONIC_PHRASE")

# Contract Addresses
CONTRACT_ADDRESS_ETHOS = "0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60"
CONTRACT_ADDRESS_STAKING = "0xD4b47EE9879470179bAC7BECf49d2755ce5a8ea0"
SERAPH_CONTRACT_ADDRESS = "0x4f81837C2f4A189A0B69370027cc2627d93785B4"
STTAO_CONTRACT_ADDRESS = "0x806041B6473DA60abbe1b256d9A2749A151be6C6"

# Contract ABI Paths
ABI_PATH_ETHOS = "../abis/ethos-trade-abi.json"
ABI_PATH_STAKING = "../abis/seraph-staking-abi.json"
ABI_PATH_SERAPH = "../abis/seraph-abi.json"
ABI_PATH_STTAO = "../abis/sttao-abi.json"

# Ethos Market ID
AIXBT_MARKET_ID = 898


# --- Initialization ---

# Validate environment variables
if not all([CDP_API_KEY, CDP_API_KEY_SECRET, MNEMONIC_PHRASE]):
    raise ValueError("Missing required environment variables.")

# Initialize CDP API
Cdp.configure(CDP_API_KEY, CDP_API_KEY_SECRET)

# Initialize Wallet
wallet = Wallet.import_wallet(
    MnemonicSeedPhrase(MNEMONIC_PHRASE), network_id="base-mainnet"
)


def load_abi(abi_path: str) -> dict:
    """Loads a contract ABI from a JSON file."""
    try:
        with open(abi_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"ABI file not found at {abi_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding ABI JSON file at {abi_path}")


# Load ABIs
abi_ethos = load_abi(ABI_PATH_ETHOS)
abi_staking = load_abi(ABI_PATH_STAKING)
abi_seraph = load_abi(ABI_PATH_SERAPH)
abi_sttao = load_abi(ABI_PATH_STTAO)



# --- Helper Functions ---

def execute_contract_method(
    contract_address: str, abi: dict, method: str, args: dict
):
    """Executes a contract method using the CDP wallet."""
    try:
        invocation = wallet.invoke_contract(
            contract_address=contract_address, abi=abi, method=method, args=args
        )
        tx = invocation.wait()
        return tx
    except Exception as e:
        print(f"Error executing {method}: {e}")
        return None

# --- Contract Specific Functions ---

def execute_trade(method: str, market_id: int):
    """Executes a trade on the Ethos contract."""
    args = {"_marketId": str(market_id)}
    return execute_contract_method(CONTRACT_ADDRESS_ETHOS, abi_ethos, method, args)


def execute_reward(method: str, rewardToken: str, rewardAmount: int):
    """Executes a reward function on the Staking contract."""
    args = {"_rewardToken": str(rewardToken), "_rewardAmount": str(rewardAmount)}
    return execute_contract_method(CONTRACT_ADDRESS_STAKING, abi_staking, method, args)


def execute_approve_sttao(method: str, spender: str, amount: int):
    """Executes an approve function on the stTAO contract."""
    args = {"spender": spender, "amount": str(amount)}
    return execute_contract_method(STTAO_CONTRACT_ADDRESS, abi_sttao, method, args)


def execute_approve_seraph(method: str, spender: str, amount: int):
    """Executes an approve function on the SERAPH contract."""
    args = {"spender": spender, "amount": str(amount)}
    return execute_contract_method(SERAPH_CONTRACT_ADDRESS, abi_seraph, method, args)


# --- Public API Functions ---

def get_wallet_address():
    """Returns the default wallet address."""
    return wallet.default_address.address_id


def buy_trust(market_id: int = AIXBT_MARKET_ID):
    """Buys trust on the Ethos market."""
    return execute_trade("longeetTrust", market_id)


def buy_distrust(market_id: int = AIXBT_MARKET_ID):
    """Buys distrust on the Ethos market."""
    return execute_trade("longeetDistrust", market_id)


def sell_trust(market_id: int = AIXBT_MARKET_ID):
    """Sells trust on the Ethos market."""
    return execute_trade("dumpeetTrust", market_id)


def sell_distrust(market_id: int = AIXBT_MARKET_ID):
    """Sells distrust on the Ethos market."""
    return execute_trade("dumpeetDistrust", market_id)

def transfer_seraph(to_address: str):
    """Transfers 1 SERAPH token to the specified address."""
    try:
        tx = wallet.transfer(1, SERAPH_CONTRACT_ADDRESS, to_address)
        return tx
    except Exception as e:
        print(f"Error transferring SERAPH: {e}")
        return None


def approve_and_execute_rewards():
    """Approves and executes rewards for stTAO and SERAPH."""

    # Approve stTAO
    sttao_balance = wallet.balance(STTAO_CONTRACT_ADDRESS)
    sttao_approve_tx = execute_approve_sttao(
        "approve", str(CONTRACT_ADDRESS_STAKING), sttao_balance
    )
    if sttao_approve_tx is None:
        print("Failed to approve stTAO")
        return None

    # Approve SERAPH
    seraph_balance = wallet.balance(SERAPH_CONTRACT_ADDRESS)
    seraph_approve_tx = execute_approve_seraph(
        "approve", str(CONTRACT_ADDRESS_STAKING), seraph_balance
    )
    if seraph_approve_tx is None:
        print("Failed to approve SERAPH")
        return None

    # Execute reward for stTAO
    rewardAmount_sttao = sttao_balance // 10
    sttao_reward_tx = execute_reward(
        "reward", str(STTAO_CONTRACT_ADDRESS), rewardAmount_sttao
    )
    if sttao_reward_tx is None:
        print("Failed to execute reward for stTAO")
        return None

    # Execute reward for SERAPH
    rewardAmount_seraph = seraph_balance // 10
    seraph_reward_tx = execute_reward(
        "reward", str(SERAPH_CONTRACT_ADDRESS), rewardAmount_seraph
    )
    if seraph_reward_tx is None:
        print("Failed to execute reward for SERAPH")
        return None

    return {
        "sttao_approve_tx": sttao_approve_tx,
        "seraph_approve_tx": seraph_approve_tx,
        "sttao_reward_tx": sttao_reward_tx,
        "seraph_reward_tx": seraph_reward_tx,
    }