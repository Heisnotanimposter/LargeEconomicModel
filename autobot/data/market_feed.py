import time
import requests
import logging

class MarketFeed:
    """
    Simulated market feed to pull data from internal sources or APIs.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.last_ts = datetime.now()
        self.last_price = 0.0
        self.missing_rate = 0.0
        self.logger = logging.getLogger("MarketFeed")

    def get_latest_tick(self, symbol="BTC-USDT"):
        """
        Mock tick. Real logic would call Upbit or Binance API.
        """
        # Example API Call (placeholder):
        # response = requests.get(f"https://api.upbit.com/v1/ticker?markets={symbol}")
        # data = response.json()
        
        # Simulated data:
        price = 65000.0 + (time.time() % 100)
        self.last_price = price
        self.last_ts = datetime.now()
        
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": self.last_ts.timestamp(),
            "volume": 1.23,
            "latency": 0.1 # Real latency estimation
        }

    def check_integrity(self, tick):
        if not tick:
            self.missing_rate = 1.0
            return False
            
        latency = time.time() - tick['timestamp']
        if latency > 5.0:
            self.logger.warning(f"Market data stale: {latency:.2f}s latency.")
            return False
            
        return True
