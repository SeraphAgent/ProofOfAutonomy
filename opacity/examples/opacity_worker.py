from game_sdk.game.worker import Worker
from game_sdk.game.custom_types import (
    Function,
    Argument,
    FunctionResult,
    FunctionResultStatus
)
from typing import Dict, Optional
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
        # Load environment variables
        load_dotenv()
        self.game_api_key = os.environ.get("GAME_API_KEY")

        if not self.game_api_key:
            raise ValueError("GAME_API_KEY not found in environment variables")

        # Required Twitter credentials
        required_twitter_creds = [
            "TWITTER_BEARER_TOKEN",
            "TWITTER_API_KEY",
            "TWITTER_API_SECRET_KEY",
            "TWITTER_ACCESS_TOKEN",
            "TWITTER_ACCESS_TOKEN_SECRET",
            "TWITTER_CLIENT_KEY",
            "TWITTER_CLIENT_SECRET"
        ]

        # Validate all Twitter credentials exist
        missing_creds = [
            cred for cred in required_twitter_creds
            if not os.environ.get(cred)
        ]
        if missing_creds:
            raise ValueError(
                f"Missing Twitter credentials: {', '.join(missing_creds)}"
            )

        self.opacity_plugin = OpacityPlugin()

        # Initialize Twitter plugin with error handling
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

            # Initialize verified agents tracking
            self.verified_agents_file = "verified_agents.txt"
            self.verified_agents = self._load_verified_agents()

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Twitter plugin: {str(e)}")

        self.worker = self._create_worker()

    def _get_state(
        self,
        function_result: FunctionResult,
        current_state: dict
    ) -> dict:
        """Simple state management"""
        return {}

    def _load_verified_agents(self) -> set:
        """Load previously verified agents from file"""
        try:
            if os.path.exists(self.verified_agents_file):
                with open(self.verified_agents_file, 'r') as f:
                    return set(line.strip() for line in f)
            return set()
        except Exception as e:
            print(f"Error loading verified agents: {e}")
            return set()

    def _save_verified_agent(self, agent_id: str):
        """Save newly verified agent to file"""
        try:
            with open(self.verified_agents_file, 'a') as f:
                f.write(f"{agent_id}\n")
            self.verified_agents.add(agent_id)
        except Exception as e:
            print(f"Error saving verified agent: {e}")

    def _extract_wallet_address(self, tweet_text: str) -> Optional[str]:
        """Extract Ethereum wallet address from tweet text"""
        try:
            # Look for wallet address with common prefixes
            patterns = [
                r'wallet address:\s*(0x[a-fA-F0-9]{40})',  # "wallet address: 0x..."
                r'address:\s*(0x[a-fA-F0-9]{40})',         # "address: 0x..."
                r'(0x[a-fA-F0-9]{40})'                     # just the address
            ]
            
            for pattern in patterns:
                match = re.search(pattern, tweet_text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"Error extracting wallet address: {e}")
            return None

    def _get_original_tweet(self, tweet_id: str) -> Optional[Dict]:
        """Get the original (root) tweet of a thread"""
        try:
            tweet_fields = [
                'conversation_id',
                'referenced_tweets',
                'text',
                'author_id'
            ]
            expansions = ['referenced_tweets.id']

            current_tweet = self.twitter_plugin.twitter_client.get_tweet(
                tweet_id,
                tweet_fields=tweet_fields,
                expansions=expansions
            )

            if not current_tweet or not current_tweet.data:
                raise ValueError(f"Tweet with ID {tweet_id} not found")

            # If this is the original tweet (no referenced tweets)
            referenced_tweets = getattr(current_tweet.data, 'referenced_tweets', None)
            if not referenced_tweets:
                return {
                    'id': str(current_tweet.data.id),
                    'text': current_tweet.data.text,
                    'author_id': current_tweet.data.author_id
                }

            # Follow the chain to find the original tweet
            while referenced_tweets:
                parent_ref = next(
                    (ref for ref in current_tweet.data.referenced_tweets
                     if ref.type == 'replied_to'),
                    None
                )

                if not parent_ref:
                    break

                current_tweet = self.twitter_plugin.twitter_client.get_tweet(
                    str(parent_ref.id),
                    tweet_fields=tweet_fields,
                    expansions=expansions
                )

                if not current_tweet or not current_tweet.data:
                    break
                
                referenced_tweets = getattr(current_tweet.data, 'referenced_tweets', None)

            return {
                'id': str(current_tweet.data.id),
                'text': current_tweet.data.text,
                'author_id': current_tweet.data.author_id
            }

        except Exception as e:
            print(f"Error in _get_original_tweet: {e}")
            raise

    def _extract_proof_from_tweet(self, tweet_text: str) -> Optional[Dict]:
        """Extract proof ID from tweet text"""
        try:
            print(f"Attempting to extract proof from tweet text: {tweet_text}")

            # Look for proof ID at the end of the tweet
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

    def verify_tweet_thread(self, tweet_id: str) -> tuple:
        """Verify a proof from the original tweet in a thread"""
        try:
            # Input validation
            if not tweet_id or not isinstance(tweet_id, str):
                return FunctionResultStatus.FAILED, "Invalid tweet ID provided", {}

            # Get the reply tweet first (the one with the wallet address)
            reply_tweet = self.twitter_plugin.twitter_client.get_tweet(
                tweet_id,
                tweet_fields=['text', 'author_id', 'referenced_tweets'],
                expansions=['referenced_tweets.id']
            )

            if not reply_tweet or not reply_tweet.data:
                return (
                    FunctionResultStatus.FAILED,
                    "Could not retrieve reply tweet",
                    {}
                )

            reply_text = reply_tweet.data.text
            print(f"Reply tweet text: {reply_text}")
            wallet_address = self._extract_wallet_address(reply_text)
            print(f"Extracted wallet address: {wallet_address}")

            # Get the original tweet
            try:
                original_tweet = self._get_original_tweet(tweet_id)
                if not original_tweet:
                    return (
                        FunctionResultStatus.FAILED,
                        "Could not retrieve original tweet",
                        {}
                    )
                print(f"Original tweet: {original_tweet}")

            except Exception as e:
                return (
                    FunctionResultStatus.FAILED,
                    f"Error retrieving tweet: {str(e)}",
                    {}
                )

            # Store both tweet IDs for replies
            reply_tweet_id = tweet_id
            original_tweet_id = original_tweet['id']

            # Get author ID directly from tweet data
            original_tweet_author = original_tweet['author_id']
            if not original_tweet_author:
                return (
                    FunctionResultStatus.FAILED,
                    "Could not determine tweet author",
                    {}
                )

            print(f"Original tweet author ID: {original_tweet_author}")  # Debug
            is_previously_verified = original_tweet_author in self.verified_agents
            print(f"Previously verified: {is_previously_verified}")  # Debug

            # Extract proof ID from original tweet
            try:
                proof_data = self._extract_proof_from_tweet(original_tweet['text'])
                if not proof_data:
                    return (
                        FunctionResultStatus.FAILED,
                        "No proof ID found in the original tweet",
                        {"original_tweet_id": original_tweet['id']}
                    )

            except Exception as e:
                return (
                    FunctionResultStatus.FAILED,
                    f"Error extracting proof data: {str(e)}",
                    {
                        "original_tweet_id": (
                            original_tweet['id'] if original_tweet else None
                        )
                    }
                )

            # Get the original tweet author's ID
            original_tweet_author = original_tweet['author_id']
            is_previously_verified = original_tweet_author in self.verified_agents

            # Extract wallet address from reply tweet if different from original
            wallet_address = None
            if reply_tweet_id != original_tweet_id:
                reply_tweet = self.twitter_plugin.twitter_client.get_tweet(
                    reply_tweet_id,
                    tweet_fields=['text']
                )
                if reply_tweet and reply_tweet.data:
                    print(f"Reply tweet text: {reply_tweet.data.text}")
                    wallet_address = self._extract_wallet_address(
                        reply_tweet.data.text
                    )
                    print(f"Extracted wallet address: {wallet_address}")

            # Verify the proof
            try:
                proof_id = proof_data["proof_id"]
                print(f"Attempting to verify proof ID: {proof_id}")

                # First, fetch the proof data using the ID
                try:
                    proof_response = requests.get(
                        f"{self.opacity_plugin.prover_url}/api/logs/{proof_id}"
                    )
                    if not proof_response.ok:
                        raise Exception(
                            f"Failed to fetch proof data: {proof_response.text}"
                        )
                    proof = proof_response.json()
                except Exception as e:
                    raise Exception(f"Error fetching proof data: {str(e)}")

                # Send the proof data directly
                verification_result = self.opacity_plugin.verify_proof(
                    {"proof": proof}
                )
                # Post replies before returning the result
                try:
                    reply_tweet_fn = self.twitter_plugin.get_function(
                        'reply_tweet'
                    )

                    # Handle different verification scenarios
                    if verification_result:
                        if not is_previously_verified:
                            # First-time verification with valid proof
                            buy_trust()
                            self._save_verified_agent(original_tweet_author)

                            if wallet_address:
                                try:
                                    transfer_seraph(wallet_address)
                                    reply_text = (
                                        f"✅ First-time verification successful! "
                                        f"The AI inference proof "
                                        f"(ID: {proof_id}) has been validated.\n"
                                        f"Bounty of 1 SERAPH transferred to "
                                        f"{wallet_address}"
                                    )
                                except Exception as e:
                                    reply_text = (
                                        f"✅ First-time verification successful! "
                                        f"The AI inference proof "
                                        f"(ID: {proof_id}) has been validated.\n"
                                        f"Failed to transfer SERAPH: {str(e)}"
                                    )
                            else:
                                reply_text = (
                                    f"✅ First-time verification successful! "
                                    f"The AI inference proof "
                                    f"(ID: {proof_id}) has been validated.\n"
                                    f"No wallet address provided for SERAPH bounty"
                                )
                        else:
                            # Previously verified agent with valid proof
                            buy_trust()
                            reply_text = (
                                f"✅ Proof verification successful! "
                                f"The AI inference proof "
                                f"(ID: {proof_id}) has been validated."
                            )
                    else:
                        # Invalid proof handling
                        if not is_previously_verified:
                            buy_distrust()
                        else:
                            sell_trust()
                        reply_text = (
                            f"❌ Proof verification failed. "
                            f"The provided proof (ID: {proof_id}) "
                            f"could not be validated."
                        )

                    # Reply to the original tweet
                    reply_tweet_fn(original_tweet_id, reply_text)

                    # If requesting tweet different from original, reply there too
                    if reply_tweet_id != original_tweet_id:
                        reply_text += "\n(Original proof found in parent tweet)"
                        reply_tweet_fn(reply_tweet_id, reply_text)

                except Exception as e:
                    print(f"Error posting verification replies: {str(e)}")
                    # Continue even if replies fail - return verification result

                # Return the final result
                return (
                    FunctionResultStatus.DONE,
                    "Proof verification completed and responses posted",
                    {
                        "valid": verification_result,
                        "original_tweet_id": original_tweet_id,
                        "proof_id": proof_id
                    }
                )

            except Exception as e:
                error_msg = f"Error during proof verification: {str(e)}"
                print(f"Verification error details: {error_msg}")
                return (
                    FunctionResultStatus.FAILED,
                    error_msg,
                    {
                        "original_tweet_id": original_tweet_id,
                        "proof_id": proof_data["proof_id"]
                    }
                )

        except Exception as e:
            error_msg = f"Unexpected error during verification: {str(e)}"
            print(error_msg)
            return FunctionResultStatus.FAILED, error_msg, {}

    def _create_worker(self) -> Worker:
        """Create worker with thread verification capability"""
        return Worker(
            api_key=self.game_api_key,
            description="Worker for verifying AI inference proofs using Opacity",
            instruction="Verify proofs in Twitter threads",
            get_state_fn=self._get_state,
            action_space=[
                Function(
                    fn_name="verify_tweet_thread",
                    fn_description=(
                        "Verify a proof from the original tweet in a thread"
                    ),
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
        """Run the worker on a single tweet thread"""
        self.worker.run(f"Verify tweet thread: {tweet_id}")


def main():
    # Example usage
    worker = OpacityVerificationWorker()

    # Test with a real tweet ID
    test_tweet_id = 1885775347679138028
    worker.run(test_tweet_id)


if __name__ == "__main__":
    main()