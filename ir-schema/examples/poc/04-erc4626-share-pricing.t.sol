// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// @dev Minimal ERC-4626-style vault illustrating the share-donation inflation
///      vector: donating assets between deposit and redeem shifts share pricing.
contract ERC4626Vault {
    mapping(address => uint256) public _balances; // shares
    uint256 public totalSupply;   // total shares
    uint256 public totalAssets;   // underlying asset balance

    function deposit(uint256 assets, address receiver) external returns (uint256 shares) {
        if (totalSupply == 0) {
            shares = assets; // 1:1 bootstrap
        } else {
            shares = (assets * totalSupply) / totalAssets;
        }
        require(shares > 0, "zero shares");
        totalAssets += assets;
        totalSupply += shares;
        _balances[receiver] += shares;
    }

    /// Donate assets directly (no share minting) — increases share price
    function donate(uint256 assets) external {
        totalAssets += assets;
    }

    function redeem(uint256 shares, address receiver, address owner) external returns (uint256 assets) {
        require(_balances[owner] >= shares, "insufficient shares");
        assets = (shares * totalAssets) / totalSupply;
        _balances[owner] -= shares;
        totalSupply -= shares;
        totalAssets -= assets;
        // In a real vault: transfer `assets` tokens to receiver
        // (omitted here; we only track accounting)
        (receiver); // silence unused warning
    }
}

contract ERC4626SharePricingTest is Test {
    ERC4626Vault vault;
    address constant ALICE   = address(0xA11CE);
    address constant BOB     = address(0xB0B);
    address constant ATTACKER = address(0xA77ACE);

    function setUp() public {
        vault = new ERC4626Vault();
    }

    /// Demonstrates share-donation inflation: attacker donates between
    /// Alice's deposit and her redemption, shifting share price.
    function test_erc4626_share_donation_inflation() public {
        // Alice deposits 1000 assets; gets 1000 shares (1:1 bootstrap)
        vm.prank(ALICE);
        uint256 aliceShares = vault.deposit(1_000 ether, ALICE);
        assertEq(aliceShares, 1_000 ether, "Alice gets 1000 shares");
        assertEq(vault.totalAssets(), 1_000 ether, "totalAssets = 1000");

        // Attacker donates 500 assets (inflates share price)
        vm.prank(ATTACKER);
        vault.donate(500 ether);
        assertEq(vault.totalAssets(), 1_500 ether, "totalAssets inflated to 1500");

        // Bob deposits 1000 assets AFTER donation — gets fewer shares due to inflation
        vm.prank(BOB);
        uint256 bobShares = vault.deposit(1_000 ether, BOB);
        // shares = 1000 * 1000 / 1500 = 666 (rounded down)
        assertLt(bobShares, aliceShares, "Bob gets fewer shares than Alice for same deposit");
        assertGt(bobShares, 0, "Bob gets non-zero shares");

        // Alice redeems: gets back more than 1000 due to donation (share price rose)
        vm.prank(ALICE);
        uint256 aliceAssets = vault.redeem(aliceShares, ALICE, ALICE);
        assertGt(aliceAssets, 1_000 ether, "Alice redeems more than deposited (donation profit)");
    }
}
