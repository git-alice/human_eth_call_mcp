# GitHub Actions Release Setup

This document explains how to set up automated releases for this project.

## Required GitHub Secrets

### 1. PyPI API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create a new API token with scope "Entire account" or specific project
3. Add the token to your GitHub repository secrets:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token

### 2. Etherscan API Key (for CI tests)

1. Get your API key from [Etherscan](https://etherscan.io/apis)
2. Add it to your GitHub repository secrets:
   - Name: `ETHERSCAN_API_KEY`
   - Value: Your Etherscan API key

## Creating a Release

### 1. Update Version

Update the version in `pyproject.toml`:

```toml
[project]
name = "human-eth-call-mcp"
version = "1.0.1"  # Update this
```

### 2. Create and Push Tag

```bash
# Commit your changes
git add .
git commit -m "Release v1.0.1"

# Create and push the tag
git tag v1.0.1
git push origin main
git push origin v1.0.1
```

### 3. Automatic Release

GitHub Actions will automatically:

1. **PyPI Job**:
   - Build the package using `uv build`
   - Publish to PyPI using `uv publish`

2. **GHCR Job**:
   - Build Docker image
   - Push to GitHub Container Registry with tags:
     - `ghcr.io/git-alice/human_eth_call_mcp:1.0.1` (version-specific)
     - `ghcr.io/git-alice/human_eth_call_mcp:latest` (latest)

## Verification

After the release completes:

1. **PyPI**: Check [PyPI project page](https://pypi.org/project/human-eth-call-mcp/)
2. **GHCR**: Check [GitHub Packages](https://github.com/git-alice/human_eth_call_mcp/pkgs/container/human_eth_call_mcp)

## Troubleshooting

### PyPI Upload Fails

- Check that `PYPI_API_TOKEN` secret is correctly set
- Verify the token has the right permissions
- Check if the version already exists on PyPI

### Docker Build Fails

- Check that the Dockerfile is valid
- Verify all required files are included
- Check GitHub Actions logs for specific errors

### Tests Fail in CI

- Ensure `ETHERSCAN_API_KEY` is set
- Check if the API key is valid and has sufficient quota
- Review test logs for specific failures
