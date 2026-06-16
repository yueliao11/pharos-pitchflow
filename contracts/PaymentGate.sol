// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PaymentGate
 * @notice Minimal on-chain payment / tipping layer for agent-generated videos.
 *         Users pay in native token (or any ERC-20 in a future version) to
 *         unlock / tip / reward an Agent for a specific content hash.
 */
contract PaymentGate {
    mapping(address => uint256) public balances;

    event PaymentReceived(
        address indexed payer,
        address indexed beneficiary,
        bytes32 indexed contentHash,
        uint256 amount,
        string reason
    );

    event Withdrawn(address indexed beneficiary, uint256 amount);

    /**
     * @notice Pay for a video or unlock gated content.
     * @param agent        Agent / creator address to receive the funds.
     * @param contentHash  Content hash being paid for.
     * @param reason       "purchase", "tip", "subscription", etc.
     */
    function payForContent(
        address agent,
        bytes32 contentHash,
        string memory reason
    ) external payable {
        require(msg.value > 0, "Payment must be > 0");
        require(agent != address(0), "Invalid beneficiary");

        balances[agent] += msg.value;

        emit PaymentReceived(msg.sender, agent, contentHash, msg.value, reason);
    }

    /**
     * @notice Convenience wrapper for tipping an Agent.
     */
    function tipAgent(address agent, bytes32 contentHash) external payable {
        this.payForContent{value: msg.value}(agent, contentHash, "tip");
    }

    /**
     * @notice Beneficiary withdraws accumulated balance.
     */
    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        balances[msg.sender] = 0;

        (bool sent, ) = payable(msg.sender).call{value: amount}("");
        require(sent, "Withdraw failed");

        emit Withdrawn(msg.sender, amount);
    }

    receive() external payable {
        revert("Use payForContent or tipAgent");
    }
}
