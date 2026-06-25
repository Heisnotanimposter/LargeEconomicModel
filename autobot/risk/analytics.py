import numpy as np
import logging

class AnalyticsEngine:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger("AnalyticsEngine")

    def calculate_sustainability_ratio(self, revenue, payout_obligations):
        """
        Calculates psi = R / H.
        - psi > 1: Surplus (Deflationary pressure)
        - psi < 1: Deficit (Tap into reserves)
        """
        if payout_obligations == 0:
            return float('inf')
        
        psi = revenue / payout_obligations
        return psi

    def calculate_var(self, portfolio_value, spot_vol, futures_vol, correlation, confidence_level=0.99, time_horizon=1):
        """
        Calculates Value at Risk (VaR) for a delta-neutral portfolio.
        VaR = Z * sigma(basis) * sqrt(T) * PortfolioValue
        """
        # Z-score for confidence level
        z_scores = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}
        z = z_scores.get(confidence_level, 2.33)

        # Variance of basis: sigma^2(basis) = sigma^2(spot) + sigma^2(futures) - 2 * rho * sigma(spot) * sigma(futures)
        basis_variance = (spot_vol**2) + (futures_vol**2) - (2 * correlation * spot_vol * futures_vol)
        basis_vol = np.sqrt(max(0, basis_variance))

        var = z * basis_vol * np.sqrt(time_horizon) * portfolio_value
        return var

    def calculate_composite_growth_score(self, defi_activity, staking_ratio, revenue):
        """
        Gt = 0.3 * DeFi + 0.3 * Staking + 0.4 * Revenue
        """
        # Normalized inputs assumed [0, 1]
        gt = (0.3 * defi_activity) + (0.3 * staking_ratio) + (0.4 * revenue)
        return gt
