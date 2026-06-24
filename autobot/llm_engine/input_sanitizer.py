import re

class InputSanitizer:
    def __init__(self, config=None):
        self.config = config or {}
        self.blacklist = [
            r"import\s+os", r"eval\(", r"exec\(", r"subprocess",
            r"rm\s+-rf", r"http://", r"https://", r"ssh\s+",
            r"<script", r"javascript:", r"\.system\("
        ]
        self.max_length = 2000

    def sanitize(self, prompt):
        """
        Cleans and validates the prompt before sending to the LLM.
        """
        # 1. Length check
        if len(prompt) > self.max_length:
            return "Prompt too long (security filter applied)."

        # 2. Pattern matching for malicious content
        for pattern in self.blacklist:
            if re.search(pattern, prompt, re.IGNORECASE):
                return "Security violation: blocked pattern detected."

        # 3. Whitelist check (optional, can be added later)
        
        return prompt

    def validate_output(self, output):
        """
        Ensures the LLM output is a valid trading signal.
        """
        output = output.strip().upper()
        allowed_actions = ["BUY", "SELL", "WAIT", "PENDING"]
        
        for action in allowed_actions:
            if action in output:
                return action
        
        return "WAIT" # Default conservative action
