from __future__ import annotations

from typing import Optional

from web3 import Web3

from app import config

REGISTRY_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "agent", "type": "address"},
            {"internalType": "string", "name": "title", "type": "string"},
            {"internalType": "string", "name": "videoURI", "type": "string"},
            {"internalType": "string", "name": "metadataURI", "type": "string"},
            {"internalType": "bytes32", "name": "contentHash", "type": "bytes32"},
        ],
        "name": "registerVideo",
        "outputs": [{"internalType": "uint256", "name": "videoId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "videoId", "type": "uint256"}],
        "name": "getVideo",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "agent", "type": "address"},
                    {"internalType": "address", "name": "creator", "type": "address"},
                    {"internalType": "string", "name": "title", "type": "string"},
                    {"internalType": "string", "name": "videoURI", "type": "string"},
                    {"internalType": "string", "name": "metadataURI", "type": "string"},
                    {"internalType": "bytes32", "name": "contentHash", "type": "bytes32"},
                    {"internalType": "uint256", "name": "createdAt", "type": "uint256"},
                ],
                "internalType": "struct AgentVideoRegistry.AgentVideo",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "videoId", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "agent", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "creator", "type": "address"},
            {"indexed": False, "internalType": "bytes32", "name": "contentHash", "type": "bytes32"},
            {"indexed": False, "internalType": "string", "name": "videoURI", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "metadataURI", "type": "string"},
        ],
        "name": "VideoRegistered",
        "type": "event",
    },
]

PAYMENT_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "agent", "type": "address"},
            {"internalType": "bytes32", "name": "contentHash", "type": "bytes32"},
            {"internalType": "string", "name": "reason", "type": "string"},
        ],
        "name": "payForContent",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    },
]


def _bytes32_from_hex(hex_str: str) -> bytes:
    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]
    return bytes.fromhex(hex_str).rjust(32, b"\x00")


def is_configured() -> bool:
    return bool(
        config.PHAROS_RPC
        and config.PHAROS_REGISTRY_ADDRESS
        and config.AGENT_ADDRESS
        and config.PRIVATE_KEY
    )


def register_video(
    title: str,
    video_uri: str,
    metadata_uri: str,
    content_hash_hex: str,
) -> Optional[str]:
    """Register content hash on Pharos. Returns tx hash or None."""
    if not is_configured():
        return None

    w3 = Web3(Web3.HTTPProvider(config.PHAROS_RPC))
    account = w3.eth.account.from_key(config.PRIVATE_KEY)

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(config.PHAROS_REGISTRY_ADDRESS),
        abi=REGISTRY_ABI,
    )

    content_hash_bytes = _bytes32_from_hex(content_hash_hex)

    tx = contract.functions.registerVideo(
        Web3.to_checksum_address(config.AGENT_ADDRESS),
        title,
        video_uri,
        metadata_uri,
        content_hash_bytes,
    ).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 500000,
        }
    )

    signed = w3.eth.account.sign_transaction(tx, config.PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()
