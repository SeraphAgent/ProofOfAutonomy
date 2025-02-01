// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.26;

import { Script, console } from "forge-std/Script.sol";
import { EthosTrade } from "../src/EthosTrade.sol";

contract EthosTradeScript is Script {
    EthosTrade public ethos;

    function setUp() public { }

    function run() public returns (EthosTrade) {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);
        ethos = new EthosTrade();
        vm.stopBroadcast();
        return ethos;
    }
}
