# Human ETH Call MCP Server

A focused MCP (Model Context Protocol) server for token operations and smart contract interactions with Etherscan API.

## 🚀 Quick Start

**Get your free Etherscan API key:**
- Visit: https://etherscan.io/apis
- Create account and get API key

## 🎯 Installation Methods

### For Cursor IDE

Choose one of the following methods to add the MCP server to Cursor:

#### Method 1: Docker (Recommended)
Add to your `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "human-eth-call": {
      "command": "docker",
      "args": [
        "run","--rm","-i",
        "-e","ETHERSCAN_API_KEY",
        "ghcr.io/git-alice/human_eth_call_mcp:0.2.0"
      ],
      "env": {
        "ETHERSCAN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Method 2: UVX (Python package manager)
Add to your `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "human-eth-call": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/git-alice/human_eth_call_mcp.git@v0.2.0",
        "human-eth-call-mcp"
      ],
      "env": {
        "ETHERSCAN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Method 3: Local Installation
```bash
git clone https://github.com/git-alice/human_eth_call_mcp.git
cd human_eth_call_mcp
bash scripts/cursor-install-mcp.sh
```

## 🔧 Available Tools

1. **getTokenBalance** - Get token balance for any address
2. **getTokenDetails** - Get comprehensive token information (name, symbol, decimals, total supply)
3. **getContractABI** - Get contract ABI for verified contracts
4. **getContractSourceCode** - Get contract source code
5. **executeContractMethod** - Execute contract methods with auto encoding/decoding
6. **getContractCreation** - Get contract deployer address and creation transaction hash (up to 5 contracts)
7. **ethGetTransactionReceipt** - Get single transaction receipt with status, gas usage, and logs
8. **ethGetTransactionReceipts** - Get multiple transaction receipts (up to 20 transactions) with status, gas usage, and logs
9. **getEventLogs** - Get event logs with topic filtering (supports event signatures and hex topics, returns recent examples)
10. **getTimestampByBlockNumber** - Get UNIX timestamp for a block number

