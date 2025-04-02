from datetime import datetime, timedelta

from mcp.server.fastmcp import FastMCP

# Custom modules
from alpaca_client import AlpacaClient
from models import (
    AlpacaOrderRequest, AlpacaOrderType, 
    AlpacaOrderSide, AlpacaTimeInForce, AlpacaTimeFrame
)
import calls

# Create the MCP server with a name and dependencies
mcp = FastMCP("Alpaca Trading", 
              dependencies=["alpaca-py", "python-dotenv"])

# Initialize Alpaca clients directly
alpaca_client = AlpacaClient()
trading_client = alpaca_client.trading_client()
stock_client = alpaca_client.stock_client()
crypto_client = alpaca_client.crypto_client()


# ---- RESOURCES ----

@mcp.resource("account://info")
def get_account_info() -> str:
    """Get current account information."""
    account = calls.get_account(trading_client)
    return (
        f"Account Summary:\n"
        f"Status: {account.status}\n"
        f"Cash: ${account.cash:.2f}\n"
        f"Portfolio Value: ${account.portfolio_value:.2f}\n"
        f"Buying Power: ${account.buying_power:.2f}\n"
        f"Equity: ${account.equity:.2f}\n"
        f"Daytrade Count: {account.daytrade_count}\n"
        f"Pattern Day Trader: {account.pattern_day_trader}\n"
    )


@mcp.resource("positions://all")
def get_all_positions() -> str:
    """Get all current positions."""
    positions = calls.get_positions(trading_client)
    
    if not positions:
        return "No open positions found."
    
    result = "Current Positions:\n\n"
    for pos in positions:
        pl_percent = pos.unrealized_plpc * 100
        pl_sign = "+" if pos.unrealized_pl >= 0 else ""
        result += (
            f"{pos.symbol} ({pos.side.upper()}):\n"
            f"  Quantity: {pos.qty}\n"
            f"  Avg Entry: ${pos.avg_entry_price:.2f}\n"
            f"  Current Price: ${pos.current_price:.2f}\n"
            f"  Market Value: ${pos.market_value:.2f}\n"
            f"  Unrealized P/L: {pl_sign}${pos.unrealized_pl:.2f} ({pl_sign}{pl_percent:.2f}%)\n\n"
        )
    
    return result


@mcp.resource("positions://{symbol}")
def get_position_by_symbol(symbol: str) -> str:
    """Get position details for a specific symbol."""
    position = calls.get_position(trading_client, symbol)
    
    if not position:
        return f"No position found for {symbol}."
    
    pl_percent = position.unrealized_plpc * 100
    pl_sign = "+" if position.unrealized_pl >= 0 else ""
    
    return (
        f"{position.symbol} Position ({position.side.upper()}):\n"
        f"Quantity: {position.qty}\n"
        f"Avg Entry: ${position.avg_entry_price:.2f}\n"
        f"Current Price: ${position.current_price:.2f}\n"
        f"Market Value: ${position.market_value:.2f}\n"
        f"Cost Basis: ${position.cost_basis:.2f}\n"
        f"Unrealized P/L: {pl_sign}${position.unrealized_pl:.2f} ({pl_sign}{pl_percent:.2f}%)\n"
        f"Today's Change: {'+' if position.change_today >= 0 else ''}{position.change_today:.2f}%\n"
    )


@mcp.resource("orders://recent/{limit}")
def get_recent_orders(limit: int) -> str:
    """Get most recent orders with specified limit."""
    try:
        limit_val = int(limit)
        if limit_val <= 0 or limit_val > 100:
            return "Limit must be between 1 and 100."
    except ValueError:
        return "Invalid limit value. Must be an integer."
    
    orders = calls.get_orders(trading_client, limit=limit_val)
    
    if not orders:
        return "No recent orders found."
    
    result = f"Recent Orders (last {limit_val}):\n\n"
    for order in orders:
        result += (
            f"Order ID: {order.id}\n"
            f"Symbol: {order.symbol}\n"
            f"Type: {order.type.value}\n"
            f"Side: {order.side.value}\n"
            f"Qty: {order.qty}\n"
            f"Status: {order.status.value}\n"
            f"Created: {order.created_at}\n"
        )
        
        if order.filled_avg_price:
            result += f"Filled Price: ${order.filled_avg_price:.2f}\n"
        
        if order.limit_price:
            result += f"Limit Price: ${order.limit_price:.2f}\n"
        
        if order.stop_price:
            result += f"Stop Price: ${order.stop_price:.2f}\n"
            
        result += "\n"
    
    return result


@mcp.resource("market://{symbol}/quote")
def get_market_quote(symbol: str) -> str:
    """Get current market quote for a specific symbol."""
    try:
        quote = calls.get_latest_quote(stock_client, symbol)
        return (
            f"Latest Quote for {symbol}:\n"
            f"Ask: ${quote.ask_price:.2f} x {quote.ask_size}\n"
            f"Bid: ${quote.bid_price:.2f} x {quote.bid_size}\n"
            f"Spread: ${quote.ask_price - quote.bid_price:.2f}\n"
            f"Timestamp: {quote.timestamp}\n"
        )
    except Exception as e:
        return f"Error fetching quote for {symbol}: {str(e)}"


@mcp.resource("market://{symbol}/bars/{timeframe}")
def get_historical_bars(symbol: str, timeframe: str) -> str:
    """Get historical price bars for a symbol with specified timeframe."""
    # Map string timeframe to Alpaca TimeFrame
    try:
        tf = AlpacaTimeFrame(timeframe).to_timeframe()
    except (ValueError, KeyError):
        return f"Invalid timeframe: {timeframe}. Use one of: Min, Hour, Day, Week, Month"
    
    # Set default time period based on timeframe
    end = datetime.now()
    if timeframe == "Min":
        start = end - timedelta(hours=6)
    elif timeframe == "Hour":
        start = end - timedelta(days=7)
    else:
        start = end - timedelta(days=30)
    
    try:
        bars = calls.get_historical_bars(
            stock_client, symbol, timeframe=tf, start=start, end=end
        )
        
        if not bars:
            return f"No historical bars found for {symbol} with {timeframe} timeframe."
        
        result = f"Historical {timeframe} Bars for {symbol} (last {len(bars)}):\n\n"
        # Show only the most recent 10 bars if there are more
        display_bars = bars[-10:] if len(bars) > 10 else bars
        
        for bar in display_bars:
            result += (
                f"{bar.timestamp.strftime('%Y-%m-%d %H:%M')}:\n"
                f"  Open: ${bar.open:.2f}\n"
                f"  High: ${bar.high:.2f}\n"
                f"  Low: ${bar.low:.2f}\n"
                f"  Close: ${bar.close:.2f}\n"
                f"  Volume: {bar.volume:,}\n\n"
            )
        
        if len(bars) > 10:
            result += f"Note: Showing only the most recent 10 of {len(bars)} bars."
        
        return result
    except Exception as e:
        return f"Error fetching bars for {symbol}: {str(e)}"


@mcp.resource("assets://list")
def list_tradable_assets() -> str:
    """List tradable assets available on Alpaca."""
    assets = calls.get_assets(trading_client)
    
    # Filter for tradable assets only
    tradable_assets = [asset for asset in assets if asset.tradable]
    
    if not tradable_assets:
        return "No tradable assets found."
    
    # Limit to first 50 for readability
    display_assets = tradable_assets[:50]
    
    result = f"Tradable Assets (showing first {len(display_assets)} of {len(tradable_assets)}):\n\n"
    
    for asset in display_assets:
        result += (
            f"{asset.symbol} - {asset.name}\n"
            f"  Class: {asset.asset_class.value}\n"
            f"  Exchange: {asset.exchange.value}\n"
            f"  Fractionable: {asset.fractionable}\n"
            f"  Shortable: {asset.shortable}\n\n"
        )
    
    return result


@mcp.resource("assets://{symbol}")
def get_asset_info(symbol: str) -> str:
    """Get detailed asset information by symbol."""
    try:
        asset = calls.get_asset_by_symbol(trading_client, symbol)
        
        attribute_list = ", ".join(asset.attributes) if asset.attributes else "None"
        
        return (
            f"Asset Information for {asset.symbol} ({asset.name}):\n"
            f"ID: {asset.id}\n"
            f"Class: {asset.asset_class.value}\n"
            f"Exchange: {asset.exchange.value}\n"
            f"Status: {asset.status.value}\n"
            f"Tradable: {asset.tradable}\n"
            f"Fractionable: {asset.fractionable}\n"
            f"Marginable: {asset.marginable}\n"
            f"Shortable: {asset.shortable}\n"
            f"Easy to Borrow: {asset.easy_to_borrow}\n"
            f"Attributes: {attribute_list}\n"
        )
    except Exception as e:
        return f"Error fetching asset information for {symbol}: {str(e)}"


# ---- TOOLS ----

@mcp.tool()
def get_account_info_tool() -> str:
    """
    Get current account information.
    
    Returns:
        Account summary with balance and status
    """
    account = calls.get_account(trading_client)
    return (
        f"Account Summary:\n"
        f"Status: {account.status}\n"
        f"Cash: ${account.cash:.2f}\n"
        f"Portfolio Value: ${account.portfolio_value:.2f}\n"
        f"Buying Power: ${account.buying_power:.2f}\n"
        f"Equity: ${account.equity:.2f}\n"
        f"Daytrade Count: {account.daytrade_count}\n"
        f"Pattern Day Trader: {account.pattern_day_trader}\n"
    )


@mcp.tool()
def place_market_order(symbol: str, quantity: float, side: str) -> str:
    """
    Place a market order to buy or sell a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        quantity: Number of shares to buy or sell (can be fractional)
        side: Either 'buy' or 'sell'
    
    Returns:
        Order confirmation details
    """
    # Validate side
    try:
        order_side = AlpacaOrderSide(side.lower())
    except ValueError:
        return f"Invalid side: {side}. Must be 'buy' or 'sell'."
    
    # Create order request
    order_request = AlpacaOrderRequest(
        symbol=symbol,
        qty=float(quantity),
        side=order_side,
        type=AlpacaOrderType.MARKET,
        time_in_force=AlpacaTimeInForce.DAY
    )
    
    try:
        order = calls.place_order(trading_client, order_request)
        
        return (
            f"Market order placed successfully!\n\n"
            f"Order ID: {order.id}\n"
            f"Symbol: {order.symbol}\n"
            f"Side: {order.side.value}\n"
            f"Type: {order.type.value}\n"
            f"Quantity: {order.qty}\n"
            f"Status: {order.status.value}\n"
            f"Created At: {order.created_at}\n"
        )
    except Exception as e:
        return f"Error placing market order: {str(e)}"


@mcp.tool()
def place_limit_order(
    symbol: str, 
    quantity: float, 
    side: str, 
    limit_price: float, 
    time_in_force: str = "day"
) -> str:
    """
    Place a limit order to buy or sell a stock at a specified price.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        quantity: Number of shares to buy or sell (can be fractional)
        side: Either 'buy' or 'sell'
        limit_price: Maximum price for buy or minimum price for sell
        time_in_force: Order duration - 'day', 'gtc' (good till canceled), 'ioc' (immediate or cancel)
    
    Returns:
        Order confirmation details
    """
    # Validate side
    try:
        order_side = AlpacaOrderSide(side.lower())
    except ValueError:
        return f"Invalid side: {side}. Must be 'buy' or 'sell'."
    
    # Validate time in force
    try:
        order_tif = AlpacaTimeInForce(time_in_force.lower())
    except ValueError:
        return f"Invalid time in force: {time_in_force}. Valid options are: day, gtc, ioc, fok"
    
    # Create order request
    order_request = AlpacaOrderRequest(
        symbol=symbol,
        qty=float(quantity),
        side=order_side,
        type=AlpacaOrderType.LIMIT,
        time_in_force=order_tif,
        limit_price=float(limit_price)
    )
    
    try:
        order = calls.place_order(trading_client, order_request)
        
        return (
            f"Limit order placed successfully!\n\n"
            f"Order ID: {order.id}\n"
            f"Symbol: {order.symbol}\n"
            f"Side: {order.side.value}\n"
            f"Type: {order.type.value}\n"
            f"Quantity: {order.qty}\n"
            f"Limit Price: ${order.limit_price:.2f}\n"
            f"Time in Force: {order.time_in_force.value}\n"
            f"Status: {order.status.value}\n"
            f"Created At: {order.created_at}\n"
        )
    except Exception as e:
        return f"Error placing limit order: {str(e)}"


@mcp.tool()
def place_stop_order(
    symbol: str, 
    quantity: float, 
    side: str, 
    stop_price: float,
    time_in_force: str = "day"
) -> str:
    """
    Place a stop order to buy or sell a stock when it reaches a specified price.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        quantity: Number of shares to buy or sell (can be fractional)
        side: Either 'buy' or 'sell'
        stop_price: Price that triggers the order
        time_in_force: Order duration - 'day', 'gtc' (good till canceled)
    
    Returns:
        Order confirmation details
    """
    # Validate side
    try:
        order_side = AlpacaOrderSide(side.lower())
    except ValueError:
        return f"Invalid side: {side}. Must be 'buy' or 'sell'."
    
    # Validate time in force
    try:
        order_tif = AlpacaTimeInForce(time_in_force.lower())
    except ValueError:
        return f"Invalid time in force: {time_in_force}. Valid options are: day, gtc"
    
    # Create order request
    order_request = AlpacaOrderRequest(
        symbol=symbol,
        qty=float(quantity),
        side=order_side,
        type=AlpacaOrderType.STOP,
        time_in_force=order_tif,
        stop_price=float(stop_price)
    )
    
    try:
        order = calls.place_order(trading_client, order_request)
        
        return (
            f"Stop order placed successfully!\n\n"
            f"Order ID: {order.id}\n"
            f"Symbol: {order.symbol}\n"
            f"Side: {order.side.value}\n"
            f"Type: {order.type.value}\n"
            f"Quantity: {order.qty}\n"
            f"Stop Price: ${order.stop_price:.2f}\n"
            f"Time in Force: {order.time_in_force.value}\n"
            f"Status: {order.status.value}\n"
            f"Created At: {order.created_at}\n"
        )
    except Exception as e:
        return f"Error placing stop order: {str(e)}"


@mcp.tool()
def place_stop_limit_order(
    symbol: str, 
    quantity: float, 
    side: str, 
    stop_price: float,
    limit_price: float,
    time_in_force: str = "day"
) -> str:
    """
    Place a stop-limit order combining stop and limit order features.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        quantity: Number of shares to buy or sell (can be fractional)
        side: Either 'buy' or 'sell'
        stop_price: Price that triggers the order
        limit_price: Maximum/minimum price for the triggered order
        time_in_force: Order duration - 'day', 'gtc' (good till canceled)
    
    Returns:
        Order confirmation details
    """
    # Validate side
    try:
        order_side = AlpacaOrderSide(side.lower())
    except ValueError:
        return f"Invalid side: {side}. Must be 'buy' or 'sell'."
    
    # Validate time in force
    try:
        order_tif = AlpacaTimeInForce(time_in_force.lower())
    except ValueError:
        return f"Invalid time in force: {time_in_force}. Valid options are: day, gtc"
    
    # Create order request
    order_request = AlpacaOrderRequest(
        symbol=symbol,
        qty=float(quantity),
        side=order_side,
        type=AlpacaOrderType.STOP_LIMIT,
        time_in_force=order_tif,
        stop_price=float(stop_price),
        limit_price=float(limit_price)
    )
    
    try:
        order = calls.place_order(trading_client, order_request)
        
        return (
            f"Stop-limit order placed successfully!\n\n"
            f"Order ID: {order.id}\n"
            f"Symbol: {order.symbol}\n"
            f"Side: {order.side.value}\n"
            f"Type: {order.type.value}\n"
            f"Quantity: {order.qty}\n"
            f"Stop Price: ${order.stop_price:.2f}\n"
            f"Limit Price: ${order.limit_price:.2f}\n"
            f"Time in Force: {order.time_in_force.value}\n"
            f"Status: {order.status.value}\n"
            f"Created At: {order.created_at}\n"
        )
    except Exception as e:
        return f"Error placing stop-limit order: {str(e)}"


@mcp.tool()
def cancel_order(order_id: str) -> str:
    """
    Cancel an open order by its ID.
    
    Args:
        order_id: ID of the order to cancel
    
    Returns:
        Confirmation of cancellation
    """
    try:
        trading_client.cancel_order_by_id(order_id)
        return f"Order {order_id} has been successfully canceled."
    except Exception as e:
        return f"Error canceling order {order_id}: {str(e)}"


@mcp.tool()
def close_position(symbol: str) -> str:
    """
    Close an open position for a specific symbol.
    
    Args:
        symbol: Stock symbol to close position for
    
    Returns:
        Confirmation of position closure
    """
    try:
        # First check if position exists
        position = calls.get_position(trading_client, symbol)
        if not position:
            return f"No open position found for {symbol}."
        
        # Close the position
        trading_client.close_position(symbol)
        return f"Position for {symbol} has been successfully closed."
    except Exception as e:
        return f"Error closing position for {symbol}: {str(e)}"


@mcp.tool()
def get_portfolio_summary() -> str:
    """
    Get a comprehensive summary of the portfolio including account details and open positions.
    
    Returns:
        Portfolio summary with account and positions information
    """
    try:
        # Get account info
        account = calls.get_account(trading_client)
        
        # Get all positions
        positions = calls.get_positions(trading_client)
        
        # Generate summary
        summary = (
            f"Portfolio Summary\n"
            f"=================\n\n"
            f"Account Information:\n"
            f"-------------------\n"
            f"Status: {account.status}\n"
            f"Cash: ${account.cash:.2f}\n"
            f"Portfolio Value: ${account.portfolio_value:.2f}\n"
            f"Buying Power: ${account.buying_power:.2f}\n"
            f"Equity: ${account.equity:.2f}\n"
            f"Daytrade Count: {account.daytrade_count}\n"
            f"Pattern Day Trader: {account.pattern_day_trader}\n\n"
        )
        
        if positions:
            summary += f"Open Positions ({len(positions)}):\n-------------------\n"
            
            # Calculate total P/L and allocation
            total_pl = sum(pos.unrealized_pl for pos in positions)
            total_value = account.portfolio_value - account.cash
            
            for pos in positions:
                pl_percent = pos.unrealized_plpc * 100
                pl_sign = "+" if pos.unrealized_pl >= 0 else ""
                allocation = (pos.market_value / account.portfolio_value) * 100 if account.portfolio_value > 0 else 0
                
                summary += (
                    f"{pos.symbol} ({pos.side.value.upper()}):\n"
                    f"  Quantity: {pos.qty}\n"
                    f"  Avg Entry: ${pos.avg_entry_price:.2f}\n"
                    f"  Current: ${pos.current_price:.2f}\n"
                    f"  Value: ${pos.market_value:.2f} ({allocation:.2f}% of portfolio)\n"
                    f"  P/L: {pl_sign}${pos.unrealized_pl:.2f} ({pl_sign}{pl_percent:.2f}%)\n\n"
                )
            
            # Add overall P/L summary
            overall_pl_percent = (total_pl / total_value) * 100 if total_value > 0 else 0
            pl_sign = "+" if total_pl >= 0 else ""
            
            summary += (
                f"Overall Position Summary:\n"
                f"------------------------\n"
                f"Total Position Value: ${total_value:.2f}\n"
                f"Total Unrealized P/L: {pl_sign}${total_pl:.2f} ({pl_sign}{overall_pl_percent:.2f}%)\n"
                f"Cash Allocation: ${account.cash:.2f} ({(account.cash / account.portfolio_value) * 100:.2f}% of portfolio)\n"
            )
        else:
            summary += "No open positions."
        
        return summary
    except Exception as e:
        return f"Error generating portfolio summary: {str(e)}"


# ---- PROMPTS ----

@mcp.prompt()
def market_order_prompt(symbol: str, quantity: float, side: str) -> str:
    """Creates a prompt for placing a market order."""
    return f"""
I want to place a market order with the following details:

Symbol: {symbol}
Quantity: {quantity}
Side: {side}

Please execute this order for me and confirm once it's placed.
"""


@mcp.prompt()
def portfolio_analysis_prompt() -> str:
    """Creates a prompt for analyzing the current portfolio."""
    return """
Please analyze my current portfolio and provide the following:

1. A summary of my account status and buying power
2. A list of my current positions with their performance
3. An assessment of my portfolio allocation and diversification
4. Any recommendations for rebalancing or risk management

Please use the portfolio summary tool to gather the necessary information.
"""


@mcp.prompt()
def market_research_prompt(symbol: str) -> str:
    """Creates a prompt for researching a specific stock."""
    return f"""
I'd like to research {symbol} before making a trading decision. Could you:

1. Provide the current market quote for {symbol}
2. Show me recent price history using the Daily timeframe
3. Give me information about the asset (exchange, class, etc.)
4. If I already have a position in {symbol}, show me its details

Please use the appropriate resources to gather this information.
"""


# Run the server
if __name__ == "__main__":
    mcp.run(transport='stdio')