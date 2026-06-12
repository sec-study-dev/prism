// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Vault {
    uint256 public totalSupply;
    address public assetToken;

    function totalAssets() public view returns (uint256) {
        return IERC20(assetToken).balanceOf(address(this));
    }

    function convertToShares(uint256 assets) public view returns (uint256) {
        uint256 supply = totalSupply;
        uint256 ta = totalAssets();
        return supply == 0 ? assets : assets * supply / ta;
    }

    function convertToAssets(uint256 shares) public view returns (uint256) {
        uint256 supply = totalSupply;
        return supply == 0 ? shares : shares * totalAssets() / supply;
    }

    function plainTransfer(address to, uint256 amount) external {
    }
}

interface IERC20 {
    function balanceOf(address) external view returns (uint256);
}
