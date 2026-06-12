// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IOracle {
    function latestAnswer() external view returns (int256);
}

interface IExternalVault {
    function exchangeRate() external view returns (uint256);
}

contract Consumer {
    IOracle public oracle;
    IExternalVault public vault;
    uint256 public localState;

    function readPrice() external view returns (int256) {
        return oracle.latestAnswer();
    }

    function readRateAndCompute() external view returns (uint256) {
        return vault.exchangeRate() * 2;
    }

    function pureLocal() external view returns (uint256) {
        return localState;
    }
}
