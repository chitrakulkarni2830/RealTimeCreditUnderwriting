import os
from crewai import Crew, Task, Process
from src.agents.aggregator import CreditAgents as AggregatorAgents
from src.agents.analyst import CreditAgents as AnalystAgents
from src.agents.underwriter import CreditAgents as UnderwriterAgents
from src.utils.mock_llm import MockLLM

# =================================================================
# CREW ORCHESTRATOR
# Ties agents and tasks together into a cohesive workflow.
# =================================================================

class CreditCrew:
    
    def __init__(self, user_id):
        self.user_id = user_id
        
        # Initialize agents using the standard CrewAI framework
        # These will use the OPENAI_API_KEY from the environment
        self.aggregator = AggregatorAgents().aggregator_agent()
        self.analyst = AnalystAgents().analyst_agent()
        self.underwriter = UnderwriterAgents().underwriter_agent()

    def run(self):
        """
        Defines the sequential process for underwriting.
        """
        
        # TASK 1: Data Fetching and Summarization
        data_task = Task(
            description=(
                f"Retrieve and summarize the alternative data for User ID {self.user_id}. "
                "You must use the 'fetch_utility_history' and 'analyze_ecommerce_spending' tools. "
                "Provide a clean data profile including utility reliability and spending volatility."
            ),
            expected_output="A structured summary of utility payments and e-commerce behavior.",
            agent=self.aggregator
        )

        # TASK 2: Behavioral Analysis
        analysis_task = Task(
            description=(
                "Analyze the summary provided by the Data Aggregator. "
                "Identify if the user shows 'High Risk' behavior (volatile luxury spending) "
                "or 'Conservative' behavior (consistent utility payments). "
                "Define their financial health profile."
            ),
            expected_output="A detailed behavioral profile highlighting risk factors and stability markers.",
            agent=self.analyst
        )

        # TASK 3: Final Underwriting Decision
        underwriting_task = Task(
            description=(
                "Review the behavioral profile and make a final credit limit decision. "
                "suggest a limit of either $500, $2000, or $5000. "
                "Provide a 3-paragraph summary justifying your decision based on the alternative data."
            ),
            expected_output="A professional 3-paragraph Decision Summary formatted in Markdown.",
            agent=self.underwriter
        )

        # ORCHESTRATE THE CREW
        credit_crew = Crew(
            agents=[self.aggregator, self.analyst, self.underwriter],
            tasks=[data_task, analysis_task, underwriting_task],
            process=Process.sequential, # Tasks are completed one after another
            verbose=True
        )

        return credit_crew.kickoff()
