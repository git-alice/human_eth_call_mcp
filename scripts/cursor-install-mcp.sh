#!/bin/bash

# Human ETH Call MCP Server - Cursor Installation Script
# Combines UV installation and Cursor MCP setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}🎯 $1${NC}"
    echo "===================="
}

# Check if we're in the project directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_header "Cursor MCP Installation"
echo "Setting up Human ETH Call MCP Server for Cursor"
echo ""

# Step 1: Check UV installation
print_status "Checking UV installation..."
if ! command -v uv &> /dev/null; then
    print_error "UV is not installed. Please install UV first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
print_success "UV is installed"

# Step 2: Check API key
print_status "Checking API key..."
if [ -z "$ETHERSCAN_API_KEY" ]; then
    print_warning "ETHERSCAN_API_KEY not set"
    echo "Please set your API key:"
    echo "export ETHERSCAN_API_KEY=your_api_key_here"
    echo ""
    echo "You can get a free API key from: https://etherscan.io/apis"
    exit 1
fi
print_success "API key found"

# Step 3: Install dependencies with UV
print_status "Installing dependencies with UV..."
uv sync
print_success "Dependencies installed"

# Step 4: Install the package in development mode
print_status "Installing package in development mode..."
uv pip install -e .
print_success "Package installed"

# Step 5: Create .env file if it doesn't exist
print_status "Setting up environment file..."
if [ ! -f ".env" ]; then
    echo "ETHERSCAN_API_KEY=$ETHERSCAN_API_KEY" > .env
    print_success "Created .env file"
else
    print_success ".env file already exists"
fi

# Step 6: Test the installation
print_status "Testing MCP server installation..."
if ! uv run python -c "from etherscan_mcp_server import EtherscanClient; print('✅ MCP server imports successfully')" 2>/dev/null; then
    print_error "MCP server installation failed"
    exit 1
fi
print_success "MCP server installation verified"

# Step 7: Cursor MCP Configuration
print_status "Setting up Cursor MCP configuration..."

# Find Cursor configuration directory
CURSOR_CONFIG_DIR="$HOME/.cursor"
if [ ! -d "$CURSOR_CONFIG_DIR" ]; then
    print_error "Cursor configuration directory not found at $CURSOR_CONFIG_DIR"
    echo "Please make sure Cursor IDE is installed"
    exit 1
fi

MCP_CONFIG_FILE="$CURSOR_CONFIG_DIR/mcp.json"

# Create MCP configuration
MCP_CONFIG='{
  "mcpServers": {
    "human-eth-call": {
      "command": "uv",
      "args": ["run", "human-eth-call-mcp"],
      "env": {
        "ETHERSCAN_API_KEY": "'$ETHERSCAN_API_KEY'"
      }
    }
  }
}'

# Backup existing configuration
if [ -f "$MCP_CONFIG_FILE" ]; then
    print_status "Backing up existing MCP configuration..."
    cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup"
    print_success "Backup created: $MCP_CONFIG_FILE.backup"
fi

# Merge with existing configuration or create new
if [ -f "$MCP_CONFIG_FILE" ]; then
    print_status "Merging with existing MCP configuration..."
    
    # Check if jq is available for JSON merging
    if command -v jq &> /dev/null; then
        # Merge using jq
        jq -s '.[0] * .[1]' <(echo "$MCP_CONFIG") "$MCP_CONFIG_FILE" > "$MCP_CONFIG_FILE.tmp"
        mv "$MCP_CONFIG_FILE.tmp" "$MCP_CONFIG_FILE"
    else
        print_warning "jq not found, overwriting MCP configuration"
        echo "$MCP_CONFIG" > "$MCP_CONFIG_FILE"
    fi
else
    print_status "Creating new MCP configuration..."
    echo "$MCP_CONFIG" > "$MCP_CONFIG_FILE"
fi

print_success "MCP configuration updated"

# Step 8: Verify MCP server accessibility
print_status "Verifying MCP server accessibility..."
if uv run python -c "from etherscan_mcp_server.server import main; print('✅ MCP server module accessible')" 2>/dev/null; then
    print_success "MCP server is accessible"
else
    print_error "MCP server not accessible. Please check the installation"
    exit 1
fi

# Step 9: Test with a simple API call
print_status "Testing API connectivity..."
if uv run python -c "
import asyncio
from etherscan_mcp_server import EtherscanClient
import os

async def test():
    client = EtherscanClient(api_key=os.getenv('ETHERSCAN_API_KEY'))
    try:
        # Test with a simple call
        result = await client.get_token_details('1', '0xA0b86991c431C15C59c7a3C9bcf0d8A0B5c3f1E7')
        print('✅ API connectivity test passed')
    except Exception as e:
        print(f'❌ API connectivity test failed: {e}')
        exit(1)

asyncio.run(test())
" 2>/dev/null; then
    print_success "API connectivity verified"
else
    print_warning "API connectivity test failed (this might be due to API key or network issues)"
fi

echo ""
print_success "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Restart Cursor IDE"
echo "2. The MCP server will be available as 'human-eth-call'"
echo "3. Test with: uv run python tests/test_all_tools.py"
echo ""
echo "🔧 Configuration:"
echo "- MCP config: $MCP_CONFIG_FILE"
echo "- Environment: .env"
echo "- API key: $ETHERSCAN_API_KEY"
echo ""
echo "📖 Documentation: README.md" 