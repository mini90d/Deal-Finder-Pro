from flask import Flask, request, jsonify, render_template
from gemini_client import generate_text_from_prompt
from image_client import generate_image_from_prompt

app = Flask(__name__)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """
    Receives a prompt, autonomy level, and output type from the frontend.
    Processes it and calls the appropriate client (text or image generation).
    Returns the generated content or an error message with appropriate HTTP status codes.
    """
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid request: No JSON data received.'}), 400

            user_prompt = data.get('prompt')
            autonomy_level = data.get('autonomy_level', 'direct')
            output_type = data.get('output_type', 'text')

            if not user_prompt or not user_prompt.strip():
                return jsonify({'error': 'Prompt is required and cannot be empty.'}), 400

            print(f"Received request for /generate: prompt='{user_prompt[:50]}...', autonomy_level='{autonomy_level}', output_type='{output_type}'")

            final_prompt = user_prompt

            if autonomy_level == 'assistant':
                final_prompt = f"You are a helpful assistant. The user wants to: '{user_prompt}'. Please provide 3 concise suggestions or actionable steps to help the user achieve this."
                print(f"Assistant mode: Modified prompt to: '{final_prompt[:100]}...'")
            elif autonomy_level == 'direct':
                pass
            else:
                # Though frontend sends specific values, good to handle unexpected ones
                print(f"Warning: Unknown autonomy_level '{autonomy_level}'. Defaulting to direct prompt handling.")


            if output_type == 'image':
                image_response_data = generate_image_from_prompt(final_prompt)
                if 'error' in image_response_data: # Client returns dict with 'error' key
                    # Log the detailed error on the server
                    print(f"Error from image_client: {image_response_data['error']}")
                    # Provide a user-friendly error
                    user_error_message = image_response_data['error'] # Use client's error directly for now
                    if "quota" in user_error_message.lower():
                         user_error_message = "Image generation failed due to quota issues. Please try again later or check your account."
                    elif "rejected by the safety filters" in user_error_message.lower():
                         user_error_message = "Image generation failed: The prompt was rejected by safety filters."
                    elif "client not configured" in user_error_message.lower():
                         user_error_message = "Image generation service is not configured. Please contact support. (Check VERTEX_AI_PROJECT_ID/LOCATION)"

                    return jsonify({'error': user_error_message}), 500
                return jsonify(image_response_data)

            elif output_type == 'text':
                text_response = generate_text_from_prompt(final_prompt)
                if text_response and text_response.startswith("Error:"): # Client returns string starting with "Error:"
                     # Log the detailed error on the server
                    print(f"Error from gemini_client: {text_response}")
                    # Provide a user-friendly error
                    user_error_message = text_response
                    if "client not configured" in user_error_message.lower():
                         user_error_message = "Text generation service is not configured. Please contact support. (Check GEMINI_API_KEY)"
                    elif "prompt was blocked" in user_error_message.lower():
                         user_error_message = "Text generation failed: The prompt was blocked by safety filters."

                    return jsonify({'error': user_error_message}), 500
                return jsonify({'generated_text': text_response})

            else:
                return jsonify({'error': f'Invalid output_type specified: {output_type}. Must be "text" or "image".'}), 400

        except Exception as e:
            # Catch-all for any other unexpected errors during request processing
            print(f"Unexpected error in /generate endpoint: {e}")
            # Consider logging the full traceback here: import traceback; traceback.print_exc();
            return jsonify({'error': f'An unexpected server error occurred. Please try again later.'}), 500

    # If not POST, method not allowed
    return jsonify({'error': 'Method Not Allowed: Only POST requests are accepted for this endpoint.'}), 405

if __name__ == '__main__':
    app.run(debug=True, port=5000)
