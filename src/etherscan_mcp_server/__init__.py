"""
Human ETH Call MCP Server

A focused MCP (Model Context Protocol) server for token operations and smart contract interactions.
Provides essential tools for blockchain data access via Etherscan API.
"""

__version__ = "1.0.0"
__author__ = "Human ETH Call MCP Team"
__email__ = "art.oxbow@gmail.com"

from .client import EtherscanClient, BlockchainConfig
from .server import main

__all__ = ["EtherscanClient", "BlockchainConfig", "main"] 