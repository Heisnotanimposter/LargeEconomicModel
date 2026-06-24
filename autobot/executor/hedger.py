import logging

class HedgingEngine:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger("HedgingEngine")
        self.hedge_ratio = self.config.get("hedge_ratio", 1.0) # 1.0 = 100% Delta-Neutral
        self.positions = {"spot": 0.0, "short_perp": 0.0}

    def update_state(self, spot_price, futures_price):
        """
        Calculates the basis and P/L.
        P&L = (Spot1 - Futures1) - (Spot0 - Futures0)
        """
        basis = spot_price - futures_price
        self.logger.info(f"Current Basis: {basis:.4f} (Spot: {spot_price}, Futures: {futures_price})")
        return basis

    def rebalance(self, spot_position_value, futures_price):
        """
        Adjusts the short perpetual position to maintain delta-neutral state.
        """
        required_short_size = (spot_position_value * self.hedge_ratio) / futures_price
        
        current_short_size = self.positions["short_perp"]
        adjustment = required_short_size - current_short_size
        
        if abs(adjustment) > 0.0001:
            self.logger.info(f"Hedge Rebalance: Adjusting short perp by {adjustment:.6f}")
            self.positions["short_perp"] = required_short_size
            return adjustment
        
        return 0.0

    def get_net_delta(self, spot_price, futures_price):
        """
        Returns the directional delta. 0.0 means perfectly hedged.
        """
        spot_delta = self.positions["spot"] * spot_price
        short_delta = -self.positions["short_perp"] * futures_price
        return spot_delta + short_delta
