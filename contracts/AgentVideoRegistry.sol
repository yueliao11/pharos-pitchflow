// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentVideoRegistry
 * @notice On-chain provenance ledger for AI-Agent-generated video content.
 *         Any Agent / Skill can register a content hash + metadata URI so that
 *         the creation time, creator and agent are immutable and verifiable.
 */
contract AgentVideoRegistry {
    struct AgentVideo {
        address agent;
        address creator;
        string title;
        string videoURI;
        string metadataURI;
        bytes32 contentHash;
        uint256 createdAt;
    }

    AgentVideo[] public videos;

    // Quick lookup: contentHash -> videoId
    mapping(bytes32 => uint256) public videoIdByHash;

    // Duplicate prevention: contentHash -> registered?
    mapping(bytes32 => bool) public isRegistered;

    event VideoRegistered(
        uint256 indexed videoId,
        address indexed agent,
        address indexed creator,
        bytes32 contentHash,
        string videoURI,
        string metadataURI
    );

    /**
     * @param agent        The AI Agent address that produced the video.
     * @param title        Human-readable title.
     * @param videoURI     Off-chain URI of the video (IPFS / Arweave / CDN).
     * @param metadataURI  Off-chain URI of metadata.json.
     * @param contentHash  sha256(video) committed on-chain.
     */
    function registerVideo(
        address agent,
        string memory title,
        string memory videoURI,
        string memory metadataURI,
        bytes32 contentHash
    ) external returns (uint256 videoId) {
        require(contentHash != bytes32(0), "Empty content hash");
        require(!isRegistered[contentHash], "Content already registered");

        AgentVideo memory record = AgentVideo({
            agent: agent,
            creator: msg.sender,
            title: title,
            videoURI: videoURI,
            metadataURI: metadataURI,
            contentHash: contentHash,
            createdAt: block.timestamp
        });

        videos.push(record);
        videoId = videos.length - 1;
        videoIdByHash[contentHash] = videoId;
        isRegistered[contentHash] = true;

        emit VideoRegistered(
            videoId,
            agent,
            msg.sender,
            contentHash,
            videoURI,
            metadataURI
        );
    }

    function getVideo(uint256 videoId) external view returns (AgentVideo memory) {
        require(videoId < videos.length, "Video does not exist");
        return videos[videoId];
    }

    function getVideoCount() external view returns (uint256) {
        return videos.length;
    }
}
