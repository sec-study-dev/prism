// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MissingValidation {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    uint256 public constant SUPPLY_CAP = 1_000_000e18;
    address public owner;

    function batchTransfer(address[] calldata recipients, uint256[] calldata amounts) external {
        require(recipients.length == amounts.length, "length mismatch");
        for (uint i = 0; i < recipients.length; i++) {
            balances[msg.sender] -= amounts[i];
            balances[recipients[i]] += amounts[i];
        }
    }

    function mint(address to, uint256 amount) external {
        balances[to] += amount;
        totalSupply += amount;
    }

    function setOwner(address newOwner) external {
        owner = newOwner;
    }

    function goodTransfer(address to, uint256 amount) external {
        require(to != address(0), "zero address");
        require(balances[msg.sender] >= amount, "insufficient");
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}
