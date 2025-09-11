# This module is responsible for executing actions defined in a plan.
# It interacts with the agent's abilities to perform tasks.
import re
from .abilities import ABILITIES_METADATA # Import for schema access

class ActionExecutor:
    def __init__(self, abilities_registry):
        self.abilities_registry = abilities_registry
        pass

    def execute_action(self, action_step: dict, executed_steps_outputs: dict = None):
        """
        Executes a single action step from a plan.
        'executed_steps_outputs' contains outputs from prior steps, keyed by node_id.
        Example: executed_steps_outputs = {"node_0": {"generated_poem": "poem text..."}}
        The action_step dictionary itself should contain 'ability_name' and parameters for the ability.
        """
        ability_name = action_step.get("ability_name")
        node_id = action_step.pop("node_id", "unknown_node")

        print(f"Executing action step (Node ID: {node_id}): Looking for ability '{ability_name}'")

        if ability_name not in self.abilities_registry:
            msg = f"Ability '{ability_name}' not found in registry."
            print(msg)
            return {"status": "error", "message": msg, "ability_name": ability_name, "node_id": node_id}

        ability_method = self.abilities_registry[ability_name]

        if executed_steps_outputs is None: # Ensure it's a dict for placeholder logic
            executed_steps_outputs = {}

        try:
            # Consolidate parameters for the ability.
            # Parameters can be directly under action_step or within a 'params' sub-dictionary.
            params_for_ability = {}
            if "params" in action_step: # Older structure might have a 'params' key
                params_for_ability.update(action_step["params"])

            # Merge other keys from action_step as parameters, excluding known control keys.
            known_action_keys = ["action", "ability_name", "params"] # 'node_id' was already popped
            for key, value in action_step.items():
                if key not in known_action_keys and key not in params_for_ability:
                    params_for_ability[key] = value

            # Resolve placeholders in parameter values.
            # Placeholders like {{node_id.output_name}} allow dynamic data flow between actions.
            for param_key, param_value in list(params_for_ability.items()):
                if isinstance(param_value, str):
                    new_param_value = param_value # Start with the original value
                    # Find all occurrences of {{placeholder_content}}
                    placeholders = re.findall(r"\{\{([^}]+)\}\}", param_value)

                    for placeholder_key_content in placeholders:
                        # Check for the old "PREVIOUS_SUCCESSFUL_OUTPUT" placeholder for basic chaining.
                        # This is a simpler form and relies on the immediately preceding step's output.
                        if placeholder_key_content == "PREVIOUS_SUCCESSFUL_OUTPUT":
                            last_node_output_value = None
                            if executed_steps_outputs:
                                # Attempt to get the output of the numerically last executed node.
                                # This is a heuristic for simple sequential plans.
                                last_executed_node_id = sorted(executed_steps_outputs.keys())[-1] if executed_steps_outputs else None
                                if last_executed_node_id:
                                    outputs_of_last_node = executed_steps_outputs.get(last_executed_node_id, {})
                                    # Prefer "default_output" if available, otherwise take the first output found.
                                    if "default_output" in outputs_of_last_node:
                                        last_node_output_value = outputs_of_last_node["default_output"]
                                    elif outputs_of_last_node:
                                        last_node_output_value = next(iter(outputs_of_last_node.values()))

                            if last_node_output_value is not None:
                                print(f"Node {node_id}: Replacing legacy placeholder '{{{{PREVIOUS_SUCCESSFUL_OUTPUT}}}}' for '{param_key}'.")
                                # If the placeholder is the entire string, replace it directly.
                                if param_value == "{{PREVIOUS_SUCCESSFUL_OUTPUT}}":
                                    new_param_value = last_node_output_value
                                else: # If part of a larger string, perform string replacement.
                                    new_param_value = new_param_value.replace("{{PREVIOUS_SUCCESSFUL_OUTPUT}}", str(last_node_output_value))
                            else:
                                print(f"Node {node_id}: Warning: Legacy placeholder {{PREVIOUS_SUCCESSFUL_OUTPUT}} for '{param_key}' but no previous output found. Replacing with empty string.")
                                if param_value == "{{PREVIOUS_SUCCESSFUL_OUTPUT}}": new_param_value = ""
                                else: new_param_value = new_param_value.replace("{{PREVIOUS_SUCCESSFUL_OUTPUT}}", "")

                        else:
                            # Handle new, more specific placeholder format: {{node_id.output_name}}
                            # This format allows referencing a specific output from a specific prior step (node).
                            parts = placeholder_key_content.split('.', 1)
                            if len(parts) == 2:
                                source_node_id, output_key_name = parts
                                # Look up the source_node_id in the dictionary of outputs from already executed steps.
                                source_node_outputs = executed_steps_outputs.get(source_node_id)

                                if source_node_outputs and output_key_name in source_node_outputs:
                                    replacement_value = source_node_outputs[output_key_name]
                                    print(f"Node {node_id}: Replacing placeholder '{{{{{placeholder_key_content}}}}}' for '{param_key}' with value from {source_node_id}.{output_key_name}.")
                                    # Perform replacement, similar to the legacy placeholder.
                                    if param_value == f"{{{{{placeholder_key_content}}}}}":
                                        new_param_value = replacement_value
                                    else:
                                        new_param_value = new_param_value.replace(f"{{{{{placeholder_key_content}}}}}", str(replacement_value))
                                else:
                                    print(f"Node {node_id}: Warning: Output '{placeholder_key_content}' not found in executed steps for '{param_key}'. Replacing with empty string.")
                                    if param_value == f"{{{{{placeholder_key_content}}}}}": new_param_value = ""
                                    else: new_param_value = new_param_value.replace(f"{{{{{placeholder_key_content}}}}}", "")
                            else:
                                print(f"Node {node_id}: Warning: Invalid placeholder format '{{{{{placeholder_key_content}}}}}' for '{param_key}'. Expected 'node_id.output_name'.")

                    # Update the parameter with the (potentially) modified value.
                    params_for_ability[param_key] = new_param_value


            print(f"Node {node_id}: Calling ability '{ability_name}' with params: {params_for_ability}")
            result_val = ability_method(**params_for_ability)
            print(f"Node {node_id}: Ability '{ability_name}' executed. Result type: {type(result_val)}")
            return {"status": "success", "result": result_val, "ability_name": ability_name, "node_id": node_id}
        except Exception as e:
            error_msg = f"Error executing ability '{ability_name}' for Node {node_id}: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": error_msg, "ability_name": ability_name, "node_id": node_id}

    def execute_plan(self, plan: list):
        """
        Executes a list of action steps (a plan).
        Passes successful outputs from one step to the next if a placeholder is used.
        Outputs are stored in `executed_steps_outputs` where the key is the `node_id` of the step
        that produced the output, and the value is a dictionary of its outputs
        (e.g., `executed_steps_outputs["node_0"] = {"generated_poem": "poem text..."}`).
        """
        print(f"Executing plan: {plan}")
        execution_results = []
        # executed_steps_outputs accumulates outputs from all successfully executed steps in the current plan.
        # This dictionary is passed to each `execute_action` call to enable placeholder resolution.
        executed_steps_outputs = {}

        for action_step in plan:
            # Execute the current action_step, providing outputs from all *previously* executed steps.
            result = self.execute_action(action_step.copy(), executed_steps_outputs)
            execution_results.append(result)

            if result.get("status") == "success":
                node_id = result.get("node_id", "unknown_node") # Node ID of the step just executed.
                ability_key = result.get("ability_name")
                actual_output_value = result.get("result") # The direct return value of the ability.

                # Use ABILITIES_METADATA to determine how to store the output.
                # The metadata's "produces_outputs" field (a list of output objects, each with a "name")
                # defines the key under which the output should be stored.
                ability_schema = ABILITIES_METADATA.get(ability_key)
                if ability_schema and ability_schema.get("produces_outputs"):
                    # Assuming the first output defined in "produces_outputs" is the primary one.
                    # For abilities producing multiple named outputs, this logic might need extension,
                    # or the ability itself should return a dictionary of its outputs.
                    output_def_name = ability_schema["produces_outputs"][0]["name"]
                    # Store the output: executed_steps_outputs["node_X"]["output_name"] = value
                    executed_steps_outputs[node_id] = {output_def_name: actual_output_value}
                else:
                    # Fallback if no explicit output definition in schema: store under a "default_output" key.
                    executed_steps_outputs[node_id] = {"default_output": actual_output_value}

                print(f"Captured output for Node {node_id}: {executed_steps_outputs[node_id]}")

            elif result.get("status") == "error":
                # If any step in the plan fails, stop further execution of the plan.
                print(f"Stopping plan execution due to error in step: {action_step.get('ability_name')} (Node ID: {result.get('node_id')})")
                break

        return execution_results
