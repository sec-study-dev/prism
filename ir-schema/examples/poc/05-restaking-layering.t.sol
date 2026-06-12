// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// @dev Minimal mock illustrating LRT (Liquid Restaking Token) layering price
///      gap: LST exchange-rate is stale at LRT redemption time, causing the
///      redemption to underprice or overprice the underlying staked ETH.

contract MockLST {
    uint256 public exchangeRate; // LST shares -> staked ETH, 1e18 = 1:1
    mapping(address => uint256) public _balances;
    uint256 public totalSupply;

    constructor(uint256 initialRate) {
        exchangeRate = initialRate;
    }

    function mint(address to, uint256 amount) external {
        _balances[to] += amount;
        totalSupply += amount;
    }

    /// Simulate a keeper update that bumps the exchange rate (lazy update)
    function updateExchangeRate(uint256 newRate) external {
        exchangeRate = newRate;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(_balances[msg.sender] >= amount, "insufficient LST");
        _balances[msg.sender] -= amount;
        _balances[to] += amount;
        return true;
    }
}

contract ExampleLRT {
    MockLST public underlyingLST;
    uint256 public lrtExchangeRate; // LRT shares -> LST, 1e18 = 1:1
    mapping(address => uint256) public _balances; // LRT shares
    uint256 public totalSupply;

    constructor(MockLST lst, uint256 initialLRTRate) {
        underlyingLST = lst;
        lrtExchangeRate = initialLRTRate;
    }

    function mint(address to, uint256 amount) external {
        _balances[to] += amount;
        totalSupply += amount;
        // In a real LRT the vault also deposits LST; omitted for simplicity
    }

    /// Redeem LRT shares for LST using the CURRENT (potentially stale) LST rate
    function redeem(uint256 lrtShares) external returns (uint256 lstAmount) {
        require(_balances[msg.sender] >= lrtShares, "insufficient LRT");
        lstAmount = (lrtShares * lrtExchangeRate) / 1e18;
        _balances[msg.sender] -= lrtShares;
        totalSupply -= lrtShares;
        underlyingLST.transfer(msg.sender, lstAmount);
        // NOTE: redemption price is fixed at lstAmount of LST tokens.
        // Actual staked-ETH value depends on underlyingLST.exchangeRate()
        // which may be stale — that gap is what this PoC demonstrates.
    }
}

contract RestakingLayeringTest is Test {
    MockLST lst;
    ExampleLRT lrt;
    address constant USER     = address(0xC0DE);
    address constant KEEPER   = address(0xDEAD);

    function setUp() public {
        // LST: 1 LST share = 1.0 staked ETH initially
        lst = new MockLST(1e18);
        // LRT: 1 LRT share = 1.0 LST initially
        lrt = new ExampleLRT(lst, 1e18);

        // Fund the LRT vault with 1000 LST (simulating staked reserves)
        lst.mint(address(lrt), 1_000 ether);
        // Give USER 100 LRT shares
        lrt.mint(USER, 100 ether);
    }

    /// Demonstrates layering price gap:
    /// LST exchange rate rises (yield accrual) but LRT redemption uses stale
    /// LRT->LST rate, so USER receives correct LST tokens but their staked-ETH
    /// value is determined by the NOW-UPDATED LST rate.
    function test_lrt_redemption_layering_price_gap() public {
        // Precondition: LST rate is 1:1, LRT rate is 1:1
        assertEq(lst.exchangeRate(), 1e18,  "LST rate starts 1:1");
        assertEq(lrt.lrtExchangeRate(), 1e18, "LRT rate starts 1:1");

        uint256 lrtSharesBefore = lrt._balances(USER);
        assertEq(lrtSharesBefore, 100 ether, "USER has 100 LRT shares");

        // LST exchange rate updates (keeper posts new yield: 1 LST = 1.05 ETH)
        lst.updateExchangeRate(1.05e18);
        assertEq(lst.exchangeRate(), 1.05e18, "LST rate updated to 1.05");

        // USER redeems 100 LRT shares BEFORE lrt.lrtExchangeRate is updated
        // (simulating the lazy-update window)
        vm.prank(USER);
        uint256 lstReceived = lrt.redeem(100 ether);

        // LST received = 100 * lrtExchangeRate/1e18 = 100 LST (correct per LRT rate)
        assertEq(lstReceived, 100 ether, "USER receives 100 LST (LRT rate applied)");

        // Actual staked-ETH value at the UPDATED LST rate
        uint256 stakedEthValue = (lstReceived * lst.exchangeRate()) / 1e18;
        assertEq(stakedEthValue, 105 ether, "100 LST now worth 105 staked ETH");

        // LRT shares after = 0 (burned)
        assertEq(lrt._balances(USER), 0, "LRT shares fully redeemed");

        // Layering gap: staked-ETH value (105) > nominal LST face value (100)
        // In an adversarial scenario where lrtExchangeRate has NOT been bumped
        // to reflect the yield, a second depositor entering before keeper
        // update gets a stale share price — the price-gap is the invariant at risk.
        assertGt(stakedEthValue, lstReceived, "layering gap: staked-ETH value exceeds LST face value");
    }
}
