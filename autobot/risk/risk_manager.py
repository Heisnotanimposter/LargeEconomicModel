import json
import os
import logging
from datetime import datetime

class RiskManager:
    def __init__(self, config_path="autobot/risk/constraints.json"):
        self.config_path = config_path
        self.load_config()
        self.daily_loss = 0.0
        self.last_reset_date = datetime.now().date()
        self.logger = logging.getLogger("RiskManager")

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.max_daily_loss = self.config['max_daily_loss_usd']
            self.max_position_pct = self.config['max_position_pct']
            self.max_order_size = self.config['max_order_size']
            self.min_order_usd = self.config['min_order_usd']
            self.allowed_symbols = self.config['allowed_symbols']
        except Exception as e:
            print(f"Error loading config: {e}")
            # Fallback defaults
            self.max_daily_loss = 2.0
            self.max_position_pct = 0.1
            self.max_order_size = 0.01

    def _maybe_reset_daily(self):
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_loss = 0.0
            self.last_reset_date = current_date
            self.logger.info("Daily loss limit reset.")

    def can_place_order(self, account_balance, order):
        """
        Validates if an order can be placed based on risk rules.
        :param account_balance: Current USD balance
        :param order: Dictionary containing symbol, size, and price
        :return: (bool, reason)
        """
        self._maybe_reset_daily()

        symbol = order.get('symbol')
        size = order.get('size')
        price = order.get('price')
        order_value = size * price

        if symbol not in self.allowed_symbols:
            return False, f"symbol_not_allowed: {symbol}"

        if self.daily_loss >= self.max_daily_loss:
            return False, f"daily_loss_limit_reached: ${self.daily_loss:.2f}"

        if order_value < self.min_order_usd:
            return False, f"order_value_too_small: ${order_value:.2f}"

        if order_value > account_balance * self.max_position_pct:
            return False, f"position_pct_exceed: {order_value/account_balance:.4f} > {self.max_position_pct}"

        if size > self.max_order_size:
            return False, f"order_size_exceed: {size} > {self.max_order_size}"

        return True, "ok"

    def record_trade_result(self, pnl):
        """
        Records the outcome of a trade to track daily drawdown.
        """
        self._maybe_reset_daily()
        if pnl < 0:
            self.daily_loss += abs(pnl)
            self.logger.warning(f"Recorded loss: ${abs(pnl):.2f}. Total daily loss: ${self.daily_loss:.2f}")
        else:
            self.logger.info(f"Recorded profit: ${pnl:.2f}")

    def get_status(self):
        return {
            "daily_loss_usage": f"{self.daily_loss:.2f}/{self.max_daily_loss:.2f}",
            "last_reset": str(self.last_reset_date)
        }
