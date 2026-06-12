"""Tests for PoC trivial-pass sanity check (spec §8 rules 1-4)."""
import pytest
from pipeline.stage1.poc.sanity import SanityChecker, SanityFailure


@pytest.fixture
def checker():
    return SanityChecker()


def test_rejects_assertTrue_only(checker):
    src = """
    function test_x() public {
        assertTrue(true);
    }
    """
    with pytest.raises(SanityFailure, match="trivial"):
        checker.check(src, mechanism_tags=["function-callable"], state_writes=["x"])


def test_rejects_no_state_change_assertion(checker):
    src = """
    function test_x() public {
        uint256 a = readView();
        assertEq(a, a);
    }
    """
    with pytest.raises(SanityFailure):
        checker.check(src, mechanism_tags=["function-callable"], state_writes=["x"])


def test_accepts_state_write_check(checker):
    src = """
    function test_x() public {
        uint256 before = vault.userBalance(attacker);
        vault.deposit(100);
        uint256 after_ = vault.userBalance(attacker);
        assertGt(after_, before);
    }
    """
    checker.check(src, mechanism_tags=["function-callable"], state_writes=["userBalance"])


def test_attackable_class_requires_profit_or_harm(checker):
    src = """
    function test_x() public {
        vault.someCall();
        assertEq(vault.flag(), true);
    }
    """
    with pytest.raises(SanityFailure, match="profit or harm"):
        checker.check(src, mechanism_tags=["validation-gap"], state_writes=["flag"])


def test_attackable_class_passes_with_profit_assertion(checker):
    src = """
    function test_x() public {
        uint256 before = token.balanceOf(ATTACKER);
        vault.exploit();
        uint256 after_ = token.balanceOf(ATTACKER);
        assertGt(after_, before);
    }
    """
    checker.check(src, mechanism_tags=["validation-gap"], state_writes=["balances"])
