import os
from dotenv import load_dotenv

# =================================================================
# GOLD STANDARD CREDIT UNDERWRITING AGENT
# Main Entry Point
# =================================================================

def main():
    # Load Environment Variables
    load_dotenv()
    
    print("\n" + "="*50)
    print("      REAL-TIME CREDIT UNDERWRITING AGENT")
    print("="*50 + "\n")
    
    # User Input
    user_id = input("Enter User ID to assess (e.g., 101, 102): ")
    
    if not user_id:
        print("Error: User ID is required.")
        return

    # Check for API Key to determine mode
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[FREE TIER] No OpenAI API Key found. Running 'Gold Standard Simulation Mode'...")
        try:
            # We defer all imports that might trigger library initialization
            from src.utils.simulator import LocalCreditSimulator
            simulator = LocalCreditSimulator(user_id=user_id)
            result = simulator.run()
        except Exception as e:
            print(f"\n[ERROR] Simulation failed: {str(e)}")
            return
    else:
        print(f"\n[INFO] Starting agentic workflow for User {user_id}...")
        try:
            # We only load CrewAI if an API key is present
            from src.crew import CreditCrew
            crew_orchestrator = CreditCrew(user_id=user_id)
            result = crew_orchestrator.run()
        except Exception as e:
            print(f"\n[ERROR] An error occurred during the workflow: {str(e)}")
            return
        
    print("\n" + "="*50)
    print("           FINAL DECISION SUMMARY")
    print("="*50 + "\n")
    print(result)
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
