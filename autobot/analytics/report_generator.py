import json
import logging
from datetime import datetime

class ReportGenerator:
    def __init__(self, log_path="autobot/autobot.log"):
        self.log_path = log_path
        self.logger = logging.getLogger("ReportGenerator")

    def generate_performance_report(self, risk_manager, executor, analytics):
        """
        Summarizes the state of the bot and its performance metrics.
        """
        status = risk_manager.get_status()
        
        report = {
            "timestamp": str(datetime.now()),
            "account": {
                "initial_balance": 5.0,
                "current_balance": executor.account_balance,
                "total_pnl": executor.account_balance - 5.0,
                "pnl_percentage": ((executor.account_balance / 5.0) - 1) * 100
            },
            "risk_metrics": {
                "daily_loss_usage": status["daily_loss_usage"],
                "last_daily_reset": status["last_reset"]
            },
            "sustainability": {
                "calculated_psi": analytics.calculate_sustainability_ratio(revenue=0.5, payout_obligations=0.4) # Mock
            }
        }
        
        report_path = f"autobot/analytics/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=4)
            self.logger.info(f"Performance report generated at: {report_path}")
            return report
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return None

    def create_markdown_summary(self, report):
        """
        Creates a readable markdown summary for the user.
        """
        if not report:
            return "No report data available."
            
        summary = f"""
# AutoBot Performance Summary
**Timestamp:** {report['timestamp']}

## Account Overview
- **Initial Balance:** ${report['account']['initial_balance']:.2f}
- **Current Balance:** ${report['account']['current_balance']:.2f}
- **Total PnL:** ${report['account']['total_pnl']:.2f} ({report['account']['pnl_percentage']:.2f}%)

## Risk & Sustainability
- **Daily Loss Usage:** {report['risk_metrics']['daily_loss_usage']}
- **Sustainability Ratio ($\psi$):** {report['sustainability']['calculated_psi']:.2f}

## Legend
- **$\psi > 1$**: System is in surplus.
- **$\psi < 1$**: System is in deficit.
"""
        return summary
