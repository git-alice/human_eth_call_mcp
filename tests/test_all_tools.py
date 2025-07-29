#!/usr/bin/env python3
"""
Comprehensive Test for Human ETH Call MCP Server

This script tests all 8 available tools with real blockchain data:
1. getTokenBalance - USDC token balance
2. getTokenDetails - USDC token details
3. getContractABI - USDC contract ABI
4. getContractSourceCode - USDC contract source code
5. executeContractMethod - USDC decimals() method call
6. getContractCreation - USDC contract creation info
7. ethGetTransactionReceipt - Single transaction receipt details
8. ethGetTransactionReceipts - Multiple transaction receipts (up to 5)

Test Data:
- Network: Ethereum Mainnet (chainID: "1")
- Token: USDC (0xA0b86991c431C15C59c7a3C9bcf0d8A0B5c3f1E7)
- Address: Vitalik's address (0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045)
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from etherscan_mcp_server import EtherscanClient, BlockchainConfig


class MockContext:
    """Mock context for testing without MCP server"""
    
    async def info(self, message: str):
        print(f"ℹ️  {message}")
    
    async def error(self, message: str):
        print(f"❌ {message}")
    
    async def report_progress(self, current: int, total: int):
        percentage = (current / total) * 100
        print(f"📊 Progress: {percentage:.1f}% ({current}/{total})")


class HumanEthCallTester:
    """Comprehensive tester for all Human ETH Call MCP tools"""
    
    def __init__(self):
        self.client = None
        self.ctx = MockContext()
        
        # Test configuration - multiple chains
        self.test_configs = [
            {
                "chain_id": "1",  # Ethereum Mainnet
                "token_address": "0xA0b86991c431C15C59c7a3C9bcf0d8A0B5c3f1E7",  # USDC
                "user_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik
                "name": "Ethereum Mainnet"
            },
            {
                "chain_id": "137",  # Polygon
                "token_address": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC on Polygon
                "user_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik
                "name": "Polygon"
            },
            {
                "chain_id": "42161",  # Arbitrum
                "token_address": "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",  # USDC on Arbitrum
                "user_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # Vitalik
                "name": "Arbitrum"
            }
        ]
        
        # Test results
        self.results = {}
    
    async def setup(self):
        """Initialize the client"""
        print("🚀 Setting up Human ETH Call MCP tester...")
        self.client = EtherscanClient()
        print()
    
    async def test_chain(self, config: dict):
        """Test all tools for a specific chain configuration"""
        chain_id = config["chain_id"]
        token_address = config["token_address"]
        user_address = config["user_address"]
        chain_name = config["name"]
        
        print(f"🌐 Testing on {chain_name} (Chain ID: {chain_id})")
        await self.ctx.info(f"Token: USDC ({token_address})")
        await self.ctx.info(f"Address: {user_address}")
        print()
        
        # Test 1: Token Balance
        print("="*30)
        result = await self.test_get_token_balance(chain_id, token_address, user_address)
        self.results[f"{chain_name}_getTokenBalance"] = result
        
        # Test 2: Token Details
        print("="*30)
        result = await self.test_get_token_details(chain_id, token_address)
        self.results[f"{chain_name}_getTokenDetails"] = result
        
        # Test 3: Contract ABI
        print("="*30)
        result = await self.test_get_contract_abi(chain_id, token_address)
        self.results[f"{chain_name}_getContractABI"] = result
        
        # Test 4: Contract Source Code
        print("="*30)
        result = await self.test_get_contract_source_code(chain_id, token_address)
        self.results[f"{chain_name}_getContractSourceCode"] = result
        
        # Test 5: Execute Contract Method
        print("="*30)
        result = await self.test_execute_contract_method(chain_id, token_address)
        self.results[f"{chain_name}_executeContractMethod"] = result
        
        # Test 6: Contract Creation
        print("="*30)
        result = await self.test_get_contract_creation(chain_id, token_address)
        self.results[f"{chain_name}_getContractCreation"] = result
        
        # Test 7: Transaction Receipt (using a known transaction hash)
        print("="*30)
        result = await self.test_eth_get_transaction_receipt(chain_id)
        self.results[f"{chain_name}_ethGetTransactionReceipt"] = result
        
        # Test 8: Multiple Transaction Receipts
        print("="*30)
        result = await self.test_eth_get_transaction_receipts(chain_id)
        self.results[f"{chain_name}_ethGetTransactionReceipts"] = result
    
    async def test_get_token_balance(self, chain_id: str, token_address: str, user_address: str) -> Dict[str, Any]:
        """Test getTokenBalance tool"""
        print("🪙 Testing getTokenBalance...")
        await self.ctx.report_progress(10, 100)
        
        try:
            await self.ctx.report_progress(50, 100)
            result = await self.client.get_token_balance(chain_id, token_address, user_address)
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                balance = result.get('balance_formatted', 'N/A')
                await self.ctx.info(f"✅ Token balance: {balance} USDC")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_get_token_details(self, chain_id: str, token_address: str) -> Dict[str, Any]:
        """Test getTokenDetails tool"""
        print("📋 Testing getTokenDetails...")
        await self.ctx.report_progress(10, 100)
        
        try:
            await self.ctx.report_progress(50, 100)
            result = await self.client.get_token_details(chain_id, token_address)
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                token_info = result.get("token_details", {})
                name = token_info.get('name', 'Unknown')
                symbol = token_info.get('symbol', 'Unknown')
                decimals = token_info.get('decimals', 'Unknown')
                await self.ctx.info(f"✅ Token details: {name} ({symbol}) - {decimals} decimals")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_get_contract_abi(self, chain_id: str, token_address: str) -> Dict[str, Any]:
        """Test getContractABI tool"""
        print("📜 Testing getContractABI...")
        await self.ctx.report_progress(10, 100)
        
        try:
            await self.ctx.report_progress(50, 100)
            result = await self.client.get_contract_abi(chain_id, token_address)
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                abi = result.get("abi", "")
                if abi:
                    await self.ctx.info(f"✅ Contract ABI retrieved ({len(abi)} characters)")
                else:
                    await self.ctx.info("✅ Contract ABI retrieved (empty)")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_get_contract_source_code(self, chain_id: str, token_address: str) -> Dict[str, Any]:
        """Test getContractSourceCode tool"""
        print("📄 Testing getContractSourceCode...")
        await self.ctx.report_progress(10, 100)
        
        try:
            await self.ctx.report_progress(50, 100)
            result = await self.client.get_contract_source_code(chain_id, token_address)
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                source_code = result.get("source_code", "")
                if source_code:
                    await self.ctx.info(f"✅ Contract source code retrieved ({len(source_code)} characters)")
                else:
                    await self.ctx.info("✅ Contract source code retrieved (empty)")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_execute_contract_method(self, chain_id: str, token_address: str) -> Dict[str, Any]:
        """Test executeContractMethod tool"""
        print("⚡ Testing executeContractMethod...")
        await self.ctx.report_progress(10, 100)
        
        try:
            # USDC decimals() method ABI
            method_abi = '{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}'
            
            await self.ctx.report_progress(30, 100)
            result = await self.client.execute_contract_method(
                chain_id, 
                token_address, 
                method_abi, 
                ""  # No parameters for decimals()
            )
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                decoded_data = result.get("decodedData", "N/A")
                await self.ctx.info(f"✅ Contract method executed: decimals() = {decoded_data}")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_get_contract_creation(self, chain_id: str, token_address: str) -> Dict[str, Any]:
        """Test getContractCreation tool"""
        print("🏗️ Testing getContractCreation...")
        await self.ctx.report_progress(10, 100)
        
        try:
            await self.ctx.report_progress(50, 100)
            result = await self.client.get_contract_creation(chain_id, [token_address])
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                creation_info = result.get("creation_info", [])
                if creation_info:
                    creator = creation_info[0].get("contract_creator", "Unknown")
                    tx_hash = creation_info[0].get("tx_hash", "Unknown")
                    await self.ctx.info(f"✅ Contract creation info: Creator={creator[:10]}..., Tx={tx_hash[:10]}...")
                else:
                    await self.ctx.info("✅ Contract creation info retrieved (empty)")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_eth_get_transaction_receipt(self, chain_id: str) -> Dict[str, Any]:
        """Test ethGetTransactionReceipt tool"""
        print("🔗 Testing ethGetTransactionReceipt...")
        await self.ctx.report_progress(10, 100)
        
        try:
            # Example transaction hash for Ethereum Mainnet (replace with a real one if available)
            # For testing, you might need to run a small transaction on the network
            # or use a testnet transaction hash.
            # For now, using a placeholder.
            tx_hash = "0x1234567890123456789012345678901234567890123456789012345678901234"
            
            await self.ctx.report_progress(50, 100)
            result = await self.client.get_transaction_receipt(chain_id, tx_hash)
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                receipt = result.get("receipt", {})
                if receipt:
                    await self.ctx.info(f"✅ Transaction receipt retrieved for hash: {tx_hash[:10]}...")
                    await self.ctx.info(f"  Block Number: {receipt.get('blockNumber', 'N/A')}")
                    await self.ctx.info(f"  Transaction Hash: {receipt.get('transactionHash', 'N/A')}")
                    await self.ctx.info(f"  Status: {receipt.get('status', 'N/A')}")
                else:
                    await self.ctx.info(f"✅ No receipt found for hash: {tx_hash[:10]}...")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_eth_get_transaction_receipts(self, chain_id: str) -> Dict[str, Any]:
        """Test ethGetTransactionReceipts tool (multiple receipts)"""
        print("🔗🔗 Testing ethGetTransactionReceipts...")
        await self.ctx.report_progress(10, 100)
        
        try:
            # Example transaction hashes for testing (placeholders)
            # For real testing, use actual transaction hashes from the network
            tx_hashes = [
                "0x1234567890123456789012345678901234567890123456789012345678901234",
                "0x5678901234567890123456789012345678901234567890123456789012345678",
                "0x9012345678901234567890123456789012345678901234567890123456789012",
                "0x1111111111111111111111111111111111111111111111111111111111111111",
                "0x2222222222222222222222222222222222222222222222222222222222222222",
                "0x3333333333333333333333333333333333333333333333333333333333333333",
                "0x4444444444444444444444444444444444444444444444444444444444444444",
                "0x5555555555555555555555555555555555555555555555555555555555555555",
                "0x6666666666666666666666666666666666666666666666666666666666666666",
                "0x7777777777777777777777777777777777777777777777777777777777777777",
                "0x8888888888888888888888888888888888888888888888888888888888888888",
                "0x9999999999999999999999999999999999999999999999999999999999999999",
                "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "0xdddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
                "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                "0x0000000000000000000000000000000000000000000000000000000000000001",
                "0x0000000000000000000000000000000000000000000000000000000000000002"
            ]
            
            await self.ctx.report_progress(50, 100)
            result = await self.client.get_transaction_receipts(chain_id, tx_hashes)
            await self.ctx.report_progress(90, 100)
            
            if result["success"]:
                successful_count = result.get("successful_count", 0)
                total_requested = result.get("total_requested", 0)
                await self.ctx.info(f"✅ Multiple transaction receipts processed: {successful_count}/{total_requested} successful")
                
                receipts_info = result.get("receipts_info", [])
                for receipt_info in receipts_info[:5]:  # Show first 5 results
                    tx_hash = receipt_info.get("tx_hash", "Unknown")
                    success = receipt_info.get("success", False)
                    if success:
                        receipt = receipt_info.get("receipt", {})
                        await self.ctx.info(f"  {tx_hash[:10]}...: ✅ Receipt found")
                    else:
                        error = receipt_info.get("error", "Unknown error")
                        await self.ctx.info(f"  {tx_hash[:10]}...: ❌ {error}")
                
                errors = result.get("errors")
                if errors:
                    await self.ctx.info(f"Some receipts failed: {len(errors)} error(s)")
            else:
                await self.ctx.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
            await self.ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await self.ctx.error(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_all_tests(self):
        """Run all tests on multiple chains"""
        print("🎯 HUMAN ETH CALL MCP - MULTI-CHAIN TEST")
        print("=" * 50)
        
        await self.setup()
        
        # Test each chain configuration
        for i, config in enumerate(self.test_configs):
            if i > 0:
                print("\n" + "="*50)
                print("🔄 SWITCHING TO NEXT CHAIN")
                print("="*50)
            
            await self.test_chain(config)
        
        # Summary
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result.get("success", False))
        
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for tool_name, result in self.results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"  {tool_name}: {status}")
            if not result.get("success", False):
                error = result.get("error", "Unknown error")
                print(f"    Error: {error}")
        
        print("\n🎉 HUMAN ETH CALL MCP TEST COMPLETE!")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.close()


async def main():
    """Main test runner"""
    tester = HumanEthCallTester()
    
    try:
        await tester.run_all_tests()
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 