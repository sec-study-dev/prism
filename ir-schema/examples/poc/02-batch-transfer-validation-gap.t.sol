// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// @dev Minimal ERC-20-like token with a batchTransfer that lacks aggregate
///      balance validation — illustrates the validation gap IR.
contract ExampleToken {
    mapping(address => uint256) public _balances;
    uint256 public totalSupply;

    function mint(address to, uint256 amount) external {
        _balances[to] += amount;
        totalSupply += amount;
    }

    /// @notice Transfers `amounts[i]` to `recipients[i]` for each i.
    ///         BUG: only checks per-iteration, not aggregate. With Solidity 0.8
    ///         unchecked-style semantics a balance underflow on the full sum is
    ///         caught, but the *ordering* still allows partial state:
    ///         if sender balance < sum(amounts) the tx reverts — demonstrating
    ///         the missing-require gap (no upfront aggregate check).
    function batchTransfer(address[] calldata recipients, uint256[] calldata amounts) external {
        require(recipients.length == amounts.length, "length mismatch");
        // Missing: require(_balances[msg.sender] >= totalAmount) upfront
        for (uint256 i = 0; i < recipients.length; i++) {
            require(_balances[msg.sender] >= amounts[i], "insufficient per-item");
            _balances[msg.sender] -= amounts[i];
            _balances[recipients[i]] += amounts[i];
        }
    }
}

contract BatchTransferValidationGapTest is Test {
    ExampleToken token;
    address constant SENDER = address(0xBEEF);
    address constant ALICE  = address(0xA11CE);
    address constant BOB    = address(0xB0B);

    function setUp() public {
        token = new ExampleToken();
        token.mint(SENDER, 100 ether);
    }

    /// Happy-path: aggregate amount <= balance
    function test_batchTransfer_validationGap() public {
        uint256 senderBefore = token._balances(SENDER);
        assertEq(senderBefore, 100 ether, "precondition: sender has 100 ether");

        address[] memory recipients = new address[](2);
        uint256[] memory amounts    = new uint256[](2);
        recipients[0] = ALICE; amounts[0] = 40 ether;
        recipients[1] = BOB;   amounts[1] = 30 ether;

        vm.prank(SENDER);
        token.batchTransfer(recipients, amounts);

        assertEq(token._balances(SENDER), 30 ether,  "sender balance decremented correctly");
        assertEq(token._balances(ALICE),  40 ether,  "alice received correct amount");
        assertEq(token._balances(BOB),    30 ether,  "bob received correct amount");

        // Invariant: total supply unchanged (no mint/burn during transfer)
        assertEq(token.totalSupply(), 100 ether, "totalSupply invariant held");
    }

    /// Demonstrates the gap: tx reverts mid-loop without upfront aggregate check.
    function test_batchTransfer_reverts_when_aggregate_exceeds_balance() public {
        address[] memory recipients = new address[](2);
        uint256[] memory amounts    = new uint256[](2);
        recipients[0] = ALICE; amounts[0] = 80 ether;
        recipients[1] = BOB;   amounts[1] = 80 ether; // total 160 > 100

        vm.prank(SENDER);
        vm.expectRevert("insufficient per-item");
        token.batchTransfer(recipients, amounts);
    }
}
