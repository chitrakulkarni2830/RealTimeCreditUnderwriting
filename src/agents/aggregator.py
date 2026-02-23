from crewai import Agent
from src.tools.financial_tools import FinancialDataTools

# =================================================================
# AGENT 1: DATA AGGREGATOR
# Responsible for fetching raw alternative data from sources.
# =================================================================

class CreditAgents:
    
    def aggregator_agent(self):
        """
        Specialized in retrieving raw data from CSV and JSON sources.
        """
        return Agent(
            role='Senior Data Aggregator',
            goal='Accurately fetch and summarize alternative financial data for a given User ID.',
            backstory=(
                "You are an expert at extracting data from disparate sources. "
                "Your job is to provide a clean, high-level summary of a user's "
                "utility and e-commerce history to the Behavioral Analyst. "
                "You value precision and never miss a data point."
            ),
            tools=[FinancialDataTools.fetch_utility_history, FinancialDataTools.analyze_ecommerce_spending],
            verbose=True,
            allow_delegation=False,
            memory=True
        )
