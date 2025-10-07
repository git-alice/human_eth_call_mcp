#!/usr/bin/env python3
"""
Etherscan MCP Server

A focused MCP (Model Context Protocol) server for interacting with Etherscan API.
Provides tools for token operations and smart contract interactions.

Features:
- Token balance and details retrieval
- Smart contract ABI and source code access
- Contract creation information (deployer address and creation tx hash) - supports up to 5 contracts
- Contract method execution with automatic ABI encoding/decoding
- Transaction receipt information with status, gas usage, and logs
- Batch transaction receipts retrieval - supports up to 5 transactions
- Event logs retrieval with topic filtering (supports event signatures and hex topics)
- Block timestamp retrieval for any block number
- Multi-chain support (Ethereum, BSC, Polygon, Arbitrum, Optimism, etc.)
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import Resource, TextResourceContents, Tool

from .client import EtherscanClient, BlockchainConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Etherscan MCP Server")


# =============================================================================
# Token Operations
# =============================================================================

@mcp.tool()
async def getTokenBalance(
    chainID: str,
    contractAddress: str,
    address: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get the token balance for a specific address.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        contractAddress: The token contract address
        address: The account address to check
        
    Returns:
        Token balance information including raw balance and formatted amount
    """
    await ctx.info(f"Getting token balance for {address} on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_token_balance(chainID, contractAddress, address)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                await ctx.info(f"Token balance retrieved: {result.get('balance_formatted', 'N/A')} tokens")
            else:
                await ctx.error(f"Failed to get token balance: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting token balance: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contract_address": contractAddress,
                "address": address,
                "network": BlockchainConfig.get_network_name(chainID)
            }


@mcp.tool()
async def getTokenDetails(
    chainID: str,
    contractAddress: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get comprehensive token details including name, symbol, decimals, and total supply.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        contractAddress: The token contract address
        
    Returns:
        Token details including name, symbol, decimals, and total supply
    """
    await ctx.info(f"Getting token details for {contractAddress} on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_token_details(chainID, contractAddress)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                token_info = result.get("token_details", {})
                await ctx.info(f"Token details retrieved: {token_info.get('name', 'Unknown')} ({token_info.get('symbol', 'Unknown')})")
            else:
                await ctx.error(f"Failed to get token details: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting token details: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contract_address": contractAddress,
                "network": BlockchainConfig.get_network_name(chainID)
            }


# =============================================================================
# Smart Contract Operations
# =============================================================================

@mcp.tool()
async def getContractABI(
    chainID: str,
    contractAddress: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get the ABI (Application Binary Interface) for a verified contract.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        contractAddress: The contract address
        
    Returns:
        Contract ABI information
    """
    await ctx.info(f"Getting contract ABI for {contractAddress} on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_contract_abi(chainID, contractAddress)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                await ctx.info(f"Contract ABI retrieved successfully")
            else:
                await ctx.error(f"Failed to get contract ABI: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting contract ABI: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contract_address": contractAddress,
                "network": BlockchainConfig.get_network_name(chainID)
            }


@mcp.tool()
async def getContractSourceCode(
    chainID: str,
    contractAddress: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get the source code for a verified contract.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        contractAddress: The contract address
        
    Returns:
        Contract source code information
    """
    await ctx.info(f"Getting contract source code for {contractAddress} on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_contract_source_code(chainID, contractAddress)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                await ctx.info(f"Contract source code retrieved successfully")
            else:
                await ctx.error(f"Failed to get contract source code: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting contract source code: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contract_address": contractAddress,
                "network": BlockchainConfig.get_network_name(chainID)
            }


@mcp.tool()
async def getContractCreation(
    chainID: str,
    contractAddresses: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get contract creator address and creation transaction hash for up to 5 contracts.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        contractAddresses: Comma-separated list of contract addresses (max 5)
        
    Returns:
        Contract creation information including deployer address and creation tx hash
    """
    # Parse contract addresses
    addresses_list = [addr.strip() for addr in contractAddresses.split(",") if addr.strip()]
    
    if not addresses_list:
        return {
            "success": False,
            "error": "No valid contract addresses provided"
        }
    
    if len(addresses_list) > 5:
        return {
            "success": False,
            "error": "Maximum 5 contract addresses allowed"
        }
    
    await ctx.info(f"Getting contract creation info for {len(addresses_list)} contract(s) on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_contract_creation(chainID, addresses_list)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                creation_count = len(result.get("creation_info", []))
                await ctx.info(f"Contract creation info retrieved for {creation_count} contract(s)")
            else:
                await ctx.error(f"Failed to get contract creation info: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting contract creation info: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "requested_addresses": addresses_list,
                "network": BlockchainConfig.get_network_name(chainID)
            }


@mcp.tool()
async def executeContractMethod(
    chainID: str,
    contractAddress: str,
    methodABI: str,
    ctx: Context,
    methodParams: str = "",
    blockNumber: int = None
) -> Dict[str, Any]:
    """
    Execute a contract method with automatic ABI encoding and result decoding.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        contractAddress: The contract address
        methodABI: JSON string containing the method ABI
        methodParams: Comma-separated parameters for the method (optional)
        blockNumber: Block number for eth_call. If None, uses "latest". Integer values are automatically converted to hex format.
        
    Returns:
        Method execution result with decoded data
    """
    # Convert blockNumber to string for client, use "latest" if None
    block_param = str(blockNumber) if blockNumber is not None else "latest"
    await ctx.info(f"Executing contract method on {contractAddress} on {BlockchainConfig.get_network_name(chainID)} at block {block_param}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(30, 100)
            result = await client.execute_contract_method(chainID, contractAddress, methodABI, methodParams, block_param)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                decoded_data = result.get("decodedData", "N/A")
                await ctx.info(f"Contract method executed successfully. Decoded result: {decoded_data}")
            else:
                await ctx.error(f"Failed to execute contract method: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error executing contract method: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "contract_address": contractAddress,
                "method_abi": methodABI,
                "method_params": methodParams,
                "network": BlockchainConfig.get_network_name(chainID)
            }


@mcp.tool()
async def ethGetTransactionReceipt(
    chainID: str,
    txHash: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get transaction receipt information including status, gas usage, and logs.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        txHash: The transaction hash to get receipt for
        
    Returns:
        Transaction receipt with status, gas usage, logs, and other details
    """
    await ctx.info(f"Getting transaction receipt for {txHash} on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_transaction_receipt(chainID, txHash)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                receipt = result.get("receipt", {})
                if receipt:
                    block_number = receipt.get("blockNumber", "N/A")
                    contract_address = receipt.get("contractAddress", "N/A")
                    from_address = receipt.get("from", "N/A")
                    logs_count = len(receipt.get("logs", []))
                    await ctx.info(f"Transaction receipt retrieved: Block={block_number}, Contract={contract_address}, From={from_address}, Logs={logs_count}")
                else:
                    await ctx.info("Transaction receipt retrieved (empty or pending)")
            else:
                await ctx.error(f"Failed to get transaction receipt: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting transaction receipt: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "tx_hash": txHash,
                "network": BlockchainConfig.get_network_name(chainID)
            }


@mcp.tool()
async def ethGetTransactionReceipts(
    chainID: str,
    txHashes: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get transaction receipts for up to 20 transactions.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        txHashes: Comma-separated list of transaction hashes (max 20)
        
    Returns:
        Transaction receipts with status, gas usage, logs, and other details for each hash
    """
    # Parse transaction hashes
    hashes_list = [tx_hash.strip() for tx_hash in txHashes.split(",") if tx_hash.strip()]
    
    if not hashes_list:
        return {
            "success": False,
            "error": "No valid transaction hashes provided"
        }
    
    if len(hashes_list) > 20:
        return {
            "success": False,
            "error": "Maximum 20 transaction hashes allowed"
        }
    
    await ctx.info(f"Getting transaction receipts for {len(hashes_list)} transaction(s) on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_transaction_receipts(chainID, hashes_list)
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                successful_count = result.get("successful_count", 0)
                total_requested = result.get("total_requested", 0)
                await ctx.info(f"Transaction receipts retrieved for {successful_count}/{total_requested} transaction(s)")
                
                # Report any errors
                errors = result.get("errors")
                if errors:
                    await ctx.info(f"Some receipts failed: {'; '.join(errors[:3])}")  # Show first 3 errors
            else:
                await ctx.error(f"Failed to get transaction receipts: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting transaction receipts: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "requested_hashes": hashes_list,
                "network": BlockchainConfig.get_network_name(chainID)
            }


# =============================================================================
# Main Function
# =============================================================================

@mcp.tool()
async def getEventLogs(
    chainID: str,
    address: str,
    topic0: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get event logs for a contract address with topic filtering.
    
    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum, "56" for BSC, "137" for Polygon)
        address: Contract address to get logs from
        topic0: Event signature (e.g., "Burn(address,uint256,uint256,address)") or hex topic0 (e.g., "0x...")
        
    Returns:
        Event logs with decoded information and examples (searches recent blocks, returns up to 5 examples)
    """
    await ctx.info(f"Getting event logs for {address} on {BlockchainConfig.get_network_name(chainID)} with topic0: {topic0}")
    await ctx.report_progress(10, 100)
    
    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(30, 100)
            result = await client.get_event_logs(
                chainID, 
                address, 
                fromBlock="0",  # Search from genesis
                toBlock="latest",  # Search to latest block
                topic0=topic0, 
                topic1=None,  # No second topic filter
                page="1",  # First page
                offset="5"  # Return up to 5 examples
            )
            await ctx.report_progress(90, 100)
            
            if result["success"]:
                logs_count = result.get("logs_count", 0)
                await ctx.info(f"Event logs retrieved: {logs_count} logs found")
                
                # Add example information if logs are found
                if logs_count > 0:
                    logs = result.get("logs", [])
                    if logs:
                        # Show first log as example
                        first_log = logs[0]
                        await ctx.info(f"Example log: Block {first_log.get('blockNumber', 'N/A')}, Tx {first_log.get('transactionHash', 'N/A')[:10]}...")
            else:
                await ctx.error(f"Failed to get event logs: {result.get('error', 'Unknown error')}")
            
            await ctx.report_progress(100, 100)
            return result
            
        except Exception as e:
            await ctx.error(f"Error getting event logs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "address": address,
                "topic0": topic0,
                "network": BlockchainConfig.get_network_name(chainID)
            }


@mcp.tool()
async def getTimestampByBlockNumber(
    chainID: str,
    blockNumber: str,
    ctx: Context
) -> Dict[str, Any]:
    """
    Get UNIX timestamp for a block number.

    Args:
        chainID: Blockchain ID (e.g., "1" for Ethereum)
        blockNumber: Block number. Accepts decimal (e.g., "19000000"), hex (e.g., "0x121b3c0"), or 'latest'.

    Returns:
        Dictionary with timestamp and related fields
    """
    await ctx.info(f"Getting timestamp for block {blockNumber} on {BlockchainConfig.get_network_name(chainID)}")
    await ctx.report_progress(10, 100)

    async with EtherscanClient() as client:
        try:
            await ctx.report_progress(50, 100)
            result = await client.get_timestamp_by_block_number(chainID, blockNumber)
            await ctx.report_progress(90, 100)

            if result.get("success"):
                await ctx.info(f"Timestamp: {result.get('timestamp')} (ISO: {result.get('timestamp_iso', 'n/a')})")
            else:
                await ctx.error(f"Failed to get timestamp: {result.get('error', 'Unknown error')}")

            await ctx.report_progress(100, 100)
            return result
        except Exception as e:
            await ctx.error(f"Error getting timestamp by block number: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "block_number_input": blockNumber,
                "network": BlockchainConfig.get_network_name(chainID)
            }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main() 