// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

contract ExampleVault {
    mapping(address => uint256) public userDeposits;
    mapping(address => uint256) public healthFactor;

    function setDeposit(address u, uint256 amount) external {
        userDeposits[u] = amount;
        healthFactor[u] = 2e18;
    }

    function emergencyWithdraw() external returns (uint256 mintedLP) {
        require(healthFactor[msg.sender] >= 1e18, "low HF");
        mintedLP = userDeposits[msg.sender];
        userDeposits[msg.sender] = 0;
    }
}

contract EmergencyWithdrawChainTest is Test {
    ExampleVault vault;
    address constant ATTACKER = address(0xA77ACE);

    function setUp() public {
        vault = new ExampleVault();
        vault.setDeposit(ATTACKER, 1_000 ether);
    }

    function test_emergencyWithdraw_chain() public {
        uint256 depositBefore = vault.userDeposits(ATTACKER);
        assertGt(depositBefore, 0, "precondition: deposit exists");

        vm.startPrank(ATTACKER);
        uint256 minted = vault.emergencyWithdraw();
        vm.stopPrank();

        uint256 depositAfter = vault.userDeposits(ATTACKER);
        assertEq(depositAfter, 0, "deposit zeroed");
        assertEq(minted, depositBefore, "LP minted equals deposit");
    }
}
