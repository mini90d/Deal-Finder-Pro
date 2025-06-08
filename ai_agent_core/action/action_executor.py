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
            params_for_ability = {}
            if "params" in action_step:
                params_for_ability.update(action_step["params"])

            known_action_keys = ["action", "ability_name", "params"]
            for key, value in action_step.items():
                if key not in known_action_keys and key not in params_for_ability:
                    params_for_ability[key] = value

            # Handle new placeholder format: {{node_id.output_name}}
            for param_key, param_value in list(params_for_ability.items()):
                if isinstance(param_value, str):
                    new_param_value = param_value
                    placeholders = re.findall(r"\{\{([^}]+)\}\}", param_value) # Find all {{...}}

                    for placeholder_key in placeholders:
                        # Check for old placeholder format first for backward compatibility / simple chaining
                        if placeholder_key == "PREVIOUS_SUCCESSFUL_OUTPUT":
                            # This assumes 'previous_successful_output' is implicitly the 'default_output' of the immediately preceding node.
                            # This part of the logic might need to be more robust or rely on explicit node_id.output_name.
                            # For now, let's try to find the last executed node's default output.
                            # This is a simplification; a more robust system would need to track execution order.
                            last_node_output = None
                            if executed_steps_outputs: # If there are any outputs
                                # Get the output of the numerically last node (assuming sequential node_ids like node_0, node_1)
                                # This is a heuristic and might not be robust for all scenarios (e.g. parallel execution)
                                last_executed_node_id = sorted(executed_steps_outputs.keys())[-1] if executed_steps_outputs else None
                                if last_executed_node_id:
                                    outputs_of_last_node = executed_steps_outputs.get(last_executed_node_id, {})
                                    if "default_output" in outputs_of_last_node: # Check for fallback name
                                        last_node_output = outputs_of_last_node["default_output"]
                                    elif outputs_of_last_node: # Take the first available output if no "default_output"
                                        last_node_output = next(iter(outputs_of_last_node.values()))

                            if last_node_output is not None:
                                print(f"Node {node_id}: Replacing legacy placeholder '{{{{PREVIOUS_SUCCESSFUL_OUTPUT}}}}' for '{param_key}' with output from last step.")
                                if param_value == "{{PREVIOUS_SUCCESSFUL_OUTPUT}}": # Placeholder is the entire value
                                    new_param_value = last_node_output
                                else: # Placeholder is part of a larger string
                                    new_param_value = new_param_value.replace("{{PREVIOUS_SUCCESSFUL_OUTPUT}}", str(last_node_output))
                            else:
                                print(f"Node {node_id}: Warning: Legacy placeholder {{PREVIOUS_SUCCESSFUL_OUTPUT}} used for '{param_key}' but no suitable previous output found.")
                                if param_value == "{{PREVIOUS_SUCCESSFUL_OUTPUT}}": new_param_value = ""
                                else: new_param_value = new_param_value.replace("{{PREVIOUS_SUCCESSFUL_OUTPUT}}", "")

                        else: # New placeholder format: {{node_id.output_name}}
                            parts = placeholder_key.split('.', 1)
                            if len(parts) == 2:
                                source_node_id, output_key_name = parts
                                source_node_outputs = executed_steps_outputs.get(source_node_id)
                                if source_node_outputs and output_key_name in source_node_outputs:
                                    replacement_value = source_node_outputs[output_key_name]
                                    print(f"Node {node_id}: Replacing placeholder '{{{{{placeholder_key}}}}}' for '{param_key}' with value from {source_node_id}.{output_key_name}.")
                                    if param_value == f"{{{{{placeholder_key}}}}}": # Placeholder is the entire value
                                        new_param_value = replacement_value
                                    else: # Placeholder is part of a larger string
                                        new_param_value = new_param_value.replace(f"{{{{{placeholder_key}}}}}", str(replacement_value))
                                else:
                                    print(f"Node {node_id}: Warning: Output '{placeholder_key}' not found in executed steps. Replacing with empty string.")
                                    if param_value == f"{{{{{placeholder_key}}}}}": new_param_value = ""
                                    else: new_param_value = new_param_value.replace(f"{{{{{placeholder_key}}}}}", "")
                            else:
                                print(f"Node {node_id}: Warning: Invalid placeholder format '{{{{{placeholder_key}}}}}'. Expected 'node_id.output_name'.")

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
        Outputs are stored in a structured way: executed_steps_outputs[node_id] = {output_name: value}.
        """
        print(f"Executing plan: {plan}")
        execution_results = []
        executed_steps_outputs = {} # Stores outputs of all executed steps

        for action_step in plan:
            # Pass the *cumulative* outputs of all previously executed steps
            result = self.execute_action(action_step.copy(), executed_steps_outputs) # Pass a copy of action_step
            execution_results.append(result)

            if result.get("status") == "success":
                node_id = result.get("node_id", "unknown_node")
                ability_key = result.get("ability_name")
                actual_output_value = result.get("result")

                ability_schema = ABILITIES_METADATA.get(ability_key)
                if ability_schema and ability_schema.get("produces_outputs"):
                    # Assuming single output for now as per current schema design
                    output_def_name = ability_schema["produces_outputs"][0]["name"]
                    executed_steps_outputs[node_id] = {output_def_name: actual_output_value}
                else:
                    # Fallback if no explicit output definition in schema
                    executed_steps_outputs[node_id] = {"default_output": actual_output_value}

                print(f"Captured output for Node {node_id}: {executed_steps_outputs[node_id]}")

            elif result.get("status") == "error":
                print(f"Stopping plan execution due to error in step: {action_step.get('ability_name')} (Node ID: {result.get('node_id')})")
                break

        return execution_results
