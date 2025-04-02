# Alpaca Trading MCP Server

A Model Context Protocol (MCP) server that provides an interface to the Alpaca trading API, allowing you to manage your stock and crypto portfolio, place trades, and access market data.

## Features

- **Account Management**: View account details, balances, and portfolio status
- **Trading**: Place market, limit, stop, and stop-limit orders
- **Portfolio Management**: View positions, calculate performance, and close positions
- **Market Data**: Access real-time quotes and historical price data
- **Asset Information**: Get details about tradable assets

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -e .
```

Or using uv:

```bash
uv pip install -e .
```

## Configuration

1. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

2. Add your Alpaca Paper Trading API credentials to the `.env` file:

```
ALPACA_PAPER_API_KEY = "your-api-key"
ALPACA_PAPER_API_SECRET = "your-api-secret"
```

You can obtain these credentials by creating an account at [Alpaca](https://app.alpaca.markets/signup).

## Usage

Run the MCP server:

```bash
python src/server.py
```

The server will start and be available for MCP clients to connect to.

## Testing with Claude for Desktop

### Configuration:

Open your Claude for Desktop App configuration in a text editor. Create the file if it doesn't exist.

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application\ Support/Claude/claude_desktop_config.json`


Add the Alpaca MCP server configuration:

```json
{
    "mcpServers": {
        "alpaca": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/alpaca-mcp-server",
                "run",
                "src/server.py"
            ]
        }
    }
}
```
[MCP For Server Developers: Quickstart](https://modelcontextprotocol.io/quickstart/server)

## Available Resources

The server provides the following resources:

- `account://info` - Get current account information
- `positions://all` - Get all current positions
- `positions://{symbol}` - Get position details for a specific symbol
- `orders://recent/{limit}` - Get most recent orders with specified limit
- `market://{symbol}/quote` - Get current market quote for a specific symbol
- `market://{symbol}/bars/{timeframe}` - Get historical price bars for a symbol with specified timeframe
- `assets://list` - List tradable assets available on Alpaca
- `assets://{symbol}` - Get detailed asset information by symbol

## Available Tools

The server provides the following tools:

- `get_account_info_tool` - Get current account information
- `place_market_order` - Place a market order to buy or sell a stock
- `place_limit_order` - Place a limit order to buy or sell a stock at a specified price
- `place_stop_order` - Place a stop order to buy or sell a stock when it reaches a specified price
- `place_stop_limit_order` - Place a stop-limit order combining stop and limit order features
- `cancel_order` - Cancel an open order by its ID
- `close_position` - Close an open position for a specific symbol
- `get_portfolio_summary` - Get a comprehensive summary of the portfolio
