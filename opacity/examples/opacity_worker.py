from game_sdk.game.worker import Worker
from game_sdk.game.custom_types import (
    Function,
    Argument,
    FunctionResult,
    FunctionResultStatus
)
from typing import Dict, Optional, Tuple
import os
from dotenv import load_dotenv
import re
import requests
from opacity_game_sdk.opacity_plugin import OpacityPlugin
from twitter_plugin_gamesdk.twitter_plugin import TwitterPlugin
import sys
sys.path.append('/home/user/CoinbaseAI/ethos-trade-cdp/py')
from main import (
    buy_trust,
    sell_trust,
    buy_distrust,
    sell_distrust,
    transfer_seraph
)


class OpacityVerificationWorker:
    def __init__(self):
        self._initialize_environment()
        self._initialize_plugins()
        self._initialize_verified_agents()
        self.worker = self._create_worker()

    def _initialize_environment(self):
        """Initialize and validate environment variables."""
        load_dotenv()
        self.game_api_key = os.environ.get("GAME_API_KEY")

        if not self.game_api_key:
            raise ValueError("GAME_API_KEY not found in environment variables")

        required_twitter_creds = [
            "TWITTER_BEARER_TOKEN",
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET_KEY",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_TOKEN_SECRET",
            "TWITTER_CLIENT_KEY",
            "TWITTER_CLIENT_SECRET"
        ]

        missing_creds = [
            cred for cred in required_twitter_creds
            if not os.environ.get(cred)
        ]
        if missing_creds:
            raise ValueError(
                f"Missing Twitter credentials: {', '.join(missing_creds)}"
            )

    def _initialize_plugins(self):
        """Initialize Opacity and Twitter plugins."""
        self.opacity_plugin = OpacityPlugin()

        try:
            twitter_options = {
                "id": "opacity_twitter_plugin",
                "name": "Opacity Twitter Plugin",
                "description": "Twitter Plugin for Opacity verification.",
                "credentials": {
                    "bearerToken": os.environ["TWITTER_BEARER_TOKEN"],
                    "apiKey": os.environ["TWITTER_API_KEY"],
                    "apiSecretKey": os.environ["TWITTER_API_SECRET_KEY"],
                    "accessToken": os.environ["TWITTER_ACCESS_TOKEN"],
                    "accessTokenSecret": os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
                    "clientKey": os.environ["TWITTER_CLIENT_KEY"],
                    "clientSecret": os.environ["TWITTER_CLIENT_SECRET"],
                },
            }
            self.twitter_plugin = TwitterPlugin(twitter_options)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Twitter plugin: {str(e)}")

    def _initialize_verified_agents(self):
        """Initialize tracking of verified agents."""
        self.verified_agents_file = "verified_agents.txt"
        self.verified_agents = self._load_verified_agents()

    def _get_state(
        self,
        function_result: FunctionResult,
        current_state: dict
    ) -> dict:
        """Simple state management."""
        return {}

    def _load_verified_agents(self) -> set:
        """Load previously verified agents from file."""
        try:
            if os.path.exists(self.verified_agents_file):
                with open(self.verified_agents_file, 'r') as f:
                    return set(line.strip() for line in f)
            return set()
        except Exception as e:
            print(f"Error loading verified agents: {e}")
            return set()

    def _save_verified_agent(self, agent_id: str) -> bool:
        """Save newly verified agent to file. Returns True if agent was newly added."""
        try:
            if agent_id in self.verified_agents:
                return False
            with open(self.verified_agents_file, 'a') as f:
                f.write(f"{agent_id}\n")
            self.verified_agents.add(agent_id)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save verified agent: {e}")
            return False

    def _extract_wallet_address(self, tweet_text: str) -> Optional[str]:
        """Extract Ethereum wallet address from tweet text."""
        try:
            patterns = [
                r'wallet address:\s*(0x[a-fA-F0-9]{40})',
                r'address:\s*(0x[a-fA-F0-9]{40})',
                r'(0x[a-fA-F0-9]{40})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, tweet_text, re.IGNORECASE)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            print(f"Error extracting wallet address: {e}")
            return None

    def _get_tweet_data(self, tweet_id: str) -> Optional[Dict]:
        """Get tweet data with specified fields."""
        return self.twitter_plugin.twitter_client.get_tweet(
            tweet_id,
            tweet_fields=['conversation_id', 'referenced_tweets', 'text', 'author_id'],
            expansions=['referenced_tweets.id']
        )

    def _get_original_tweet(self, tweet_id: str) -> Optional[Dict]:
        """Get the original (root) tweet of a thread."""
        try:
            current_tweet = self._get_tweet_data(tweet_id)

            if not current_tweet or not current_tweet.data:
                raise ValueError(f"Tweet with ID {tweet_id} not found")

            referenced_tweets = getattr(current_tweet.data, 'referenced_tweets', None)
            if not referenced_tweets:
                return self._format_tweet_data(current_tweet.data)

            while referenced_tweets:
                parent_ref = next(
                    (ref for ref in referenced_tweets if ref.type == 'replied_to'),
                    None
                )
                if not parent_ref:
                    break

                current_tweet = self._get_tweet_data(str(parent_ref.id))
                if not current_tweet or not current_tweet.data:
                    break
                
                referenced_tweets = getattr(current_tweet.data, 'referenced_tweets', None)

            return self._format_tweet_data(current_tweet.data)

        except Exception as e:
            print(f"Error in _get_original_tweet: {e}")
            raise

    def _format_tweet_data(self, tweet_data) -> Dict:
        """Format tweet data into consistent structure."""
        return {
            'id': str(tweet_data.id),
            'text': tweet_data.text,
            'author_id': tweet_data.author_id
        }

    def _extract_proof_from_tweet(self, tweet_text: str) -> Optional[Dict]:
        """Extract proof ID from tweet text."""
        try:
            print(f"Attempting to extract proof from tweet text: {tweet_text}")
            proof_match = re.search(
                r'Proof ID:\s*(\S+)\s*$',
                tweet_text,
                re.IGNORECASE
            )
            if proof_match:
                proof_id = proof_match.group(1)
                print(f"Found proof ID: {proof_id}")
                return {"proof_id": proof_id}

            print("No proof ID found in tweet text")
            return None
        except Exception as e:
            print(f"Error extracting proof ID: {e}")
            return None

    def _handle_verification_response(
        self,
        verification_result: bool,
        proof_id: str,
        is_previously_verified: bool,
        wallet_address: Optional[str],
        original_tweet_id: str,
        reply_tweet_id: str,
        original_author_id: str
    ) -> Tuple[FunctionResultStatus, str, Dict]:
        """Handle verification result and post appropriate responses."""
        try:
            reply_tweet_fn = self.twitter_plugin.get_function('reply_tweet')
            base_reply_text = self._generate_reply_text(
                verification_result,
                proof_id,
                is_previously_verified,
                wallet_address
            )

            # Add mention of original author if replying to a different tweet
            if reply_tweet_id != original_tweet_id:
                reply_text = f"@{original_author_id} {base_reply_text}"
            else:
                reply_text = base_reply_text

            # Only reply to the incoming tweet
            reply_tweet_fn(reply_tweet_id, reply_text)

            return (
                FunctionResultStatus.DONE,
                "Proof verification completed and response posted",
                {
                    "valid": verification_result,
                    "original_tweet_id": original_tweet_id,
                    "proof_id": proof_id
                }
            )
        except Exception as e:
            print(f"Error posting verification reply: {str(e)}")
            return (
                FunctionResultStatus.FAILED,
                f"Error posting reply: {str(e)}",
                {}
            )

    def _generate_reply_text(
        self,
        verification_result: bool,
        proof_id: str,
        is_previously_verified: bool,
        wallet_address: Optional[str]
    ) -> str:
        """Generate appropriate reply text based on verification result."""
        def get_scan_url(tx):
            if tx and hasattr(tx, 'transaction_hash'):
                return f"https://basescan.org/tx/{tx.transaction_hash}"
            return None

        if verification_result:
            if not is_previously_verified:
                trust_tx = buy_trust()
                trust_url = get_scan_url(trust_tx)
                print(f"[TRUST] Bought trust: {trust_url}")
                
                base_message = f"[SUCCESS] First verification\n└─ Proof {proof_id}"
                if trust_url:
                    base_message += f"\n└─ Trust tx: {trust_url}"

                if wallet_address:
                    try:
                        seraph_tx = transfer_seraph(wallet_address)
                        seraph_url = get_scan_url(seraph_tx)
                        if seraph_url:
                            print(f"[SERAPH] Transferred to {wallet_address}: {seraph_url}")
                            return (
                                f"{base_message}\n"
                                f"└─ SERAPH: 1.0 → {wallet_address}\n"
                                f"└─ Transfer tx: {seraph_url}"
                            )
                    except Exception as e:
                        print(f"[ERROR] SERAPH transfer failed: {e}")
                        return f"{base_message}\n└─ [ERROR] SERAPH transfer failed"
                return f"{base_message}\n└─ [WARN] No wallet provided"
            else:
                trust_tx = buy_trust()
                trust_url = get_scan_url(trust_tx)
                print(f"[TRUST] Bought trust: {trust_url}")
                base_message = f"[SUCCESS] Reverification\n└─ Proof {proof_id}"
                if trust_url:
                    base_message += f"\n└─ Trust tx: {trust_url}"
                return base_message
        else:
            if not is_previously_verified:
                distrust_tx = buy_distrust()
                distrust_url = get_scan_url(distrust_tx)
                print(f"[DISTRUST] Bought distrust: {distrust_url}")
                base_message = f"[FAILED] Verification\n└─ Proof {proof_id}"
                if distrust_url:
                    base_message += f"\n└─ Distrust tx: {distrust_url}"
                return base_message
            else:
                trust_tx = sell_trust()
                trust_url = get_scan_url(trust_tx)
                print(f"[TRUST] Sold trust: {trust_url}")
                base_message = f"[FAILED] Verification\n└─ Proof {proof_id}"
                if trust_url:
                    base_message += f"\n└─ Trust sold tx: {trust_url}"
                return base_message
    
    def verify_tweet_thread(self, tweet_id: str) -> tuple:
        """Verify a proof from the original tweet in a thread."""
        try:
            if not tweet_id or not isinstance(tweet_id, str):
                return FunctionResultStatus.FAILED, "Invalid tweet ID provided", {}

            reply_tweet = self._get_tweet_data(tweet_id)
            if not reply_tweet or not reply_tweet.data:
                return FunctionResultStatus.FAILED, "Could not retrieve reply tweet", {}

            reply_text = reply_tweet.data.text
            wallet_address = self._extract_wallet_address(reply_text)

            try:
                original_tweet = self._get_original_tweet(tweet_id)
                if not original_tweet:
                    return FunctionResultStatus.FAILED, "Could not retrieve original tweet", {}
            except Exception as e:
                return FunctionResultStatus.FAILED, f"Error retrieving tweet: {str(e)}", {}

            original_tweet_author = original_tweet['author_id']
            # Check if author is already verified before proceeding
            is_previously_verified = str(original_tweet_author) in self.verified_agents
            print(f"[DEBUG] Author {original_tweet_author} verification status: {'verified' if is_previously_verified else 'not verified'}")
            print(f"[DEBUG] Current verified agents: {self.verified_agents}")

            try:
                author_data = self.twitter_plugin.twitter_client.get_user(id=original_tweet_author)
                author_username = author_data.data.username
            except Exception as e:
                print(f"Error getting author username: {e}")
                author_username = original_tweet_author

            proof_data = self._extract_proof_from_tweet(original_tweet['text'])
            if not proof_data:
                return (
                    FunctionResultStatus.FAILED,
                    "No proof ID found in the original tweet",
                    {"original_tweet_id": original_tweet['id']}
                )

            try:
                proof_id = proof_data["proof_id"]
                proof_response = requests.get(
                    f"{self.opacity_plugin.prover_url}/api/logs/{proof_id}"
                )
                if not proof_response.ok:
                    raise Exception(f"Failed to fetch proof data: {proof_response.text}")

                verification_result = self.opacity_plugin.verify_proof(
                    {"proof": proof_response.json()}
                )

                # Only save if verification successful and not previously verified
                if verification_result and not is_previously_verified:
                    self._save_verified_agent(str(original_tweet_author))

                return self._handle_verification_response(
                    verification_result,
                    proof_id,
                    is_previously_verified,
                    wallet_address,
                    original_tweet['id'],
                    tweet_id,
                    author_username
                )

            except Exception as e:
                error_msg = f"Error during proof verification: {str(e)}"
                print(f"Verification error details: {error_msg}")
                return (
                    FunctionResultStatus.FAILED,
                    error_msg,
                    {
                        "original_tweet_id": original_tweet['id'],
                        "proof_id": proof_data["proof_id"]
                    }
                )

        except Exception as e:
            error_msg = f"Unexpected error during verification: {str(e)}"
            print(error_msg)
            return FunctionResultStatus.FAILED, error_msg, {}

    def _create_worker(self) -> Worker:
        """Create worker with thread verification capability."""
        return Worker(
            api_key=self.game_api_key,
            description="Worker for verifying AI inference proofs using Opacity",
            instruction="Verify proofs in Twitter threads",
            get_state_fn=self._get_state,
            action_space=[
                Function(
                    fn_name="verify_tweet_thread",
                    fn_description="Verify a proof from the original tweet in a thread",
                    args=[
                        Argument(
                            name="tweet_id",
                            type="string",
                            description="ID of any tweet in the thread to verify"
                        )
                    ],
                    executable=self.verify_tweet_thread
                )
            ]
        )

    def run(self, tweet_id: str):
        """Run the worker on a single tweet thread."""
        self.worker.run(f"Verify tweet thread: {tweet_id}")


def main():
    worker = OpacityVerificationWorker()
    test_tweet_id = 1885775347679138028
    worker.run(test_tweet_id)


if __name__ == "__main__":
    main()