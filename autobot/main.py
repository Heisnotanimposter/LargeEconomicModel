import time
import logging
import signal
import sys
from autobot.risk.risk_manager import RiskManager
from autobot.monitor.watchdog import Watchdog
from autobot.monitor.notifier import Notifier
from autobot.executor.executor import Executor
from autobot.data.market_feed import MarketFeed
from autobot.llm_engine.llm_interface import MockLLM
from autobot.llm_engine.input_sanitizer import InputSanitizer
from autobot.risk.analytics import AnalyticsEngine
from autobot.executor.hedger import HedgingEngine
from autobot.executor.treasury import TreasuryManager
from autobot.monitor.circuit_breaker import CircuitBreaker

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("autobot/autobot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AutoBotMain")

class AutoBotEngine:
    def __init__(self):
        self.risk_manager = RiskManager("autobot/risk/constraints.json")
        self.notifier = Notifier()
        self.watchdog = Watchdog(self.risk_manager, self.notifier)
        self.executor = Executor(self.risk_manager, self.watchdog)
        self.market_feed = MarketFeed()
        self.llm = MockLLM() # Using Mock for now
        self.sanitizer = InputSanitizer()
        
        # Level 2 Integration
        self.analytics = AnalyticsEngine()
        self.hedger = HedgingEngine()
        self.treasury = TreasuryManager()
        self.circuit_breaker = CircuitBreaker(self.watchdog)
        
        self.running = True

    def stop(self):
        self.running = False

    def run_loop(self):
        logger.info("AutoBot 24/7 Engine STARTED.")
        
        while self.running:
            try:
                # 1. Heartbeat
                self.watchdog.heartbeat()

                # 2. Get Market Data
                tick = self.market_feed.get_latest_tick("BTC-USDT")
                if not self.market_feed.check_integrity(tick):
                    self.watchdog.check_health({'latency': 10.0}) # Trigger stale data
                    time.sleep(1)
                    continue

                # 3. System Health Check & Circuit Breaker
                self.watchdog.check_health({'latency': tick.get('latency', 0)})
                
                # Mock metrics for Level 2 Circuit Breaker
                composite_metrics = {
                    'tvl_outflow': 0.02, 
                    'gas_price': 30, 
                    'collateral_ratio': 1.5
                }
                self.circuit_breaker.evaluate_composite_risk(composite_metrics)
                
                if self.watchdog.is_safe_mode:
                    logger.warning("System in SAFE MODE. Waiting for manual reset...")
                    time.sleep(10)
                    continue

                # 4. Signal Generation (LLM)
                # In real scenario, we'd feed market summary text to LLM
                prompt = f"Market is currently at {tick['price']}. Symbol: {tick['symbol']}. Give signal."
                raw_signal = self.llm.generate_signal(prompt)
                signal = self.sanitizer.validate_output(raw_signal)

                # 5. Execution
                if signal != "WAIT":
                    logger.info(f"Signal received: {signal}. Passing to Executor.")
                    trade_res = self.executor.execute_signal(tick['symbol'], signal, tick)
                    
                    if trade_res:
                        # Level 2: Adjust Hedge
                        self.hedger.rebalance(self.executor.account_balance, tick['price'] * 0.99) # Mock futures price

                # Level 2: Treasury Analytics
                psi = self.analytics.calculate_sustainability_ratio(revenue=0.5, payout_obligations=0.4)
                logger.debug(f"Level 2 Metrics -> Sustainability Ratio (psi): {psi:.2f}")

                # 6. Sleep Interval (24/7 loop control)
                time.sleep(5) 

            except KeyboardInterrupt:
                logger.info("Shutdown signal received.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in loop: {e}")
                time.sleep(1)

        logger.info("AutoBot Engine SHUTDOWN.")

if __name__ == "__main__":
    bot = AutoBotEngine()
    
    # Handle OS signals
    def signal_handler(sig, frame):
        bot.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    bot.run_loop()
