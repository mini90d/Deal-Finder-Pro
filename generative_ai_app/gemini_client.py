import os
import google.generativeai as genai

# Load the API key from an environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

# Global variable to hold the initialized model, initialized to None
generative_model = None
is_configured = False

def ensure_configured(model_name: str = "gemini-pro"):
    """
    Ensures the Gemini client is configured. If not already configured,
    it attempts to configure it.

    Args:
        model_name: The name of the Gemini model to use if configuration is needed.

    Returns:
        True if configuration is successful or already configured, False otherwise.
    """
    global generative_model, is_configured

    if is_configured and generative_model:
        # If a specific model is requested and it's different from the current one, reconfigure.
        # For simplicity in this version, we assume if it's configured, it's with the desired model.
        # A more robust implementation might check generative_model.model_name if accessible
        # or always reconfigure if model_name differs from a stored configured_model_name.
        if generative_model.model_name != model_name: #This might need adjustment based on actual SDK object
             print(f"Switching model configuration to {model_name}")
             is_configured = False # Force reconfiguration for the new model
        else:
            return True

    if not API_KEY:
        print("CRITICAL: GEMINI_API_KEY environment variable not set.")
        # Log this error in a real app
        return False

    try:
        print(f"Configuring Gemini client with API key and model: {model_name}...")
        genai.configure(api_key=API_KEY)
        generative_model = genai.GenerativeModel(model_name)
        is_configured = True
        print(f"Gemini client configured successfully with model: {model_name}")
        return True
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")
        generative_model = None
        is_configured = False
        return False

def generate_text_from_prompt(prompt: str, model_name: str = "gemini-pro"):
    """
    Sends a prompt to the Gemini API using the specified model and returns the generated text.
    It ensures the client is configured before making a call.

    Args:
        prompt: The text prompt to send to the model.
        model_name: The name of the Gemini model to use (e.g., "gemini-pro").

    Returns:
        A string containing the model's response, or an error message if issues occur.
    """
    global generative_model

    if not ensure_configured(model_name):
        return "Error: Gemini client not configured. Please check API key and configuration."

    if not generative_model: # Should be caught by ensure_configured, but as a safeguard
        return "Error: Model not available after configuration attempt."

    print(f"\nSending prompt to Gemini (model: {generative_model.model_name}): '{prompt}'")
    try:
        response = generative_model.generate_content(prompt)

        if response.parts:
            return response.text
        elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        else:
            # Check for blocked prompt
            if response.prompt_feedbacks:
                for feedback in response.prompt_feedbacks:
                    if feedback.block_reason:
                        block_reason_message = feedback.block_reason.name # Using .name for enum
                        if hasattr(feedback, 'block_reason_message') and feedback.block_reason_message:
                             block_reason_message = feedback.block_reason_message
                        print(f"Warning: Prompt blocked due to {block_reason_message}. Full response: {response}")
                        return f"Error: Prompt blocked due to {block_reason_message}."

            print(f"Warning: Could not directly extract text from response. Full response: {response}")
            return "Error: No text content found in the response, or the prompt was blocked without specific feedback reason."

    except Exception as e:
        print(f"Error interacting with Gemini API: {e}")
        return f"Error: Could not get response from Gemini API. Details: {str(e)}"

# main function for standalone testing of this module
if __name__ == '__main__':
    print("Running gemini_client.py for testing purposes...")

    # The ensure_configured function will be called by generate_text_from_prompt
    # It relies on GEMINI_API_KEY being set in the environment.
    # If you want to test this directly, ensure GEMINI_API_KEY is set before running.

    if not os.getenv("GEMINI_API_KEY"):
        print("Note: GEMINI_API_KEY is not set. API calls will fail configuration.")
        print("Set GEMINI_API_KEY and run again for a full test.")
        # Example of how configuration would be triggered:
        if ensure_configured():
             print("Test configuration successful.")
        else:
             print("Test configuration failed. See errors above.")
    else:
        print(f"GEMINI_API_KEY found. Attempting to generate text...")
        example_prompt_1 = "Explain quantum computing in one sentence."
        response_1 = generate_text_from_prompt(example_prompt_1)
        print(f"\nTest Model response for prompt 1:\n{response_1}")

        example_prompt_2 = "What is the capital of France?"
        # Example of using a different model if needed, though ensure_configured
        # would ideally handle model switching more robustly if that's a frequent use case.
        # For now, it reconfigures if model_name changes.
        response_2 = generate_text_from_prompt(example_prompt_2, model_name="gemini-pro")
        print(f"\nTest Model response for prompt 2:\n{response_2}")

        # Test a potentially problematic prompt (if safety settings are strict)
        # response_3 = generate_text_from_prompt("Tell me how to do something dangerous.")
        # print(f"\nTest Model response for prompt 3:\n{response_3}")
