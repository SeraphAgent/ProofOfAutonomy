//SPDX-License-Identifier: MIT

pragma solidity ^0.8.26;

import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";

interface IEthosMarket {
    /**
     * @notice Buy trust or distrust votes for a market
     * @dev Protocol fees and donations are taken from the payment amount.
     *      Excess ETH is refunded to the buyer.
     * @param profileId The ID of the market to buy votes in
     * @param isPositive True to buy trust votes, false to buy distrust votes
     * @param maxVotesToBuy Maximum number of votes to buy with the provided ETH
     * @param minVotesToBuy Minimum acceptable number of votes (protects against slippage)
     * @notice payable - Send ETH to cover vote cost plus fees
     */
    function buyVotes(
        uint256 profileId,
        bool isPositive,
        uint256 maxVotesToBuy,
        uint256 minVotesToBuy
    )
        external
        payable;

    /**
     * @notice Sell trust or distrust votes from a market
     * @dev Protocol fees are taken from the sale proceeds.
     *      Proceeds are sent to the seller after fees.
     * @param profileId The ID of the market to sell votes in
     * @param isPositive True to sell trust votes, false to sell distrust votes
     * @param votesToSell Number of votes to sell
     * @param minimumVotePrice Minimum acceptable price per vote (protects against slippage)
     */
    function sellVotes(uint256 profileId, bool isPositive, uint256 votesToSell, uint256 minimumVotePrice) external;

    /**
     * @notice Calculates the current odds for a market position and converts them to a price using the market's base
     * price
     * @param profileId The profile ID of the market
     * @param isPositive Whether to get trust (true) or distrust (false) odds
     * @return The odds converted to a price in wei (odds * basePrice)
     */
    function getVotePrice(uint256 profileId, bool isPositive) external view returns (uint256);

    /**
     * @notice Simulates buying votes to preview costs and fees without executing the trade
     * @param profileId The profile ID of the market
     * @param isPositive True for trust votes, false for distrust votes
     * @param votesToBuy Number of votes to simulate buying
     * @return purchaseCostBeforeFees The base cost of votes before fees
     * @return protocolFee Protocol fee amount
     * @return donation Donation amount for market creator
     * @return totalCostIncludingFees Total cost including all fees
     * @return newVotePrice The new vote price after simulation
     */
    function simulateBuy(
        uint256 profileId,
        bool isPositive,
        uint256 votesToBuy
    )
        external
        view
        returns (
            uint256 purchaseCostBeforeFees,
            uint256 protocolFee,
            uint256 donation,
            uint256 totalCostIncludingFees,
            uint256 newVotePrice
        );

    /**
     * @notice Simulates selling votes to preview proceeds and fees without executing the trade
     * @param profileId The profile ID of the market
     * @param isPositive True for trust votes, false for distrust votes
     * @param votesToSell Number of votes to simulate selling
     * @return proceedsBeforeFees The base proceeds before fees
     * @return protocolFee Protocol fee amount
     * @return proceedsAfterFees Net proceeds after fees
     * @return newVotePrice The new vote price after simulation
     */
    function simulateSell(
        uint256 profileId,
        bool isPositive,
        uint256 votesToSell
    )
        external
        view
        returns (uint256 proceedsBeforeFees, uint256 protocolFee, uint256 proceedsAfterFees, uint256 newVotePrice);
}

contract EthosTrade is Ownable {
    IEthosMarket immutable ethos = IEthosMarket(0xC26F339F4E46C776853b1c190eC17173DBe059Bf);

    mapping(address => bool) public allowed;

    address public immutable MPC = 0xe2F3B3129b33A535f1Bf9c8EDaC50D3BdeE420Cc; //CDP

    event AyeHeresOneDistrustForYou(uint256 indexed marketId);
    event AyeHeresOneTrustForYou(uint256 indexed marketId);
    event BogdanoffDampitTrust(uint256 indexed marketId);
    event BogdanoffDampitDistrust(uint256 indexed marketId);

    constructor() Ownable(msg.sender) {
        allowed[msg.sender] = true;
        allowed[MPC] = true;
    }

    receive() external payable { }

    function longeetTrust(uint256 _marketId) external {
        require(allowed[msg.sender], "Not allowed");
        (,,, uint256 price,) = ethos.simulateBuy(_marketId, true, 1);
        ethos.buyVotes{ value: price }(_marketId, true, 1, 1);
        emit AyeHeresOneTrustForYou(_marketId);
    }

    function longeetDistrust(uint256 _marketId) external {
        require(allowed[msg.sender], "Not allowed");
        (,,, uint256 price,) = ethos.simulateBuy(_marketId, false, 1);
        ethos.buyVotes{ value: price }(_marketId, false, 1, 1);
        emit AyeHeresOneDistrustForYou(_marketId);
    }

    function dumpeetTrust(uint256 _marketId) external {
        require(allowed[msg.sender], "Not allowed");
        (,,, uint256 proceeds) = ethos.simulateSell(_marketId, true, 1);
        ethos.sellVotes(_marketId, true, 1, proceeds);
        emit BogdanoffDampitTrust(_marketId);
    }

    function dumpeetDistrust(uint256 _marketId) external {
        require(allowed[msg.sender], "Not allowed");
        (,,, uint256 proceeds) = ethos.simulateSell(_marketId, false, 1);
        ethos.sellVotes(_marketId, false, 1, proceeds);
        emit BogdanoffDampitDistrust(_marketId);
    }

    function allowedSwitcheroo(address _address) external {
        require(allowed[msg.sender], "Not allowed");
        allowed[_address] = !allowed[_address];
    }

    function recoverETH() external onlyOwner {
        (bool success,) = (msg.sender).call{ value: address(this).balance }("");
        require(success, "ETH transfer failed");
    }
}
