import os
import argparse
from src.agents import deepagent
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file in the repo root
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--output-file", required=True)
    args = parser.parse_args()

    with open(args.prompt_file, 'r') as f:
        prompt = f.read()

    api_key = None
    if args.provider.lower() == "gemini" or args.provider.lower() == "google":
        api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    elif args.provider.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY")

    agent = deepagent.SDLCFlexibleAgent(
        provider=args.provider,
        api_key=api_key,
        model=args.model,
        dry_run=False
    )
    response = agent.run(prompt)

    with open(args.output_file, 'w') as f:
        f.write(response.get('output', ''))

if __name__ == "__main__":
    main()
