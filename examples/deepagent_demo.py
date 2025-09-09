"""
Example script demonstrating the SDLCFlexibleAgent.

This script shows how to:
- Initialize the SDLCFlexibleAgent.
- Run the agent with a simple prompt.
- Run the agent with a session ID to demonstrate conversational memory.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.deepagent import SDLCFlexibleAgent
from dotenv import load_dotenv

def main():
    """Main demonstration function."""
    print("🤖 SDLCFlexibleAgent Demo")
    print("=" * 50)

    # Load environment variables from .env file
    load_dotenv()

    # --- Basic Usage ---
    print("\n--- Basic Usage ---")
    try:
        # Initialize the agent (provider and model are loaded from config/model_config.yaml)
        agent = SDLCFlexibleAgent()

        prompt = "What is the capital of France?"
        print(f"Running prompt: '{prompt}'")
        result = agent.run(prompt)
        print("Agent result:", result)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print("  Please ensure you have a valid API key in your .env file.")


    # --- Conversational Memory with Session ID ---
    print("\n--- Conversational Memory with Session ID ---")
    try:
        # Initialize the agent again for a new conversation
        agent = SDLCFlexibleAgent()
        session_id = "my-test-session"

        # First turn
        prompt1 = "My name is Bob."
        print(f"Running prompt 1: '{prompt1}' (session: {session_id})")
        result1 = agent.run(prompt1, session_id=session_id)
        print("Agent result 1:", result1)

        # Second turn
        prompt2 = "What is my name?"
        print(f"\nRunning prompt 2: '{prompt2}' (session: {session_id})")
        result2 = agent.run(prompt2, session_id=session_id)
        print("Agent result 2:", result2)

        print("\nNote how the agent remembers the name 'Bob' in the second turn.")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        print("  Please ensure you have a valid API key in your .env file.")


if __name__ == "__main__":
    main()
