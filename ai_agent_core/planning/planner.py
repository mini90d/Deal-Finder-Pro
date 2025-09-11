# This module is responsible for creating plans to achieve agent goals.
# It uses information from the understanding module (parser) and task decomposer (if applicable).
# A key capability of the Planner is to create "chained plans" where the output of one action
# can be dynamically used as an input to a subsequent action. This is facilitated by
# ABILITIES_METADATA which defines how abilities produce and consume data.

from ai_agent_core.action.abilities import ABILITIES_METADATA

class Planner:
    def __init__(self):
        # Initialize planner-specific settings or models
        pass

    def create_plan(self, structured_request, available_abilities=None, node_id_counter_start=0):
        """
        Creates a plan based on the structured request.
        For a 'hello_world' task in 'python', it plans code generation.
        Assigns node_ids to all actions.
        The `node_id_counter_start` parameter ensures unique node_ids across recursive calls,
        especially for chained actions where sub-plans are generated.
        """
        print(f"Creating plan for request: {structured_request}, starting node_id from {node_id_counter_start}")
        plan = []
        # current_node_id_offset is used by add_action_to_plan to create sequential node_ids
        # within the current planning context (e.g., for a single, non-chained request, or for one part of a chain).
        current_node_id_offset = 0

        intent = structured_request.get("intent")
        language = structured_request.get("language")
        task = structured_request.get("task")

        if intent == "chained_actions":
            final_plan = []
            sub_requests = structured_request.get("sub_requests", [])
            # For simplicity, as per requirements, focusing on a two-action chain first.
            # The logic will need to be generalized for longer chains.
            # Currently, this focuses on a two-step chain for simplicity.

            output_placeholder = None
            # current_chain_node_id_start tracks the starting node_id for the current sub-plan being processed.
            # It's initialized with node_id_counter_start passed to this create_plan call.
            current_chain_node_id_start = node_id_counter_start

            # Process the first sub-request in the chain
            if len(sub_requests) >= 1:
                # Recursively call create_plan for the first sub-request.
                # Pass current_chain_node_id_start to ensure its actions get unique, sequential node_ids.
                plan1_actions = self.create_plan(sub_requests[0], available_abilities, node_id_counter_start=current_chain_node_id_start)
                if plan1_actions:
                    # Assuming the sub-plan returns at least one action if successful.
                    first_action = plan1_actions[0]
                    # The node_id for first_action (e.g., "node_0") is assigned by the recursive create_plan call
                    # (specifically, by its 'add_action_to_plan' helper).

                    # Check if the first action produces any output that can be used by subsequent actions.
                    first_ability_name = first_action.get("ability_name")
                    first_ability_meta = ABILITIES_METADATA.get(first_ability_name)

                    if first_ability_meta and first_ability_meta.get("produces_outputs"):
                        # Get the name of the first output defined in its metadata (e.g., "generated_poem").
                        output_name = first_ability_meta["produces_outputs"][0]["name"]
                        # Create a placeholder string, e.g., "{{node_0.generated_poem}}".
                        # This placeholder will be used by the ActionExecutor to substitute the actual output
                        # of node_0 when executing the subsequent action that consumes this output.
                        output_placeholder = f"{{{{{first_action['node_id']}.{output_name}}}}}"
                        print(f"Action {first_action.get('action')} from {first_ability_name} produces output. Placeholder: {output_placeholder}")

                    final_plan.extend(plan1_actions)
                    # Update current_chain_node_id_start for the next sub-plan,
                    # ensuring its node_ids follow sequentially.
                    current_chain_node_id_start += len(plan1_actions)

            # Process the second sub-request in the chain
            if len(sub_requests) >= 2:
                # Only attempt to link if an output_placeholder was successfully generated from the first action.
                if output_placeholder:
                    # Recursively call create_plan for the second sub-request.
                    plan2_actions = self.create_plan(sub_requests[1], available_abilities, node_id_counter_start=current_chain_node_id_start)
                    if plan2_actions:
                        second_action = plan2_actions[0] # Assuming single action

                        # Check if the second action can accept the output from the first action.
                        second_ability_name = second_action.get("ability_name")
                        second_ability_meta = ABILITIES_METADATA.get(second_ability_name)

                        if second_ability_meta and second_ability_meta.get("can_accept_previous_output_for"):
                            # Iterate through parameters of the second action's ability.
                            for param_details in second_ability_meta.get("parameters", []):
                                # If a parameter is listed in "can_accept_previous_output_for",
                                # it means this parameter can be filled by the output_placeholder.
                                if param_details["name"] in second_ability_meta["can_accept_previous_output_for"]:
                                    print(f"Linking output to {second_action.get('action')}'s param: {param_details['name']}")
                                    # Set the parameter of the second action to the output_placeholder.
                                    # This overrides any value that might have been parsed from the user's request for this parameter.
                                    second_action[param_details["name"]] = output_placeholder
                                    break # Assuming one parameter accepts the chained output for now.

                        final_plan.extend(plan2_actions)
                        current_chain_node_id_start += len(plan2_actions)
                else: # Second request exists, but no output_placeholder to link (first action didn't produce usable output)
                    # Still need to plan the second sub-request and assign its node IDs correctly.
                    plan2_actions = self.create_plan(sub_requests[1], available_abilities, node_id_counter_start=current_chain_node_id_start)
                    if plan2_actions:
                        final_plan.extend(plan2_actions)
                        current_chain_node_id_start += len(plan2_actions) # Keep counter accurate

            print(f"Final plan for chained actions: {final_plan}")
            return final_plan

        # Assign node_id for non-chained actions
        # For non-chained actions, or for individual actions within a sub-plan of a chain.
        # This helper ensures each action gets a unique, sequential node_id.
        def add_action_to_plan(action_details):
            nonlocal current_node_id_offset # Modifies the offset within the current create_plan call.
            # Assigns node_id like "node_0", "node_1", etc., based on the node_id_counter_start
            # (which ensures uniqueness across different parts of a chain) and the current_node_id_offset
            # (which ensures uniqueness within this specific list of actions being planned).
            action_details['node_id'] = f"node_{node_id_counter_start + current_node_id_offset}"
            plan.append(action_details)
            current_node_id_offset += 1

        if intent == "unrecognized_request":
            # If the parser marked it as unrecognized, return an empty plan.
            # The agent's process_request will handle this based on parser output.
            print(f"Request intent is '{intent}', returning empty plan.")
            return plan

        if language == "python" and task == "hello_world":
            # Corrected: remove nested call
            add_action_to_plan({
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
            # Corrected: use add_action_to_plan
            add_action_to_plan({
                "action": "generate_code",
                "ability_name": "python_coding_ability.generate_code",
                "language": "python",
                "code_details": game_code
            })
        elif structured_request.get("intent") == "generate_html_page":
            details = structured_request.get("details", {})
            add_action_to_plan({
                "action": "generate_html", # Conceptual action name
                "ability_name": "html_generation_ability.generate_html",
                "title": details.get("title", "Default Title"),
                "heading_text": details.get("heading_text", "Default Heading"),
                "body_content": details.get("body_content", "Default body content.")
            })
        elif structured_request.get("intent") == "generate_melody":
            details = structured_request.get("details", {})
            add_action_to_plan({
                "action": "generate_melody", # Conceptual action name
                "ability_name": "music_generation_ability.generate_melody",
                "num_notes": details.get("num_notes", 8),
                "scale_name": details.get("scale", "C_major"),
                "base_octave": details.get("base_octave", 4)
            })
        elif structured_request.get("intent") == "generate_poem":
            details = structured_request.get("details", {})
            add_action_to_plan({
                "action": "generate_poem", # Conceptual action name
                "ability_name": "text_generation_ability.generate_poem",
                "topic": details.get("topic"),
                "num_lines": details.get("num_lines", 4)
            })
        elif structured_request.get("intent") == "greet":
            add_action_to_plan({
                "action": "execute_ability",
                "ability_name": "greet_user",
                "params": {"user_name": "User"}
            })
        else:
            # Default or fallback plan if no specific handler
            add_action_to_plan({
                "action": "execute_ability",
                "ability_name": "default_ability", # This ability might not exist, placeholder
                "params": {"request_details": structured_request}
            })

        # Ensure node_ids are assigned if plan was populated by non-chained action logic
        # The add_action_to_plan helper handles this.
        # If the plan somehow got actions without going through add_action_to_plan (e.g. future modification)
        # this loop would be a safeguard, but it's better to ensure node_id assignment at creation.
        # For now, add_action_to_plan covers all non-chained cases.

        print(f"Created plan: {plan}")
        return plan
