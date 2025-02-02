// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.26;

import { Test, console } from "forge-std/Test.sol";
import { EthosTrade } from "../src/EthosTrade.sol";

contract EthosTradeTest is Test {
    EthosTrade public ethos;

    address public MPC = makeAddr("MPC");

    function setUp() public {
        ethos = new EthosTrade();
    }

    function testAllowedSwitcheroo() public {
        assertEq(ethos.allowed(MPC), false);
        ethos.allowedSwitcheroo(MPC);
        assertEq(ethos.allowed(MPC), true);
    }
}
