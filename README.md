# Proof of Autonomy: Verifiable Inference for AI Agents

## 💡 Inspiration
Remember Amazon's "Just Walk Out" technology? Marketed as AI, it turned out to be powered by humans in India watching security feeds. As AI agents become more prevalent in finance and daily life, how do we separate real AI from clever marketing or outright scams? This challenge becomes especially critical when these agents influence markets or handle sensitive data.

## 🎯 What We Built

### 🏗 Infrastructure: Cross-Agent Universal Verification Layer
We transformed Opacity Network's single-agent proof system into a universal verification network:

1. **Enhanced Opacity Integration**
   - Extended Opacity's ElizaOS plugin from self-verification to cross-agent verification
   - Built first-ever proof sharing protocol on Opacity's zkTLS infrastructure (Actively Validated Service on EigenLayer)
   - Enabled any agent to verify proofs from any other agent
   - Approach can be extended to other verifiable inference solutions

2. **Framework-Agnostic Plugins**
   - ElizaOS agents: Full proof generation and verification capabilities
   - Virtuals agents: Proof verification (generation coming with open-source inference)
   - Ready-to-deploy adapters for Langchain, PydanticAI, Coinbase AgentKit
   - Simple one-line integration for any framework

### 💫 Application: Proof of Autonomy Trust System
Built the first decentralized AI reputation system using our verification layer:

1. **Live Verification Network**
   - [Seraph Agent](https://x.com/seraphagent/with_replies): Our Virtuals-based verifier that detects AI-generated images and validates proofs
   - [maybe_aixbt](https://x.com/maybe_aixbt): ElizaOS-based proof generator (inspired by aixbt)
   - [Live Reputation Dashboard](https://stream.seraphai.xyz/): Real-time trust scores and verification status

2. **Automated Trust Network**
   - Seraph actively monitors and verifies AI inference claims
   - Automated trust/distrust positions on Ethos Markets based on verification
   - Smart contract rewards for first-time verified agents:
     - 1.0 SERAPH token for initial verification
     - Trust position opened on Ethos Markets
     - Continuous trust strengthening for consistent valid proofs

3. **Verification Workflow**
   - Agents post proofs with their inference results
   - Seraph verifies proofs through Opacity's infrastructure
   - Valid proofs trigger trust positions and rewards
   - Invalid proofs trigger distrust positions and community alerts
   - All verification results permanently recorded on-chain

4. **Economic Incentives**
   - Rewards genuine AI behavior through SERAPH tokens
   - Creates market signals through Ethos trade positions
   - Penalizes deceptive practices through distrust mechanisms
   - Builds foundation for crowdsourced AI authenticity verification


## 🛠 Technical Implementation

- **Virtuals Proof Verifier Plugin**: [`https://github.com/BitMind-AI/game-python/commits/verifier`](virtuals/opacity/opacity_game_sdk/examples/opacity_agent.py) *
- **Virtuals Proof Verifier (Seraph)**: [`virtuals/opacity/opacity_game_sdk/examples/opacity_agent.py`](virtuals/opacity/opacity_game_sdk/examples/opacity_agent.py)
- **ElizaOS Opacity Generator and Verifier Actions**: [`https://github.com/SeraphAgent/bittensor/tree/opacity/packages/plugin-opacity`](https://github.com/SeraphAgent/bittensor/tree/opacity/packages/plugin-opacity) **
- **Proof of Autonomy Buying/Selling on Ethos Market (CDP, Base)**: [`ethos-market/`](./ethos-market/)

* PR to Virtuals G.A.M.E. SDK repo
** PR to ElizaOS repo

## 🎯 Target Tracks
- Coinbase Developer Platform (CDP), Base
- Virtuals Protocol

## 👥 Team
BitMind - Bittensor Subnet 34, Deepfake Detection Applications, Agentic AI (Seraph)

## 🔗 Links
- [Demo Video](#)
- [Presentation Deck](#)

## 🚀 Next Steps
- Explicit support for: 
    - more agent frameworks (Coinbase AgentKit, Langchain, PydanticAI, etc.)
    - additional Verifiable Inference methods
- Cross-chain verification capabilities
- Expanded reward mechanisms for verifiers