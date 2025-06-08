# This module is responsible for creating plans to achieve agent goals.
# It will use information from the understanding module and task decomposer.

class Planner:
    def __init__(self):
        # Initialize planner-specific settings or models
        pass

    def create_plan(self, structured_request, available_abilities=None):
        """
        Creates a plan based on the structured request.
        For a 'hello_world' task in 'python', it plans code generation.
        """
        print(f"Creating plan for request: {structured_request}")
        plan = []

        intent = structured_request.get("intent")
        language = structured_request.get("language")
        task = structured_request.get("task")

        if intent == "chained_actions":
            final_plan = []
            sub_requests = structured_request.get("sub_requests", [])
            print(f"Planning for chained actions. Number of sub-requests: {len(sub_requests)}")
            for i, sub_request in enumerate(sub_requests):
                print(f"Planning for sub-request {i+1}: {sub_request.get('raw', 'N/A')}")
                # Pass available_abilities, though it's not strictly used by all planning branches yet
                sub_plan = self.create_plan(sub_request, available_abilities)
                if sub_plan:
                    final_plan.extend(sub_plan)
                else:
                    # Handle case where a sub-plan might be empty (e.g., if a sub-request is unrecognized)
                    # This could mean stopping the whole chain or trying to continue.
                    # For now, we'll just extend, an empty sub_plan won't add actions.
                    # If a sub-request was unrecognized, its 'error' field should propagate.
                    print(f"Warning: Sub-plan for sub-request {i+1} was empty or None.")
            print(f"Final plan for chained actions: {final_plan}")
            return final_plan

        if intent == "unrecognized_request":
            # If the parser marked it as unrecognized, return an empty plan.
            # The agent's process_request will handle this based on parser output.
            print(f"Request intent is '{intent}', returning empty plan.")
            return plan

        if language == "python" and task == "hello_world":
            plan.append({
                "action": "generate_code",
                "ability_name": "python_coding_ability.generate_code",
                "language": "python",
                "code_details": "print(\"Hello, World!\")"
            })
        elif structured_request.get("intent") == "generate_number_guessing_game_python":
            game_code = """import random

def number_guessing_game():
    number_to_guess = random.randint(1, 100)
    guess = None
    print("I've picked a number between 1 and 100. Try to guess it!")
    while guess != number_to_guess:
        try:
            guess_str = input("Enter your guess: ")
            guess = int(guess_str)
            if guess < number_to_guess:
                print("Too low!")
            elif guess > number_to_guess:
                print("Too high!")
            else:
                print(f"Congratulations! You guessed the number {number_to_guess}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == '__main__':
    number_guessing_game()"""
            plan.append({
                "action": "generate_code",
                "ability_name": "python_coding_ability.generate_code",
                "language": "python",
                "code_details": game_code
            })
        elif structured_request.get("intent") == "generate_html_page":
            details = structured_request.get("details", {})
            plan.append({
                "action": "generate_html", # Conceptual action name
                "ability_name": "html_generation_ability.generate_html",
                # Parameters for the ability are taken from the 'details' field
                "title": details.get("title", "Default Title"),
                "heading_text": details.get("heading_text", "Default Heading"),
                "body_content": details.get("body_content", "Default body content.")
            })
        elif structured_request.get("intent") == "generate_melody":
            details = structured_request.get("details", {})
            plan.append({
                "action": "generate_melody", # Conceptual action name
                "ability_name": "music_generation_ability.generate_melody",
                "num_notes": details.get("num_notes", 8), # Default if not provided
                "scale_name": details.get("scale", "C_major"), # Default scale, corrected param name
                "base_octave": details.get("base_octave", 4) # Default octave
            })
        elif structured_request.get("intent") == "generate_poem":
            details = structured_request.get("details", {})
            plan.append({
                "action": "generate_poem", # Conceptual action name
                "ability_name": "text_generation_ability.generate_poem",
                "topic": details.get("topic"), # Will be None if not found, ability handles None
                "num_lines": details.get("num_lines", 4)
            })
        elif structured_request.get("intent") == "greet": # Keep existing greet functionality
            plan.append({
                "action": "execute_ability",
                "ability_name": "greet_user",
                "params": {"user_name": "User"}
            })
        else:
            # Default or fallback plan if no specific handler
            plan.append({
                "action": "execute_ability",
                "ability_name": "default_ability",
                "params": {"request_details": structured_request}
            })

        print(f"Created plan: {plan}")
        return plan
