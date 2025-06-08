# This module is responsible for executing actions defined in a plan.
# It interacts with the agent's abilities to perform tasks.

class ActionExecutor:
    def __init__(self, abilities_registry):
        self.abilities_registry = abilities_registry
        pass

    def execute_action(self, action_step: dict, previous_successful_output: str = None):
        """
        Executes a single action step from a plan.
        The action_step dictionary contains details like 'ability_name' and other parameters.
        'previous_successful_output' can be used to inject output from a prior step.
        """
        ability_name = action_step.get("ability_name")

        print(f"Executing action step: Looking for ability '{ability_name}'")

        if ability_name not in self.abilities_registry:
            msg = f"Ability '{ability_name}' not found in registry."
            print(msg)
            return {"status": "error", "message": msg, "ability_name": ability_name}

        ability_method = self.abilities_registry[ability_name]

        try:
            params_for_ability = {}
            if "params" in action_step:
                params_for_ability.update(action_step["params"])

            known_action_keys = ["action", "ability_name", "params"]
            for key, value in action_step.items():
                if key not in known_action_keys and key not in params_for_ability:
                    params_for_ability[key] = value

            # Handle placeholder for previous output
            # Using list(params_for_ability.items()) to iterate over a copy as we might modify the dict
            for key, value in list(params_for_ability.items()):
                if isinstance(value, str) and value == "{{PREVIOUS_SUCCESSFUL_OUTPUT}}":
                    if previous_successful_output is not None:
                        print(f"Replacing placeholder for '{key}' with previous output.")
                        params_for_ability[key] = previous_successful_output
                    else:
                        print(f"Warning: Placeholder {{PREVIOUS_SUCCESSFUL_OUTPUT}} used for '{key}' in ability '{ability_name}' but no previous successful string output available.")
                        params_for_ability[key] = "" # Replace with empty string as a fallback

            print(f"Calling ability '{ability_name}' with params: {params_for_ability}")
            result_val = ability_method(**params_for_ability)
            print(f"Ability '{ability_name}' executed. Result type: {type(result_val)}")
            return {"status": "success", "result": result_val, "ability_name": ability_name}
        except Exception as e:
            error_msg = f"Error executing ability '{ability_name}': {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": error_msg, "ability_name": ability_name}

    def execute_plan(self, plan: list):
        """
        Executes a list of action steps (a plan).
        Passes successful string outputs from one step to the next if a placeholder is used.
        """
        print(f"Executing plan: {plan}")
        execution_results = []
        previous_successful_output: str = None # Initialize here

        for action_step in plan:
            result = self.execute_action(action_step, previous_successful_output)
            execution_results.append(result)

            if result.get("status") == "success":
                # Check if the result of the successful action is a string to pass forward
                if isinstance(result.get("result"), str):
                    previous_successful_output = result.get("result")
                    print(f"Captured string output from '{result.get('ability_name')}' for potential next step.")
                # else:
                    # If the result is not a string, subsequent steps expecting {{PREVIOUS_SUCCESSFUL_OUTPUT}}
                    # might not get what they expect.
                    # Clear previous_successful_output if current result is not a string,
                    # to prevent using an old string output for an unrelated later step.
                    # previous_successful_output = None
            elif result.get("status") == "error":
                print(f"Stopping plan execution due to error in step: {action_step.get('ability_name')}")
                break # Stop on first error

        return execution_results
