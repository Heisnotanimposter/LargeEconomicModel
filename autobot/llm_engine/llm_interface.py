import logging
from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def generate_signal(self, prompt: str) -> str:
        pass

class MockLLM(LLMInterface):
    """Simple mock for testing without local weights."""
    def generate_signal(self, prompt: str) -> str:
        # Simulate local LLM response
        if "market is crashing" in prompt.lower():
            return "SELL"
        if "market is mooning" in prompt.lower():
            return "BUY"
        return "WAIT"

class LocalGemmaLLM(LLMInterface):
    """Placeholder for local Gemma-3 1b inference."""
    def __init__(self, model_path="gemma-3-pytorch-gemma-3-1b-it-v1"):
        self.model_path = model_path
        self.logger = logging.getLogger("LocalGemmaLLM")
        # In a real setup, we would load the weights here:
        # import torch
        # self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.logger.info(f"Initialized LocalGemmaLLM with path: {model_path}")

    def generate_signal(self, prompt: str) -> str:
        """
        Placeholder for actual inference logic.
        """
        # Logic to call the model would go here:
        # tokens = self.tokenizer.encode(prompt)
        # output = self.model.generate(tokens)
        self.logger.warning("LocalGemmaLLM.generate_signal() is in placeholder mode.")
        return "WAIT" # Default safer behavior
