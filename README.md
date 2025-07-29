# Human ETH Call MCP Server

[![asciicast](https://asciinema.org/a/rcqanivzNeegQkYm8VFImiucd.svg)](https://asciinema.org/a/rcqanivzNeegQkYm8VFImiucd)

A focused MCP (Model Context Protocol) server for token operations and smart contract interactions with Etherscan API.

## 🚀 Quick Start

### For Cursor IDE

1. **Get your free Etherscan API key:**
   - Visit: https://etherscan.io/apis
   - Create account and get API key

2. **Set environment variable:**
```bash
export ETHERSCAN_API_KEY=your_api_key_here
```

3. **Clone and install:**
```bash
git clone https://github.com/git-alice/human_eth_call_mcp.git
cd human_eth_call_mcp
bash scripts/cursor-install-mcp.sh
```

4. **Ready to use!** 🎉

**Note:** The API key is also stored in `~/.cursor/mcp.json` for Cursor IDE integration.


## ✨ Features

- **8 Essential Tools**: Token balance, details, ABI, source code, method execution, contract creation info, and transaction receipts (single & batch)
- **Universal Chain Support**: All EVM-compatible blockchains via API v2
- **Automatic ABI Encoding/Decoding**: Seamless contract interactions
- **Batch Operations**: Get multiple contract creation info and transaction receipts in one call

## 🔧 Available Tools

1. **getTokenBalance** - Get token balance for any address
2. **getTokenDetails** - Get comprehensive token information (name, symbol, decimals, total supply)
3. **getContractABI** - Get contract ABI for verified contracts
4. **getContractSourceCode** - Get contract source code
5. **executeContractMethod** - Execute contract methods with auto encoding/decoding
6. **getContractCreation** - Get contract deployer address and creation transaction hash (up to 5 contracts)
7. **ethGetTransactionReceipt** - Get single transaction receipt with status, gas usage, and logs
8. **ethGetTransactionReceipts** - Get multiple transaction receipts (up to 5 transactions) with status, gas usage, and logs

## 📝 Configuration

Set environment variable:
```bash
export ETHERSCAN_API_KEY=your_api_key_here
```

Or create `.env` file:
```env
ETHERSCAN_API_KEY=your_api_key_here
```

## 🧪 Testing

```bash
uv run python tests/test_all_tools.py
```

## 📄 License

MIT License

---

**Made with ❤️ for the Web3 community** 