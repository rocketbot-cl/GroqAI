from groq_client import get_client  # Import function to get client
import traceback  # For capturing error traces
from groq.resources.models import Models  # type: ignore


def generate_text(prompt, model, result_var, temperature, max_tokens, stop_sequence, SetVar, PrintException):
    """
    Generate text using the groq AI client and assign it to the specified variable.

    :param prompt: The input prompt for text generation.
    :param model: The model to use for text generation.
    :param result_var: Name of the variable to store the generated text.
    :param temperature: Sampling temperature for text generation.
    :param max_tokens: Maximum number of tokens to generate.
    :param stop_sequence: Optional stop sequence to end text generation.
    :param SetVar: Function to set variables in Rocketbot.
    :param PrintException: Function to print exceptions in Rocketbot.
    """
    try:
        # Get the client
        client = get_client()
        if not client:
            raise Exception(
                "You must connect to groq AI before using this command. Please run the connection module first.")

        # Validate required parameters
        if not prompt or not model:
            raise Exception(
                "You must provide both a prompt and a model to generate text.")

        # Create the user message
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Generate text using the `chat.complete` method
        response = client.chat.complete(
            model=model,
            messages=messages,
            temperature=float(temperature or 0.7),
            max_tokens=int(max_tokens or 100),
            stop=[stop_sequence] if stop_sequence else None
        )

        # Debug: Print the full response and the generated message content
        print("DEBUG: response =", response)
        print("DEBUG: response.choices[0].message.content =",
              response.choices[0].message.content)

        # Access the generated message content
        generated_text = response.choices[0].message.content

        # Assign the result to the specified Rocketbot variable
        SetVar(result_var, generated_text)

    except Exception as e:
        # On failure, set the result variable to None and raise the exception
        SetVar(result_var, None)
        print("Error generating text with groq AI:")
        print(traceback.format_exc())  # Print full error trace
        PrintException()

        if isinstance(e, HTTPValidationError):
            raise Exception(
                "Some parameters are not valid. Please check your parameters and try again.")
        else:
            raise e
