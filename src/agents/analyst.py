from crewai import Agent

# =================================================================
# AGENT 2: BEHAVIORAL ANALYST
# Responsible for interpreting the raw data into behavioral patterns.
# =================================================================

class CreditAgents:
    
    def analyst_agent(self):
        """
        Interprets spending volatility and habits to create a health profile.
        """
        return Agent(
            role='Behavioral Financial Analyst',
            goal='Identify risk patterns and financial stability from spending habits.',
            backstory=(
                "You are a specialist in consumer psychology and financial behavior. "
                "You don't just look at numbers; you look for 'why' people spend. "
                "High volatility worries you, while consistent utility payments impress you. "
                "Your analysis is the foundation for the final credit decision."
            ),
            verbose=True,
            allow_delegation=False,
            memory=True
        )
