import logging

class TreasuryManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger("TreasuryManager")
        
        # Default Balancer-style smart pool index (e.g., 90% Native, 10% Fee Asset)
        self.target_index = self.config.get("target_index", {"native": 0.90, "fee_asset": 0.10})
        self.fdv_thresholds = self.config.get("fdv_thresholds", {
            "low": 1.0e9,  # <$1B: Aggressive buyback
            "mid": 2.5e9   # >$2.5B: Restrained buyback
        })

    def calculate_buyback_allocation(self, current_fdv, revenue):
        """
        Adjusts buyback intensity based on FDV/PS valuation as per research.
        """
        if current_fdv <= self.fdv_thresholds["low"]:
            allocation_pct = 1.0 # 100% of revenue
        elif current_fdv >= self.fdv_thresholds["mid"]:
            allocation_pct = 0.4 # 40% of revenue
        else:
            # Linear scaling between thresholds
            low = self.fdv_thresholds["low"]
            mid = self.fdv_thresholds["mid"]
            allocation_pct = 1.0 - (0.6 * (current_fdv - low) / (mid - low))
            
        return revenue * allocation_pct

    def rebalance_pool(self, current_balances, token_prices):
        """
        Simulated rebalance of a 'Buyback and Make' smart pool.
        """
        total_value = (current_balances["native"] * token_prices["native"]) + \
                      (current_balances["fee_asset"] * token_prices["fee_asset"])
        
        target_native_value = total_value * self.target_index["native"]
        current_native_value = current_balances["native"] * token_prices["native"]
        
        diff_value = target_native_value - current_native_value
        
        if abs(diff_value) > total_value * 0.01: # 1% threshold for rebalance
            trade_size = abs(diff_value) / token_prices["native"]
            side = "BUY" if diff_value > 0 else "SELL"
            self.logger.info(f"Pool Rebalance Triggered: {side} {trade_size:.4f} Native to restore 90/10 index.")
            return {"side": side, "size": trade_size}
        
        return None
