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
ABI_PATH = "../abis/ethos-trade-abi.json"
CONTRACT_ADDRESS = "0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60"

# Ethos market
AIXBT_MARKET_ID = 898

# SERAPH
SERAPH_CONTRACT_ADDRESS = "0x4f81837C2f4A189A0B69370027cc2627d93785B4"

# Validate environment variables
if not all([CDP_API_KEY, CDP_API_KEY_SECRET, MNEMONIC_PHRASE]):
    raise ValueError("Missing required environment variables.")

# Initialize CDP API
Cdp.configure(CDP_API_KEY, CDP_API_KEY_SECRET)

# Initialize Wallet
wallet = Wallet.import_wallet(
    MnemonicSeedPhrase(MNEMONIC_PHRASE), network_id="base-mainnet"
)

# Load contract ABI
try:
    with open(ABI_PATH, "r") as file:
        abi = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"ABI file not found at {ABI_PATH}")
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
            contract_address=CONTRACT_ADDRESS,
            abi=abi,
            method=method,
            args={"_marketId": str(market_id)}
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

# --- Functions for export ---
