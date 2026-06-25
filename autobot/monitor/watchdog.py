import time
import logging
from datetime import datetime

class Watchdog:
    def __init__(self, risk_manager, notifier, config=None):
        self.risk_manager = risk_manager
        self.notifier = notifier
        self.config = config or {}
        self.last_heartbeat = time.time()
        self.is_safe_mode = False
        self.logger = logging.getLogger("Watchdog")
        
        # Thresholds
        self.latency_threshold = self.config.get("latency_threshold", 5.0) # seconds
        self.max_orders_per_minute = self.config.get("max_orders_per_minute", 2)
        self.last_order_timestamps = []

    def enter_safe_mode(self, reason):
        if not self.is_safe_mode:
            self.is_safe_mode = True
            msg = f"CRITICAL: Entering Safe Mode! Reason: {reason}"
            self.logger.critical(msg)
            self.notifier.alert(msg, level="CRITICAL")
            # Logic to halt all trading/cancel orders would go here
            self._halt_trading()

    def _halt_trading(self):
        self.logger.info("Halt command sent to Executor.")

    def exit_safe_mode(self):
        self.is_safe_mode = False
        self.logger.info("Safe Mode exited manually.")

    def check_health(self, state):
        """
        Main monitoring loop call.
        :param state: Dictionary with market/system stats (latency, order_count, etc.)
        """
        # 1. Latency Check
        if state.get('latency', 0) > self.latency_threshold:
            self.enter_safe_mode(f"High network latency: {state['latency']}s")

        # 2. Risk Check
        daily_loss = self.risk_manager.daily_loss
        if daily_loss >= self.risk_manager.max_daily_loss:
            self.enter_safe_mode(f"Daily loss limit hit: ${daily_loss:.2f}")

        # 3. Order Frequency Check
        current_time = time.time()
        # Clean up old timestamps
        self.last_order_timestamps = [t for t in self.last_order_timestamps if current_time - t < 60]
        if len(self.last_order_timestamps) >= self.max_orders_per_minute:
            self.enter_safe_mode(f"Order frequency threshold hit: {len(self.last_order_timestamps)} orders/min")

    def record_order(self):
        self.last_order_timestamps.append(time.time())

    def heartbeat(self):
        self.last_heartbeat = time.time()
        # self.logger.debug("Heartbeat recorded.")
