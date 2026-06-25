import pytest
from autobot.risk.analytics import AnalyticsEngine
from autobot.executor.hedger import HedgingEngine
from autobot.executor.treasury import TreasuryManager
from autobot.monitor.circuit_breaker import CircuitBreaker
from autobot.monitor.watchdog import Watchdog
from autobot.risk.risk_manager import RiskManager
from autobot.monitor.notifier import Notifier

@pytest.fixture
def level2_setup():
    rm = RiskManager("autobot/risk/constraints.json")
    notifier = Notifier()
    wd = Watchdog(rm, notifier)
    analytics = AnalyticsEngine()
    hedger = HedgingEngine({"hedge_ratio": 1.0})
    treasury = TreasuryManager()
    breaker = CircuitBreaker(wd)
    return analytics, hedger, treasury, breaker, wd

def test_sustainability_ratio_calculation(level2_setup):
    analytics, _, _, _, _ = level2_setup
    psi = analytics.calculate_sustainability_ratio(revenue=1000, payout_obligations=500)
    assert psi == 2.0
    
    psi_low = analytics.calculate_sustainability_ratio(revenue=100, payout_obligations=500)
    assert psi_low == 0.2

def test_var_calculation(level2_setup):
    analytics, _, _, _, _ = level2_setup
    # Portfolio: $10,000, Spot Vol: 2%, Futures Vol: 2.1%, Corr: 0.99
    var = analytics.calculate_var(10000, 0.02, 0.021, 0.99)
    assert var > 0
    assert var < 10000 # Should be a fraction of the portfolio

def test_delta_neutral_rebalance(level2_setup):
    _, hedger, _, _, _ = level2_setup
    
    # 1. Open spot position $5000
    hedger.positions["spot"] = 1.0 # 1 BTC @ $5000
    
    # 2. Futures price $5100
    adj = hedger.rebalance(5000, 5100)
    
    # Should short ~0.98 BTC to match $5000 value
    assert hedger.positions["short_perp"] > 0
    assert abs(hedger.get_net_delta(5000, 5100)) < 1.0 # Significant reduction in delta

def test_valuation_sensitive_buyback(level2_setup):
    _, _, treasury, _, _ = level2_setup
    
    # FDV $500M (Low) -> 100% allocation
    alloc_low = treasury.calculate_buyback_allocation(500e6, 1000)
    assert alloc_low == 1000
    
    # FDV $3B (High) -> 40% allocation
    alloc_high = treasury.calculate_buyback_allocation(3e9, 1000)
    assert alloc_high == 400

def test_circuit_breaker_gas_spike(level2_setup):
    _, _, _, breaker, wd = level2_setup
    
    metrics = {'gas_price': 600} # Spike!
    triggered = breaker.evaluate_composite_risk(metrics)
    
    assert triggered == True
    assert wd.is_safe_mode == True
