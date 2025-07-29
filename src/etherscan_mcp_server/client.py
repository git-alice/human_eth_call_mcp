"""
Comprehensive Etherscan API Client

Provides access to a wide range of Etherscan API endpoints including:
- Account operations (balance, transactions, token transfers)
- Contract operations (ABI, source code, method execution)
- Block and transaction data
- Gas oracle and network statistics
- Token information and transfers
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from dotenv import load_dotenv
from eth_abi import decode, encode
from eth_utils import function_signature_to_4byte_selector
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class EtherscanConfig(BaseModel):
    """Configuration for Etherscan API client."""
    
    api_key: str = Field(..., description="Etherscan API key")
    base_url: str = Field(default="https://api.etherscan.io", description="Base URL for Etherscan API")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    
    @validator('api_key')
    def validate_api_key(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("API key cannot be empty")
        return v.strip()


class BlockchainConfig:
    """Configuration for blockchain networks with universal support."""
    
    # Common network names for popular chains
    NETWORK_NAMES = {
        "1": "Ethereum Mainnet",
        "56": "BSC Mainnet", 
        "137": "Polygon Mainnet",
        "42161": "Arbitrum One",
        "10": "Optimism",
        "43114": "Avalanche C-Chain",
        "250": "Fantom Opera",
        "8453": "Base",
        "59144": "Linea",
        "534352": "Scroll",
        "1101": "Polygon zkEVM",
        "7777777": "Zora",
        "11155111": "Sepolia Testnet",
        "5": "Goerli Testnet",
        "11155420": "Optimism Sepolia",
        "421614": "Arbitrum Sepolia",
        "80001": "Mumbai Testnet",
        "97": "BSC Testnet",
        "43113": "Avalanche Fuji Testnet",
        "4002": "Fantom Testnet",
    }
    
    @classmethod
    def get_base_url(cls, chain_id: str) -> str:
        """
        Get the base URL for any chain ID.
        For v2 API, we use a universal endpoint that supports all chains via chainid parameter.
        """
        # For v2 API, we can use a universal endpoint
        # The chainid parameter will route to the correct network
        return "https://api.etherscan.io"
    
    @classmethod
    def get_network_name(cls, chain_id: str) -> str:
        """Get the network name for a specific chain ID."""
        return cls.NETWORK_NAMES.get(chain_id, f"Chain ID: {chain_id}")


class EtherscanAPIError(Exception):
    """Custom exception for Etherscan API errors."""
    
    def __init__(self, message: str, code: Optional[int] = None, chain_id: Optional[str] = None):
        self.message = message
        self.code = code
        self.chain_id = chain_id
        super().__init__(f"Etherscan API Error: {message}")


class EtherscanClient:
    """
    Comprehensive async client for Etherscan API with extensive functionality.
    
    Supports multiple blockchain networks and provides access to:
    - Account operations
    - Contract interactions
    - Block and transaction data
    - Token operations
    - Gas oracle
    - And much more
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize the Etherscan client.
        
        Args:
            api_key: Etherscan API key. If not provided, will look for ETHERSCAN_API_KEY env var
            timeout: Request timeout in seconds
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("ETHERSCAN_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Etherscan API key is required. Set ETHERSCAN_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
        
        logger.info("Etherscan client initialized successfully")
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _get_base_url(self, chain_id: str) -> str:
        """Get the appropriate base URL for the given chain ID."""
        return BlockchainConfig.get_base_url(chain_id)
    
    async def _make_request(
        self, 
        chain_id: str, 
        params: Dict[str, Any], 
        use_v2_api: bool = False
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Etherscan API.
        
        Args:
            chain_id: Blockchain ID
            params: Request parameters
            use_v2_api: Whether to use v2 API endpoint
            
        Returns:
            API response data
            
        Raises:
            EtherscanAPIError: If the API request fails
        """
        base_url = self._get_base_url(chain_id)
        endpoint = "/v2/api" if use_v2_api else "/api"
        url = urljoin(base_url, endpoint)
        
        # Add API key to parameters
        params["apikey"] = self.api_key
        
        # Add chain ID for v2 API
        if use_v2_api and "chainid" not in params:
            params["chainid"] = chain_id
        
        try:
            logger.debug(f"Making request to {url} with params: {params}")
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle v2 API format
            if use_v2_api:
                if "result" in result and "error" not in result:
                    return {
                        "success": True,
                        "result": result["result"],
                        "message": "OK"
                    }
                elif "error" in result:
                    raise EtherscanAPIError(
                        result["error"].get("message", "Unknown error"),
                        result["error"].get("code"),
                        chain_id
                    )
            
            # Handle v1 API format
            if result.get("status") == "1":
                return {
                    "success": True,
                    "result": result.get("result"),
                    "message": result.get("message", "OK")
                }
            else:
                error_msg = result.get("message", "Unknown error")
                if result.get("result") and isinstance(result["result"], str):
                    error_msg += f": {result['result']}"
                raise EtherscanAPIError(error_msg, None, chain_id)
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during API request: {e}")
            raise EtherscanAPIError(f"HTTP error: {str(e)}", None, chain_id)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise EtherscanAPIError(f"Invalid JSON response: {str(e)}", None, chain_id)
        except Exception as e:
            if isinstance(e, EtherscanAPIError):
                raise
            logger.error(f"Unexpected error during API request: {e}")
            raise EtherscanAPIError(f"Unexpected error: {str(e)}", None, chain_id)
    
    # =============================================================================
    # Account Operations
    # =============================================================================
    
    async def get_account_balance(self, chain_id: str, address: str) -> Dict[str, Any]:
        """
        Get the account balance for a specific address.
        
        Args:
            chain_id: Blockchain ID
            address: Account address
            
        Returns:
            Account balance information
        """
        params = {
            "module": "account",
            "action": "balance", 
            "address": address,
            "tag": "latest"
        }
        
        try:
            result = await self._make_request(chain_id, params)
            balance_wei = int(result["result"])
            balance_eth = balance_wei / 10**18
            
            return {
                "success": True,
                "address": address,
                "balance_wei": balance_wei,
                "balance_eth": balance_eth,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def get_transactions_by_address(
        self, 
        chain_id: str, 
        address: str,
        start_block: Optional[str] = None,
        end_block: Optional[str] = None,
        page: str = "1",
        offset: str = "10"
    ) -> Dict[str, Any]:
        """
        Get list of transactions for a specific address.
        
        Args:
            chain_id: Blockchain ID
            address: Account address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number
            offset: Number of records to return
            
        Returns:
            List of transactions
        """
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block or "0",
            "endblock": end_block or "99999999",
            "page": page,
            "offset": offset,
            "sort": "desc"
        }
        
        try:
            result = await self._make_request(chain_id, params)
            return {
                "success": True,
                "address": address,
                "transactions": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def get_internal_transactions_by_address(
        self,
        chain_id: str,
        address: str,
        start_block: Optional[str] = None,
        end_block: Optional[str] = None,
        page: str = "1",
        offset: str = "10"
    ) -> Dict[str, Any]:
        """
        Get list of internal transactions for a specific address.
        
        Args:
            chain_id: Blockchain ID
            address: Account address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number
            offset: Number of records to return
            
        Returns:
            List of internal transactions
        """
        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": start_block or "0",
            "endblock": end_block or "99999999",
            "page": page,
            "offset": offset,
            "sort": "desc"
        }
        
        try:
            result = await self._make_request(chain_id, params)
            return {
                "success": True,
                "address": address,
                "internal_transactions": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    # =============================================================================
    # Token Operations
    # =============================================================================
    
    async def get_token_balance(
        self, 
        chain_id: str, 
        contract_address: str, 
        address: str
    ) -> Dict[str, Any]:
        """
        Get the token balance for a specific address and token contract.
        
        Args:
            chain_id: Blockchain ID
            contract_address: Token contract address
            address: Account address
            
        Returns:
            Token balance information
        """
        params = {
            "module": "account",
            "action": "tokenbalance",
            "contractaddress": contract_address,
            "address": address,
            "tag": "latest"
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            return {
                "success": True,
                "address": address,
                "contract_address": contract_address,
                "balance": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address,
                "contract_address": contract_address
            }
    
    async def get_token_transfers_by_address(
        self,
        chain_id: str,
        address: str,
        contract_address: Optional[str] = None,
        start_block: Optional[str] = None,
        end_block: Optional[str] = None,
        page: str = "1",
        offset: str = "10"
    ) -> Dict[str, Any]:
        """
        Get list of token transfers for a specific address.
        
        Args:
            chain_id: Blockchain ID
            address: Account address
            contract_address: Token contract address (optional)
            start_block: Starting block number
            end_block: Ending block number
            page: Page number
            offset: Number of records to return
            
        Returns:
            List of token transfers
        """
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": start_block or "0",
            "endblock": end_block or "99999999",
            "page": page,
            "offset": offset,
            "sort": "desc"
        }
        
        if contract_address:
            params["contractaddress"] = contract_address
        
        try:
            result = await self._make_request(chain_id, params)
            return {
                "success": True,
                "address": address,
                "token_transfers": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def get_erc721_transfers(
        self,
        chain_id: str,
        address: str,
        contract_address: Optional[str] = None,
        start_block: Optional[str] = None,
        end_block: Optional[str] = None,
        page: str = "1",
        offset: str = "10"
    ) -> Dict[str, Any]:
        """
        Get list of ERC721 (NFT) transfers for a specific address.
        
        Args:
            chain_id: Blockchain ID
            address: Account address
            contract_address: NFT contract address (optional)
            start_block: Starting block number
            end_block: Ending block number
            page: Page number
            offset: Number of records to return
            
        Returns:
            List of ERC721 transfers
        """
        params = {
            "module": "account",
            "action": "tokennfttx",
            "address": address,
            "startblock": start_block or "0",
            "endblock": end_block or "99999999",
            "page": page,
            "offset": offset,
            "sort": "desc"
        }
        
        if contract_address:
            params["contractaddress"] = contract_address
        
        try:
            result = await self._make_request(chain_id, params)
            return {
                "success": True,
                "address": address,
                "nft_transfers": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    # =============================================================================
    # Contract Operations
    # =============================================================================
    
    async def get_contract_abi(self, chain_id: str, contract_address: str) -> Dict[str, Any]:
        """
        Get the ABI for a verified contract.
        
        Args:
            chain_id: Blockchain ID
            contract_address: Contract address
            
        Returns:
            Contract ABI information
        """
        params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            abi_json = result["result"]
            
            # Parse ABI to extract function signatures
            functions = []
            events = []
            
            try:
                abi = json.loads(abi_json)
                for item in abi:
                    if item.get("type") == "function":
                        functions.append({
                            "name": item.get("name"),
                            "inputs": item.get("inputs", []),
                            "outputs": item.get("outputs", []),
                            "stateMutability": item.get("stateMutability"),
                        })
                    elif item.get("type") == "event":
                        events.append({
                            "name": item.get("name"),
                            "inputs": item.get("inputs", []),
                        })
            except json.JSONDecodeError:
                pass  # ABI parsing failed, return raw ABI
            
            return {
                "success": True,
                "contract_address": contract_address,
                "abi": abi_json,
                "functions": functions,
                "events": events,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "contract_address": contract_address
            }
    
    async def get_contract_source_code(self, chain_id: str, contract_address: str) -> Dict[str, Any]:
        """
        Get the source code of a verified contract.
        
        Args:
            chain_id: Blockchain ID
            contract_address: Contract address
            
        Returns:
            Contract source code information
        """
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": contract_address
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            
            # Handle different response formats
            if isinstance(result["result"], list) and len(result["result"]) > 0:
                source_info = result["result"][0]
            elif isinstance(result["result"], dict):
                source_info = result["result"]
            else:
                source_info = {}
            
            return {
                "success": True,
                "contract_address": contract_address,
                "source_code": source_info.get("SourceCode", ""),
                "contract_name": source_info.get("ContractName", ""),
                "compiler_version": source_info.get("CompilerVersion", ""),
                "optimization_used": source_info.get("OptimizationUsed", ""),
                "runs": source_info.get("Runs", ""),
                "constructor_arguments": source_info.get("ConstructorArguments", ""),
                "library": source_info.get("Library", ""),
                "license_type": source_info.get("LicenseType", ""),
                "proxy": source_info.get("Proxy", ""),
                "implementation": source_info.get("Implementation", ""),
                "swarm_source": source_info.get("SwarmSource", ""),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "contract_address": contract_address
            }
    
    async def get_contract_creation(self, chain_id: str, contract_addresses: List[str]) -> Dict[str, Any]:
        """
        Get contract creator address and creation transaction hash for up to 5 contracts.
        
        Args:
            chain_id: Blockchain ID
            contract_addresses: List of contract addresses (max 5)
            
        Returns:
            Contract creation information for each address
        """
        # Validate input
        if not contract_addresses:
            return {
                "success": False,
                "error": "Contract addresses list cannot be empty"
            }
        
        if len(contract_addresses) > 5:
            return {
                "success": False,
                "error": "Maximum 5 contract addresses allowed"
            }
        
        # Join addresses with comma
        addresses_param = ",".join(contract_addresses)
        
        params = {
            "module": "contract",
            "action": "getcontractcreation",
            "contractaddresses": addresses_param
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            
            # Process results
            creation_info = []
            if isinstance(result["result"], list):
                for item in result["result"]:
                    creation_info.append({
                        "contract_address": item.get("contractAddress", ""),
                        "contract_creator": item.get("contractCreator", ""),
                        "tx_hash": item.get("txHash", "")
                    })
            elif isinstance(result["result"], dict):
                # Single result format
                creation_info.append({
                    "contract_address": result["result"].get("contractAddress", ""),
                    "contract_creator": result["result"].get("contractCreator", ""),
                    "tx_hash": result["result"].get("txHash", "")
                })
            
            return {
                "success": True,
                "requested_addresses": contract_addresses,
                "creation_info": creation_info,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "requested_addresses": contract_addresses,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    # =============================================================================
    # Smart Contract Method Execution with ABI Encoding/Decoding
    # =============================================================================
    
    def encode_function_call(self, method_abi: str, method_params: str = "") -> str:
        """
        Encode a function call from ABI and parameters into call_data.
        
        Args:
            method_abi: JSON string with function ABI
            method_params: Comma-separated parameter values
            
        Returns:
            Encoded call data for eth_call (0x...)
        """
        try:
            # Parse ABI
            abi = json.loads(method_abi)
            
            # Get function signature
            function_name = abi["name"]
            inputs = abi.get("inputs", [])
            
            # Build function signature for selector
            input_types = [inp["type"] for inp in inputs]
            function_signature = f"{function_name}({','.join(input_types)})"
            
            # Get 4-byte function selector
            selector = function_signature_to_4byte_selector(function_signature)
            
            # Parse parameters
            if not method_params or method_params.strip() == "":
                params = []
            else:
                # Simple parameter parsing (can be enhanced for complex types)
                params = [param.strip() for param in method_params.split(",")]
            
            # Convert parameters to correct types
            converted_params = []
            for i, param in enumerate(params):
                if i < len(input_types):
                    param_type = input_types[i]
                    converted_param = self._convert_param(param, param_type)
                    converted_params.append(converted_param)
            
            # Encode parameters
            if converted_params:
                encoded_params = encode(input_types, converted_params)
            else:
                encoded_params = b""
            
            # Combine selector and parameters
            call_data = selector + encoded_params
            
            return call_data.hex()
            
        except Exception as e:
            raise ValueError(f"Error encoding function call: {str(e)}")
    
    def decode_function_result(self, result_hex: str, method_abi: str) -> Dict[str, Any]:
        """
        Decode eth_call result based on ABI outputs.
        
        Args:
            result_hex: Hex string result (e.g., "0x000...123")
            method_abi: JSON string with function ABI
            
        Returns:
            Dictionary with decoded data
        """
        try:
            # Parse ABI
            abi = json.loads(method_abi)
            outputs = abi.get("outputs", [])
            
            # Check for empty result
            if not result_hex or result_hex == "0x" or result_hex == "0x0":
                return {
                    "raw_data": result_hex,
                    "decoded_data": None,
                    "output_types": [out["type"] for out in outputs],
                    "output_names": [out.get("name", f"output_{i}") for i, out in enumerate(outputs)],
                    "error": "Empty result" if result_hex == "0x" else None
                }
            
            # Remove 0x prefix
            hex_data = result_hex[2:] if result_hex.startswith("0x") else result_hex
            
            # Check for empty data
            if not hex_data:
                return {
                    "raw_data": result_hex,
                    "decoded_data": None,
                    "output_types": [out["type"] for out in outputs],
                    "output_names": [out.get("name", f"output_{i}") for i, out in enumerate(outputs)],
                    "error": "No data to decode"
                }
            
            # If no outputs in ABI, return raw data
            if not outputs:
                return {
                    "raw_data": result_hex,
                    "decoded_data": result_hex,
                    "output_types": [],
                    "output_names": [],
                    "note": "No outputs defined in ABI"
                }
            
            # Get output types and names
            output_types = [out["type"] for out in outputs]
            output_names = [out.get("name", f"output_{i}") for i, out in enumerate(outputs)]
            
            # Decode data
            try:
                decoded_values = decode(output_types, bytes.fromhex(hex_data))
            except Exception as decode_err:
                return {
                    "raw_data": result_hex,
                    "decoded_data": None,
                    "output_types": output_types,
                    "output_names": output_names,
                    "error": f"Decode error: {str(decode_err)}"
                }
            
            # Format result
            if len(decoded_values) == 1:
                # Single value
                formatted_value = self._format_decoded_value(decoded_values[0], output_types[0])
                decoded_data = formatted_value
            else:
                # Multiple values
                decoded_data = {}
                for i, (value, name) in enumerate(zip(decoded_values, output_names)):
                    formatted_value = self._format_decoded_value(value, output_types[i])
                    key = name if name else f"output_{i}"
                    decoded_data[key] = formatted_value
            
            return {
                "raw_data": result_hex,
                "decoded_data": decoded_data,
                "output_types": output_types,
                "output_names": output_names,
                "values_count": len(decoded_values)
            }
            
        except Exception as e:
            return {
                "raw_data": result_hex,
                "decoded_data": None,
                "error": f"Error decoding result: {str(e)}"
            }
    
    def _format_decoded_value(self, value: Any, value_type: str) -> Union[str, int, bool, Any]:
        """Format decoded value into readable format."""
        try:
            if value_type == "address":
                # Return addresses as hex strings
                if isinstance(value, bytes):
                    return "0x" + value.hex()
                elif isinstance(value, str):
                    if not value.startswith("0x"):
                        return "0x" + value
                return value
            elif value_type.startswith("uint") or value_type.startswith("int"):
                # Return numbers as int
                return int(value)
            elif value_type == "bool":
                return bool(value)
            elif value_type == "string":
                if isinstance(value, bytes):
                    return value.decode('utf-8', errors='ignore')
                return str(value)
            elif value_type.startswith("bytes"):
                if isinstance(value, bytes):
                    return "0x" + value.hex()
                return value
            else:
                # For other types return as is
                return value
        except Exception:
            # If formatting fails, return as is
            return value
    
    def _convert_param(self, param: str, param_type: str) -> Any:
        """Convert string parameter to appropriate type."""
        try:
            if param_type.startswith("uint") or param_type.startswith("int"):
                return int(param)
            elif param_type == "address":
                return param.strip()
            elif param_type == "bool":
                return param.lower() in ("true", "1", "yes")
            elif param_type == "string":
                return param.strip()
            elif param_type.startswith("bytes"):
                if param.startswith("0x"):
                    return bytes.fromhex(param[2:])
                return param.encode()
            else:
                # For other types return as is
                return param.strip()
        except Exception:
            # If conversion fails, return as is
            return param.strip()
    
    async def execute_contract_method(
        self,
        chain_id: str,
        contract_address: str,
        method_abi: str,
        method_params: str = "",
        tag: str = "latest"
    ) -> Dict[str, Any]:
        """
        Execute a smart contract method using ABI and parameters.
        
        Args:
            chain_id: Blockchain ID
            contract_address: Smart contract address
            method_abi: JSON string with method ABI
            method_params: Comma-separated parameter values
            tag: Block tag
            
        Returns:
            Method execution result with decoded data
        """
        try:
            # Encode function call
            call_data = self.encode_function_call(method_abi, method_params)
            
            # Add 0x prefix if needed
            if not call_data.startswith("0x"):
                call_data = "0x" + call_data
            
            # Execute eth_call
            result = await self.eth_call(
                chain_id=chain_id,
                to_address=contract_address,
                data=call_data,
                tag=tag
            )
            
            # If call succeeded, decode result
            decoded_result = None
            if result["success"] and result.get("result"):
                decoded_result = self.decode_function_result(result["result"], method_abi)
            
            # Form proper function signature
            abi = json.loads(method_abi)
            function_name = abi["name"]
            input_types = [inp["type"] for inp in abi.get("inputs", [])]
            function_signature = f"{function_name}({','.join(input_types)})"
            
            # Add call information and decoded data
            result.update({
                "function_signature": function_signature,
                "encoded_call_data": call_data,
                "input_params": method_params,
                "decoded_result": decoded_result,
                "network": BlockchainConfig.get_network_name(chain_id)
            })
            
            return result
            
        except Exception as e:
            # Try to form function signature even on error
            function_signature = "unknown"
            if method_abi:
                try:
                    abi = json.loads(method_abi)
                    function_name = abi.get("name", "unknown")
                    input_types = [inp["type"] for inp in abi.get("inputs", [])]
                    function_signature = f"{function_name}({','.join(input_types)})"
                except:
                    function_signature = "unknown"
            
            return {
                "success": False,
                "error": f"Error executing contract method: {str(e)}",
                "function_signature": function_signature,
                "input_params": method_params,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    async def eth_call(
        self,
        chain_id: str,
        to_address: str,
        data: str,
        tag: str = "latest"
    ) -> Dict[str, Any]:
        """
        Execute eth_call request to a smart contract.
        
        Args:
            chain_id: Blockchain ID
            to_address: Smart contract address
            data: Encoded function call data
            tag: Block tag (latest, earliest, pending or block number)
            
        Returns:
            eth_call result
        """
        params = {
            "module": "proxy",
            "action": "eth_call",
            "to": to_address,
            "data": data,
            "tag": tag
        }
        
        try:
            logger.info(f"Making eth_call to {to_address} on {BlockchainConfig.get_network_name(chain_id)}")
            result = await self._make_request(chain_id, params, use_v2_api=True)
            result["network"] = BlockchainConfig.get_network_name(chain_id)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    # =============================================================================
    # Block and Transaction Operations
    # =============================================================================
    
    async def get_latest_block_number(self, chain_id: str) -> Dict[str, Any]:
        """
        Get the latest block number.
        
        Args:
            chain_id: Blockchain ID
            
        Returns:
            Latest block number
        """
        params = {
            "module": "proxy",
            "action": "eth_blockNumber"
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            block_number = int(result["result"], 16) if result["result"].startswith("0x") else int(result["result"])
            
            return {
                "success": True,
                "block_number": block_number,
                "block_number_hex": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    async def get_block_by_number(self, chain_id: str, block_number: str) -> Dict[str, Any]:
        """
        Get block information by block number.
        
        Args:
            chain_id: Blockchain ID
            block_number: Block number (or 'latest')
            
        Returns:
            Block information
        """
        params = {
            "module": "proxy",
            "action": "eth_getBlockByNumber",
            "tag": block_number,
            "boolean": "true"
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            return {
                "success": True,
                "block": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    async def get_transaction_by_hash(self, chain_id: str, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction details by hash.
        
        Args:
            chain_id: Blockchain ID
            tx_hash: Transaction hash
            
        Returns:
            Transaction details
        """
        params = {
            "module": "proxy",
            "action": "eth_getTransactionByHash",
            "txhash": tx_hash
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            return {
                "success": True,
                "transaction": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    async def get_transaction_receipt(self, chain_id: str, tx_hash: str) -> Dict[str, Any]:
        """
        Check transaction receipt status.
        
        Args:
            chain_id: Blockchain ID
            tx_hash: Transaction hash
            
        Returns:
            Transaction receipt
        """
        params = {
            "module": "proxy",
            "action": "eth_getTransactionReceipt",
            "txhash": tx_hash
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            return {
                "success": True,
                "receipt": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    async def get_transaction_receipts(self, chain_id: str, tx_hashes: List[str]) -> Dict[str, Any]:
        """
        Get transaction receipts for up to 5 transactions.
        
        Args:
            chain_id: Blockchain ID
            tx_hashes: List of transaction hashes (max 5)
            
        Returns:
            Transaction receipts for each hash
        """
        # Validate input
        if not tx_hashes:
            return {
                "success": False,
                "error": "Transaction hashes list cannot be empty"
            }
        
        if len(tx_hashes) > 20:
            return {
                "success": False,
                "error": "Maximum 20 transaction hashes allowed"
            }
        
        try:
            # Get receipts for each transaction
            receipts_info = []
            errors = []
            
            for tx_hash in tx_hashes:
                try:
                    receipt_result = await self.get_transaction_receipt(chain_id, tx_hash)
                    if receipt_result["success"]:
                        receipts_info.append({
                            "tx_hash": tx_hash,
                            "receipt": receipt_result["receipt"],
                            "success": True
                        })
                    else:
                        receipts_info.append({
                            "tx_hash": tx_hash,
                            "receipt": None,
                            "success": False,
                            "error": receipt_result.get("error", "Unknown error")
                        })
                        errors.append(f"{tx_hash}: {receipt_result.get('error', 'Unknown error')}")
                except Exception as e:
                    receipts_info.append({
                        "tx_hash": tx_hash,
                        "receipt": None,
                        "success": False,
                        "error": str(e)
                    })
                    errors.append(f"{tx_hash}: {str(e)}")
            
            # Check if we have any successful results
            successful_count = sum(1 for r in receipts_info if r["success"])
            
            return {
                "success": True,
                "requested_hashes": tx_hashes,
                "receipts_info": receipts_info,
                "successful_count": successful_count,
                "total_requested": len(tx_hashes),
                "errors": errors if errors else None,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "requested_hashes": tx_hashes,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    async def get_transaction_status(self, chain_id: str, tx_hash: str) -> Dict[str, Any]:
        """
        Check contract execution status.
        
        Args:
            chain_id: Blockchain ID
            tx_hash: Transaction hash
            
        Returns:
            Transaction execution status
        """
        params = {
            "module": "transaction",
            "action": "getstatus",
            "txhash": tx_hash
        }
        
        try:
            result = await self._make_request(chain_id, params)
            return {
                "success": True,
                "status": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    async def get_transaction_count(self, chain_id: str, address: str, tag: str = "latest") -> Dict[str, Any]:
        """
        Get the number of transactions sent from an address.
        
        Args:
            chain_id: Blockchain ID
            address: Account address
            tag: Block number tag (default: 'latest')
            
        Returns:
            Transaction count (nonce)
        """
        params = {
            "module": "proxy",
            "action": "eth_getTransactionCount",
            "address": address,
            "tag": tag
        }
        
        try:
            result = await self._make_request(chain_id, params, use_v2_api=True)
            nonce = int(result["result"], 16) if result["result"].startswith("0x") else int(result["result"])
            
            return {
                "success": True,
                "address": address,
                "nonce": nonce,
                "nonce_hex": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    # =============================================================================
    # Gas and Network Operations
    # =============================================================================
    
    async def get_gas_oracle(self, chain_id: str) -> Dict[str, Any]:
        """
        Get current gas price oracle output.
        
        Args:
            chain_id: Blockchain ID
            
        Returns:
            Gas price information
        """
        params = {
            "module": "gastracker",
            "action": "gasoracle"
        }
        
        try:
            result = await self._make_request(chain_id, params)
            return {
                "success": True,
                "gas_price": result["result"],
                "network": BlockchainConfig.get_network_name(chain_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "network": BlockchainConfig.get_network_name(chain_id)
            }
    
    # =============================================================================
    # Utility Methods
    # =============================================================================
    
    async def get_token_details(self, chain_id: str, contract_address: str) -> Dict[str, Any]:
        """
        Get comprehensive token information by analyzing the contract.
        
        Args:
            chain_id: Blockchain ID
            contract_address: Token contract address
            
        Returns:
            Comprehensive token details
        """
        try:
            # Get contract ABI
            abi_result = await self.get_contract_abi(chain_id, contract_address)
            if not abi_result["success"]:
                return {
                    "success": False,
                    "error": "Could not retrieve contract ABI",
                    "contract_address": contract_address
                }
            
            # Common ERC20 function ABIs
            name_abi = '{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}'
            symbol_abi = '{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"}'
            decimals_abi = '{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"}'
            total_supply_abi = '{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}'
            
            # Execute multiple contract calls
            results = {}
            
            # Get token name
            try:
                name_result = await self.execute_contract_method(chain_id, contract_address, name_abi)
                if name_result["success"] and name_result.get("decoded_result"):
                    results["name"] = name_result["decoded_result"]["decoded_data"]
            except:
                results["name"] = "Unknown"
            
            # Get token symbol
            try:
                symbol_result = await self.execute_contract_method(chain_id, contract_address, symbol_abi)
                if symbol_result["success"] and symbol_result.get("decoded_result"):
                    results["symbol"] = symbol_result["decoded_result"]["decoded_data"]
            except:
                results["symbol"] = "Unknown"
            
            # Get decimals
            try:
                decimals_result = await self.execute_contract_method(chain_id, contract_address, decimals_abi)
                if decimals_result["success"] and decimals_result.get("decoded_result"):
                    results["decimals"] = decimals_result["decoded_result"]["decoded_data"]
            except:
                results["decimals"] = 18  # Default for most tokens
            
            # Get total supply
            try:
                supply_result = await self.execute_contract_method(chain_id, contract_address, total_supply_abi)
                if supply_result["success"] and supply_result.get("decoded_result"):
                    results["total_supply"] = supply_result["decoded_result"]["decoded_data"]
            except:
                results["total_supply"] = 0
            
            return {
                "success": True,
                "contract_address": contract_address,
                "token_details": results,
                "network": BlockchainConfig.get_network_name(chain_id)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "contract_address": contract_address,
                "network": BlockchainConfig.get_network_name(chain_id)
            } 