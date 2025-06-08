# This file marks the 'abilities' directory as a Python package.
# This package will contain various abilities that the agent can perform.
# Each ability can be a separate Python module or defined within this package.

# Example:
# from .basic_abilities import greet
# from .file_system_abilities import read_file, write_file

# A simple way to register abilities could be a dictionary
ABILITIES_REGISTRY = {}
ABILITIES_METADATA = {}

# Example of a simple ability directly in __init__ for demonstration
def default_ability(params=None):
    """A placeholder ability."""
    print(f"Default ability called with parameters: {params}")
    return "Default ability executed successfully."

def greet_user(user_name="User"):
    """Greets the user."""
    message = f"Hello, {user_name}! Welcome to the AI Agent."
    print(message)
    return message

ABILITIES_REGISTRY['default_ability'] = default_ability
ABILITIES_REGISTRY['greet_user'] = greet_user

# You might have a more sophisticated way to discover and register abilities
# from other files within this package.
# For example, iterating over modules in the package and looking for
# functions or classes decorated with an @ability decorator.

# Import and register PythonCodingAbility
try:
    from .python_coding_ability import PythonCodingAbility
    # We can register the instance or specific methods.
    # If we register methods, ActionExecutor needs to handle that.
    # For now, let's assume ActionExecutor can get the method from the class instance.
    # Or, more simply, register specific callable methods directly if that's the pattern.

    # Let's register the method directly for simplicity with the new planner.
    # The planner now specifies 'python_coding_ability.generate_code'
    # So, the key in ABILITIES_REGISTRY should match this.

    # To make this work, we need an instance of the class or make methods static/module-level.
    # Let's instantiate for now. A shared instance could also be used.
    _python_coder = PythonCodingAbility()
    ABILITIES_REGISTRY['python_coding_ability.generate_code'] = _python_coder.generate_code
    # If we wanted to register the whole class:
    # ABILITIES_REGISTRY['PythonCodingAbility'] = PythonCodingAbility()

except ImportError as e:
    print(f"Error importing python_coding_ability: {e}. This might be okay if the ability is optional.")


# Import and register HtmlGenerationAbility
try:
    from .html_generation_ability import HtmlGenerationAbility
    _html_generator = HtmlGenerationAbility()
    ABILITIES_REGISTRY['html_generation_ability.generate_html'] = _html_generator.generate_html

except ImportError as e:
    print(f"Error importing html_generation_ability: {e}. This might be okay if the ability is optional.")

# Import and register MusicGenerationAbility
try:
    from .music_generation_ability import MusicGenerationAbility
    _music_generator = MusicGenerationAbility()
    ABILITIES_REGISTRY['music_generation_ability.generate_melody'] = _music_generator.generate_melody

except ImportError as e:
    print(f"Error importing music_generation_ability: {e}. This might be okay if the ability is optional.")

# Import and register TextGenerationAbility
try:
    from .text_generation_ability import TextGenerationAbility
    _text_generator = TextGenerationAbility()
    ABILITIES_REGISTRY['text_generation_ability.generate_poem'] = _text_generator.generate_poem

except ImportError as e:
    print(f"Error importing text_generation_ability: {e}. This might be okay if the ability is optional.")

# Populate ABILITIES_METADATA (example for poem and html)

# For text_generation_ability.generate_poem
if 'text_generation_ability.generate_poem' in ABILITIES_REGISTRY:
    ABILITIES_METADATA['text_generation_ability.generate_poem'] = {
        "key": "text_generation_ability.generate_poem",
        "display_name": "Generate Poem",
        "description": "Generates a short poem based on a topic and number of lines.",
        "parameters": [
            {"name": "topic", "type": "str", "prompt": "Enter the topic for the poem (e.g., nature, stars):", "default": None},
            {"name": "num_lines", "type": "int", "prompt": "Enter the number of lines for the poem:", "default": 4}
        ],
        "can_accept_previous_output_for": [],
        "produces_output_type": "str",
        "produces_outputs": [{"name": "generated_poem", "type": "str", "description": "The full text of the generated poem."}]
    }

# For html_generation_ability.generate_html
if 'html_generation_ability.generate_html' in ABILITIES_REGISTRY:
    ABILITIES_METADATA['html_generation_ability.generate_html'] = {
        "key": "html_generation_ability.generate_html",
        "display_name": "Create HTML Page",
        "description": "Generates an HTML page with a title, heading, and body content.",
        "parameters": [
            {"name": "title", "type": "str", "prompt": "Enter the title for the HTML page:", "default": "My Page"},
            {"name": "heading_text", "type": "str", "prompt": "Enter the main heading for the page:", "default": "Welcome"},
            {"name": "body_content", "type": "str", "prompt": "Enter the body content for the page:", "default": "Hello, world!"}
        ],
        "can_accept_previous_output_for": ["body_content", "title", "heading_text"],
        "produces_output_type": "html_str",
        "produces_outputs": [{"name": "html_document", "type": "html_str", "description": "The complete HTML document."}]
    }

# For python_coding_ability.generate_code (Hello World example)
# This metadata is for the UI Builder when "Generate Python Script" is chosen.
# The actual ability method `python_coding_ability.generate_code` is simpler.
if 'python_coding_ability.generate_code' in ABILITIES_METADATA: # Check if already exists from previous step
    # Update existing entry for python_coding_ability.generate_code
    ABILITIES_METADATA['python_coding_ability.generate_code'].update({
        "produces_output_type": "python_code_str", # Keep this
        "produces_outputs": [{"name": "generated_code", "type": "python_code_str", "description": "The generated Python code."}]
        # The 'parameters' list with 'script_choice' is already defined from previous step and should be preserved.
    })
else: # Fallback if it wasn't defined (should not happen if previous step ran)
    ABILITIES_METADATA['python_coding_ability.generate_code'] = {
        "key": "python_coding_ability.generate_code",
        "display_name": "Generate Python Script", # Default if not set by choice logic
        "description": "Generates Python code.",
        "parameters": [ # Default parameters if not using choice-based schema
            {"name": "code_details", "type": "str", "prompt": "Enter Python code details:", "default": "print(\"Hello!\")"},
            {"name": "language", "type": "str", "prompt": "Language:", "default": "python"}
        ],
        "can_accept_previous_output_for": ["code_details"],
        "produces_output_type": "python_code_str",
        "produces_outputs": [{"name": "generated_code", "type": "python_code_str", "description": "The generated Python code."}]
    }
    # Note: Number Guessing game used to use this key directly with pre-defined code_details.
    # It will now be a 'choice' within this ability's schema in the UI builder.
    # The actual python_coding_ability.generate_code method still expects 'language' and 'code_details'.
    # The UI builder will resolve the 'choice' to these parameters.
    # For direct calls to agent.process_request (like from old CLI), the old specific intents
    # (e.g., hello_world_python, generate_number_guessing_game_python) in the parser/planner
    # will still work by setting 'code_details' directly.

# For music_generation_ability.generate_melody
if 'music_generation_ability.generate_melody' in ABILITIES_REGISTRY:
    ABILITIES_METADATA['music_generation_ability.generate_melody'] = {
        "key": "music_generation_ability.generate_melody",
        "display_name": "Compose Melody",
        "description": "Generates a simple musical melody.",
        "parameters": [
            {"name": "num_notes", "type": "int", "prompt": "Number of notes (e.g., 8)", "default": 8},
            {"name": "scale_name", "type": "str", "prompt": "Musical scale (e.g., C_major)", "default": "C_major"},
            {"name": "base_octave", "type": "int", "prompt": "Base octave (e.g., 4)", "default": 4}
        ],
        "can_accept_previous_output_for": [],
        "produces_output_type": "str",
        "produces_outputs": [{"name": "melody_string", "type": "str", "description": "The generated melody as a string."}]
    }

# Update for python_coding_ability.generate_code to support choices for UI builder
# The actual ability method `python_coding_ability.generate_code` still takes `language` and `code_details`.
# The `script_choice` parameter is a UI builder concept that resolves to these.
if 'python_coding_ability.generate_code' in ABILITIES_METADATA: # Modify existing entry
    ABILITIES_METADATA['python_coding_ability.generate_code']['display_name'] = "Generate Python Script" # Update display name
    ABILITIES_METADATA['python_coding_ability.generate_code']['description'] = "Generates predefined Python scripts via a choice."
    # Parameters for the UI Builder to present as a choice
    # The core ability still expects 'language' and 'code_details'.
    # The UI Builder will use the 'value_for_node_parameters' from the chosen option
    # to populate the node's 'parameters' field.
    ABILITIES_METADATA['python_coding_ability.generate_code']['parameters'] = [
        {
            "name": "script_choice",
            "type": "choice",
            "prompt": "Choose a Python script to generate:",
            "choices": [
                {
                    "display_name": "Hello, World!",
                    "value_for_node_parameters": { # This dict will become the node's 'parameters'
                        "language": "python",
                        "code_details": "print(\"Hello, World!\")"
                    }
                },
                {
                    "display_name": "Number Guessing Game",
                    "value_for_node_parameters": {
                        "language": "python",
                        "code_details": "import random\n\ndef number_guessing_game():\n    number_to_guess = random.randint(1, 100)\n    guess = None\n    print(\"I've picked a number between 1 and 100. Try to guess it!\")\n    while guess != number_to_guess:\n        try:\n            guess_str = input(\"Enter your guess (1-100): \")\n            guess = int(guess_str)\n            if guess < number_to_guess:\n                print(\"Too low!\")\n            elif guess > number_to_guess:\n                print(\"Too high!\")\n            else:\n                print(f\"Congratulations! You guessed the number {number_to_guess}.\")\n        except ValueError:\n            print(\"Invalid input. Please enter a number.\")\n\nif __name__ == '__main__':\n    number_guessing_game()"
                    }
                }
                # Future script choices can be added here
            ],
            "default_choice_index": 0
        }
        # Note: "can_accept_previous_output_for" remains as defined before, typically for 'code_details'.
        # The 'script_choice' itself doesn't accept previous output.
    ]


# Ensure all registered abilities have at least a basic metadata entry if not detailed
for key in ABILITIES_REGISTRY:
    if key not in ABILITIES_METADATA:
        # For abilities like default_ability, greet_user, etc.
        # Parameters would need to be manually introspected or defined if they were to be configurable.
        # For now, assume they take simple or no params if not explicitly defined above.
        param_list = []
        if key == "default_ability": # Example if we knew its params
             param_list = [{"name": "params", "type": "str", "prompt": "Enter params for default ability:", "default": None}]
        elif key == "greet_user":
             param_list = [{"name": "user_name", "type": "str", "prompt": "Enter user name to greet:", "default": "User"}]

        ABILITIES_METADATA[key] = {
            "key": key,
            "display_name": key.replace("_", " ").replace(".", " ").title(), # Generic display name
            "description": f"Executes the {key} ability.",
            "parameters": param_list,
            "can_accept_previous_output_for": [],
            "produces_output_type": "unknown",
            "produces_outputs": [{"name": "default_output", "type": "unknown", "description": "The direct output of the ability."}]
        }

pass
