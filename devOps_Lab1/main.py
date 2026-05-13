"""
DevOps Lab 1 - OpenAI API Python Client
Demonstrates direct API usage with temperature, max_tokens, and system message control.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client (reads OPENAI_API_KEY from environment)
client = OpenAI()


def get_response(user_message: str, temperature: float = 0.7, max_tokens: int = 256) -> str:
    """
    Send a message to the model and return the response text.

    Args:
        user_message: The user's input message.
        temperature: Controls randomness (0 = deterministic, 2 = very random).
        max_tokens: Maximum number of tokens in the response.

    Returns:
        The model's response as a string.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant specialized in Python and DevOps topics. "
                    "Keep your answers concise and practical."
                ),
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def compare_temperatures(prompt: str) -> None:
    """
    Send the same prompt at three different temperature levels and print all outputs
    side-by-side so differences are easy to observe.

    Args:
        prompt: The question or statement to send.
    """
    print("\n" + "=" * 60)
    print(f"Prompt: {prompt}")
    print("=" * 60)

    for temp in [0.0, 0.7, 1.5]:
        label = {0.0: "Deterministic (0.0)", 0.7: "Balanced   (0.7)", 1.5: "Creative   (1.5)"}[temp]
        print(f"\n[{label}]")
        result = get_response(prompt, temperature=temp, max_tokens=150)
        print(result)

    print("\n" + "=" * 60)


def interactive_chat() -> None:
    """
    Run a simple REPL that lets the user chat with the model interactively.
    Type 'exit' or 'quit' to stop. Type 'compare' to trigger a temperature comparison.
    """
    print("\n=== OpenAI Interactive Chat ===")
    print("Commands: 'exit' to quit | 'compare' to run temperature demo\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if user_input.lower() == "compare":
            topic = input("Enter a prompt for temperature comparison: ").strip()
            if topic:
                compare_temperatures(topic)
            continue

        response = get_response(user_input)
        print(f"\nAssistant: {response}\n")


if __name__ == "__main__":
    # --- Quick demo (runs once, then drops into interactive mode) ---
    print("Running temperature comparison demo...")
    compare_temperatures("Explain what a Docker container is in one sentence.")

    # --- Interactive session ---
    interactive_chat()
