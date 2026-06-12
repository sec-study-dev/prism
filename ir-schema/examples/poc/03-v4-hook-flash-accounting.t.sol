// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

/// @dev Minimal mock of Uniswap v4 flash-accounting mechanics.
///      Illustrates that currencyDelta is an intra-lock running net,
///      NOT a settled balance — a hook that reads it as final is misled.

contract MockPoolManager {
    mapping(address => int256) public currencyDelta; // running net inside lock
    bool public locked;

    modifier onlyWhileLocked() {
        require(locked, "not locked");
        _;
    }

    function lock() external {
        locked = true;
    }

    function unlock() external {
        locked = false;
        // In real v4: require all deltas are settled before unlock
    }

    /// Simulate a swap contributing +delta to lock holder
    function addDelta(address account, int256 delta) external onlyWhileLocked {
        currencyDelta[account] += delta;
    }

    /// Simulate settling (paying/receiving currency)
    function settleDelta(address account, int256 amount) external onlyWhileLocked {
        currencyDelta[account] -= amount;
    }
}

contract ExampleHook {
    MockPoolManager public poolManager;
    int256 public snapshotDelta; // hook snapshots delta before settlement

    constructor(MockPoolManager pm) {
        poolManager = pm;
    }

    /// Hook callback called by PoolManager during a swap — reads currencyDelta
    /// before intra-lock settlement is complete (the vulnerability).
    function beforeSwap(address lockHolder) external {
        snapshotDelta = poolManager.currencyDelta(lockHolder);
    }
}

contract V4HookFlashAccountingTest is Test {
    MockPoolManager pm;
    ExampleHook hook;
    address constant LOCK_HOLDER = address(0x1337);

    function setUp() public {
        pm   = new MockPoolManager();
        hook = new ExampleHook(pm);
    }

    /// Demonstrates that a hook reading currencyDelta mid-lock sees an
    /// intermediate value, not the final settled balance.
    function test_hook_misreads_intra_lock_delta() public {
        // --- begin lock ---
        pm.lock();

        // Intra-lock: swap adds +100 to lock holder
        pm.addDelta(LOCK_HOLDER, 100);

        // Hook fires at beforeSwap, snapshots the running delta
        hook.beforeSwap(LOCK_HOLDER);
        int256 hookSnapshot = hook.snapshotDelta();
        assertEq(hookSnapshot, 100, "hook sees +100 at beforeSwap");

        // Further intra-lock operations add another +50 (e.g. donation)
        pm.addDelta(LOCK_HOLDER, 50);

        // Settlement: lock holder pays back 120 (net +30 after settle)
        pm.settleDelta(LOCK_HOLDER, 120);

        int256 finalDelta = pm.currencyDelta(LOCK_HOLDER);
        assertEq(finalDelta, 30, "final settled delta is +30");

        // Key assertion: hook snapshot (100) != final settled value (30)
        assertTrue(hookSnapshot != finalDelta, "hook snapshot differs from final delta");

        pm.unlock();
    }
}
