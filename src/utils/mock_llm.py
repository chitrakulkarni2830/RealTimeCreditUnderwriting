import re
import random

# =================================================================
# SMART MOCK LLM
# This class mimics the LangChain LLM interface but runs for FREE.
# It generates realistic agent reasoning based on the input text.
# =================================================================

class MockLLM:
    """
    A lightweight Mock LLM that simulates agentic behavior.
    Designed for zero-cost demos and local testing.
    """
    
    def __init__(self, model_name="MockGPT"):
        self.model_name = model_name

    def __call__(self, prompt, stop=None):
        return self.generate_response(prompt)

    def bind(self, **kwargs):
        # LangChain often calls .bind(), we just return self
        return self

    def invoke(self, input, config=None, **kwargs):
        # Handle different input formats from LangChain
        if isinstance(input, str):
            prompt = input
        elif isinstance(input, list):
            # Often a list of BaseMessages
            prompt = str(input[-1].content)
        else:
            prompt = str(input)
            
        response_text = self.generate_response(prompt)
        
        # Mocking the response structure LangChain expects
        class MockResponse:
            def __init__(self, content):
                self.content = content
        return MockResponse(response_text)

    def generate_response(self, prompt):
        """
        Determines the agent's goal from the prompt and generates a 
        context-aware mock response.
        """
        prompt_lower = prompt.lower()
        
        # --- Logic for AGGREGATOR AGENT ---
        if "fetch_utility_history" in prompt or "analyze_ecommerce_spending" in prompt:
            user_id_match = re.search(r'user\s*(?:id)?\s*(\d+)', prompt_lower)
            uid = user_id_match.group(1) if user_id_match else "101"
            
            # Logic: User 101 is slightly 'riskier' in our mock data
            if uid == "101":
                return f"I have analyzed User {uid}. They have 1 late utility payment. Spending volatility is moderate (188.23). Luxury ratio is 3.27, signifying high lifestyle leverage."
            else:
                return f"I have analyzed User {uid}. They have 0 late payments. Spending is very stable (volatility 45.12). Luxury ratio is 0.15, indicating conservative habits."

        # --- Logic for ANALYST AGENT ---
        elif "behavioral" in prompt_lower or "risk settings" in prompt_lower:
            if "late payment" in prompt_lower and "3.27" in prompt_lower:
                return "The behavioral profile for this user shows high risk. The high luxury-to-essential ratio combined with late utility payments suggests potential cash flow instability despite high spending levels."
            else:
                return "The user demonstrates a highly conservative and stable financial profile. Essential spending dominates the history, and utility bills are paid with 100% consistency."

        # --- Logic for UNDERWRITER AGENT (Final Decision) ---
        elif "decision summary" in prompt_lower:
            if "high risk" in prompt_lower or "3.27" in prompt_lower:
                return (
                    "**Paragraph 1 (Stability)**: The applicant shows inconsistent payment behavior for core utilities, with at least one recorded late payment in the recent quarter. This suggests a lack of prioritization for essential bills.\n\n"
                    "**Paragraph 2 (Habits)**: The alternative data reveals a high luxury-to-essential ratio (3.27). This indicates that the user prioritizes discretionary high-value items over essential staples, leading to high spending volatility.\n\n"
                    "**Paragraph 3 (Decision)**: Due to the observed volatility and payment lapses, we suggest a conservative initial credit limit of **$500**. Future increases are contingent on 6 months of on-time utility payments."
                )
            else:
                return (
                    "**Paragraph 1 (Stability)**: The applicant demonstrates a solid foundation of financial stability. Utility payments show 100% reliability, with no late entries in the documented history.\n\n"
                    "**Paragraph 2 (Habits)**: Spending habits are exceptionally disciplined. The Luxury-to-Essential ratio is very low, showing that the applicant maintains a strong margin for unexpected expenses.\n\n"
                    "**Paragraph 3 (Decision)**: Given the consistent patterns and low risk profile, we recommend a premium-tier starting credit limit of **$5,000**. The applicant is an ideal candidate for higher-limit products."
                )

        # Default fallback
        return "The analysis is complete and follows the requested guidelines. Data suggests the user is within acceptable risk parameters."
