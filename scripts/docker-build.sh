#!/bin/bash

# Docker build script for Human ETH Call MCP Server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 Building Human ETH Call MCP Server Docker image...${NC}"

# Check if ETHERSCAN_API_KEY is set
if [ -z "$ETHERSCAN_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  Warning: ETHERSCAN_API_KEY environment variable is not set${NC}"
    echo -e "${YELLOW}   You'll need to set it when running the container${NC}"
fi

# Build the Docker image
docker build -t human-eth-call-mcp:latest .

echo -e "${GREEN}✅ Docker image built successfully!${NC}"
echo ""
echo -e "${GREEN}To run the container:${NC}"
echo -e "  ${YELLOW}docker run -e ETHERSCAN_API_KEY=your_api_key_here human-eth-call-mcp:latest${NC}"
echo ""
echo -e "${GREEN}Or use docker-compose:${NC}"
echo -e "  ${YELLOW}docker-compose up${NC}"
echo ""
echo -e "${GREEN}To run in background:${NC}"
echo -e "  ${YELLOW}docker-compose up -d${NC}"
