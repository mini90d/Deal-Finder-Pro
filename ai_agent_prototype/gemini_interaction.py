import os
import google.generativeai as genai

# Load the API key from an environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

# Global variable to hold the initialized model
generative_model = None

def configure_gemini(model_name: str = "gemini-pro"):
    """
    Configures the Gemini client and initializes the specified model.

    Args:
        model_name: The name of the Gemini model to use (e.g., "gemini-pro").

    Returns:
        True if configuration is successful, False otherwise.
    """
    global generative_model
    if not API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set this environment variable with your Google Gemini API key.")
        return False

    try:
        genai.configure(api_key=API_KEY)
        generative_model = genai.GenerativeModel(model_name)
        print(f"Gemini client configured successfully with model: {model_name}")
        return True
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")
        generative_model = None
        return False

def generate_text_from_prompt(prompt: str):
    """
    Sends a prompt to the configured Gemini API model and returns the generated text.

    Args:
        prompt: The text prompt to send to the model.

    Returns:
        A string containing the model's response, or an error message if issues occur.
    """
    global generative_model
    if not generative_model:
        print("Error: Gemini model not configured. Please call configure_gemini() first.")
        return "Error: Model not configured."

    print(f"\nSending prompt to Gemini: '{prompt}'")
    try:
        response = generative_model.generate_content(prompt)
        # Handle cases where the response might not have text or parts
        if response.parts:
            return response.text
        elif response.candidates and response.candidates[0].content.parts: # Check deeper for content
             return response.candidates[0].content.parts[0].text
        else:
            # Log the full response for debugging if text is not directly accessible
            print(f"Warning: Could not directly extract text from response. Full response: {response}")
            # Attempt to access prompt feedback if content is blocked
            if response.prompt_feedbacks:
                for feedback in response.prompt_feedbacks:
                    if feedback.block_reason:
                        return f"Error: Prompt blocked due to {feedback.block_reason_message or feedback.block_reason}."
            return "Error: No text content found in the response or prompt was blocked."

    except Exception as e:
        print(f"Error interacting with Gemini API: {e}")
        return f"Error: Could not get response from Gemini API. Details: {str(e)}"

def main():
    """
    Main function to demonstrate Gemini API interaction.
    """
    # Configure with the default "gemini-pro" model
    if not configure_gemini():
        print("Exiting due to configuration error.")
        return

    example_prompt_1 = "Explain quantum computing in simple terms. Keep it concise, like one paragraph."
    response_1 = generate_text_from_prompt(example_prompt_1)
    print(f"\nModel response for prompt 1:\n{response_1}")

    example_prompt_2 = "What are some common use cases for AI in software development?"
    response_2 = generate_text_from_prompt(example_prompt_2)
    print(f"\nModel response for prompt 2:\n{response_2}")

    # Example of a potentially problematic prompt (to test safety feedback)
    # Depending on the API's safety settings, this might be blocked or return a generic response.
    # example_prompt_3 = "Tell me something inappropriate."
    # response_3 = generate_text_from_prompt(example_prompt_3)
    # print(f"\nModel response for prompt 3:\n{response_3}")

if __name__ == "__main__":
    main()
