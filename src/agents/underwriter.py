from crewai import Agent

# =================================================================
# AGENT 3: SENIOR UNDERWRITER
# Responsible for the final decision and human-readable summary.
# =================================================================

class CreditAgents:
    
    def underwriter_agent(self):
        """
        Synthesizes the behavioral profile into a final credit limit decision.
        """
        return Agent(
            role='Senior Credit Underwriter',
            goal='Provide a fair, justifiable 3-paragraph decision summary for a credit limit.',
            backstory=(
                "You are a veteran of the fintech industry with 20 years of experience. "
                "You balances risk with opportunity. You are known for your clear, "
                "3-paragraph summaries that explain 'Why' a specific limit was set. "
                "Your word is final."
            ),
            verbose=True,
            allow_delegation=False,
            memory=True
        )
