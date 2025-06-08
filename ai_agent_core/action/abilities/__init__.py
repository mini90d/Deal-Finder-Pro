# This file marks the 'abilities' directory as a Python package.
# This package will contain various abilities that the agent can perform.
# Each ability can be a separate Python module or defined within this package.

# Example:
# from .basic_abilities import greet
# from .file_system_abilities import read_file, write_file

# A simple way to register abilities could be a dictionary
ABILITIES_REGISTRY = {}

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

pass
