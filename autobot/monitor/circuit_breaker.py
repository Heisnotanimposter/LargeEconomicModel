import logging

class CircuitBreaker:
    def __init__(self, watchdog, config=None):
        self.watchdog = watchdog
        self.config = config or {}
        self.logger = logging.getLogger("CircuitBreaker")
        
        # Thresholds
        self.tvl_outflow_threshold = self.config.get("tvl_outflow_threshold", 0.10) # 10% drop
        self.gas_spike_threshold = self.config.get("gas_spike_threshold", 500) # 500 gwei
        self.collateral_ratio_threshold = self.config.get("min_collateral_ratio", 1.20)

    def evaluate_composite_risk(self, metrics):
        """
        Monitors composite risk scores including TVL outflow, gas spikes, and collateral ratios.
        Logic: if (risk_score > threshold) { trigger_breaker(); }
        """
        reasons = []
        
        # 1. TVL Outflow Check
        if metrics.get('tvl_outflow', 0) > self.tvl_outflow_threshold:
            reasons.append(f"High TVL Outflow: {metrics['tvl_outflow']*100:.1f}%")
            
        # 2. Gas Spike Check
        if metrics.get('gas_price', 0) > self.gas_spike_threshold:
            reasons.append(f"Network Congestion: {metrics['gas_price']} Gwei")
            
        # 3. Collateralization Ratio check
        if metrics.get('collateral_ratio', 2.0) < self.collateral_ratio_threshold:
            reasons.append(f"Low Collateral Ratio: {metrics['collateral_ratio']:.2f}")

        if reasons:
            reason_str = " | ".join(reasons)
            self.logger.critical(f"Circuit Breaker TRIGGERED: {reason_str}")
            self.watchdog.enter_safe_mode(f"Circuit Breaker: {reason_str}")
            return True
            
        return False
