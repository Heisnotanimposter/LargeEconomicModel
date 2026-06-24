import logging
import time

class Executor:
    def __init__(self, risk_manager, watchdog, api_client=None):
        self.risk_manager = risk_manager
        self.watchdog = watchdog
        self.api_client = api_client # Mock for now
        self.account_balance = 5.0 # Test fund: $5
        self.logger = logging.getLogger("Executor")

    def execute_signal(self, symbol, signal, price_tick):
        """
        Translates a signal (BUY/SELL) into an order after risk validation.
        """
        if self.watchdog.is_safe_mode:
            self.logger.warning(f"Execution blocked: Safe Mode is ACTIVE.")
            return None

        if signal not in ["BUY", "SELL"]:
            return None

        # 1. Prepare Order
        # Example: Buy $1 worth of symbol
        order_size = 1.0 / price_tick['price'] 
        order = {
            "symbol": symbol,
            "side": signal,
            "size": order_size,
            "price": price_tick['price']
        }

        # 2. Risk Validation
        ok, reason = self.risk_manager.can_place_order(self.account_balance, order)
        if not ok:
            self.logger.warning(f"Risk Manager BLOCKED order: {reason}")
            return None

        # 3. Execution
        self.logger.info(f"PLACING ORDER: {signal} {order_size} {symbol} @ {price_tick['price']}")
        
        # In real mode:
        # response = self.api_client.create_order(symbol, side, size, price)
        # result = self._handle_response(response)
        
        # Simulation:
        self.watchdog.record_order()
        self.account_balance -= 1.0 if signal == "BUY" else -1.0
        
        return {
            "status": "success",
            "order_id": f"sim_{int(time.time())}",
            "symbol": symbol,
            "side": signal,
            "price": price_tick['price'],
            "size": order_size,
            "cost": 1.0
        }

    def _handle_response(self, response):
        """
        Handle API response and retries.
        """
        # Logic for slippage check, retry on 5xx, or enter Safe Mode on failure
        pass
