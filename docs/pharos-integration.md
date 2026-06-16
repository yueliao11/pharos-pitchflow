# Pharos On-chain Integration

## Smart Contracts

Located in `contracts/`:

- **`AgentVideoRegistry.sol`** — stores content hashes, agent/creator addresses, video URIs and metadata URIs.
- **`PaymentGate.sol`** — enables users to pay or tip Agents for specific content hashes.

## Deploy

1. Copy `.env.example` to `.env` in the project root and fill in your private key + Pharos testnet RPC.
2. Install dependencies and compile:

```bash
npm install
cp .env.example .env
# edit .env
npm run compile
npm run deploy:testnet
```

After deployment, Hardhat prints the contract addresses. Add them to `backend/.env`.

## Backend Configuration

Copy `backend/.env.example` to `backend/.env` and set:

```bash
PHAROS_RPC=https://testnet.pharosnetwork.xyz
PHAROS_CHAIN_ID=500
PHAROS_REGISTRY_ADDRESS=0x...
PHAROS_PAYMENT_ADDRESS=0x...
AGENT_ADDRESS=0x...          # The Agent wallet that produced the video
PRIVATE_KEY=0x...            # Deployer / Agent private key
```

With these set, `POST /skill/generate?register_onchain=true` will call `AgentVideoRegistry.registerVideo(...)` after the video is generated.

## Payment / Tipping Flow

1. Frontend connects to MetaMask.
2. User enters `PaymentGate` address, beneficiary `AGENT_ADDRESS`, and amount.
3. `PaymentGate.payForContent(agent, contentHash, "tip")` is called with native token value.
4. The Agent can later call `PaymentGate.withdraw()` to collect accumulated balance.

## Content Hash

The Skill computes `sha256(video.mp4)` and stores the first 32 bytes as `bytes32` on Pharos. Anyone can later verify that the downloaded file matches the on-chain hash.
