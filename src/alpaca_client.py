import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from alpaca.trading.client import TradingClient
from alpaca.data import CryptoHistoricalDataClient, StockHistoricalDataClient, OptionHistoricalDataClient

# Load environment variables
load_dotenv()

# Base class for SQLAlchemy models
Base = declarative_base()

class AlpacaClient:
    _instance = None
    _trading_client = None
    _crypto_client = None
    _stock_client = None
    
    def __new__(cls):
        """Ensure only one instance of AlpacaClient is created."""
        if cls._instance is None:
            cls._instance = super(AlpacaClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            api_key = os.getenv('ALPACA_PAPER_API_KEY')
            secret_key = os.getenv('ALPACA_PAPER_API_SECRET')
            self._trading_client = TradingClient(api_key, secret_key, paper=True)
            self._crypto_client = CryptoHistoricalDataClient()
            self._stock_client = StockHistoricalDataClient(api_key, secret_key)
            
        except Exception as e:
            raise Exception(f"Failed to initialize Alpaca client: {str(e)}")
        
    def trading_client(self):
        """Get the Alpaca TradingClient instance."""
        return self._trading_client
    
    def crypto_client(self):
        """Get the Alpaca CryptoHistoricalDataClient instance."""
        return self._crypto_client
    
    def stock_client(self):
        """Get the Alpaca StockHistoricalDataClient instance."""
        return self._stock_client
    
    
if __name__ == "__main__":
    from alpaca.data.requests import CryptoLatestQuoteRequest

    # no keys required
    client = CryptoHistoricalDataClient()

    # single symbol request
    request_params = CryptoLatestQuoteRequest(symbol_or_symbols="ETH/USD")

    latest_quote = client.get_crypto_latest_quote(request_params)

    # must use symbol to access even though it is single symbol
    latest_quote["ETH/USD"].ask_price
    
    print(latest_quote)