import json
import sys
import os

# Adjust Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from ai_agent_core.agent import Agent
except ImportError as e:
    print(f"Error: Could not import Agent: {e}")
    print("Ensure ai_agent_core is in PYTHONPATH or accessible.")
    sys.exit(1)


def get_user_input(prompt_message, param_type, default_value=None):
    while True:
        try:
            prompt_suffix = f" (default: {default_value})" if default_value is not None else ""
            user_val = input(f"{prompt_message}{prompt_suffix}: ").strip()

            if not user_val and default_value is not None:
                return default_value # Return default if user just hits Enter

            if param_type == "int":
                return int(user_val)
            elif param_type == "bool": # Example for boolean
                return user_val.lower() in ['true', 'y', 'yes', '1']
            return user_val # String by default
        except ValueError:
            print(f"Invalid input. Expected a(n) {param_type}. Please try again.")
        except EOFError:
            print("\nInput cancelled.")
            return None


def print_execution_results(results):
    print("\n--- Agent Execution Results ---")
    if not results or not results.get("execution_results"):
        print("No execution results returned or results format is unexpected.")
        print(json.dumps(results, indent=2)) # Print the whole thing for debugging
        return

    for result_item in results["execution_results"]:
        print(f"  Node ID: {result_item.get('node_id', 'N/A')}")
        print(f"  Ability: {result_item.get('ability_name', 'N/A')}")
        print(f"  Status:  {result_item.get('status', 'N/A')}")
        if result_item.get("status") == "success":
            output = result_item.get("result")
            # Truncate long outputs for display
            if isinstance(output, str) and len(output) > 200:
                output = output[:200] + "..."
            print(f"  Result:  {output}")
        else:
            print(f"  Error:   {result_item.get('message', 'N/A')}")
        print("-" * 20)
    print(f"Overall Plan Status: {results.get('status', 'N/A')}")
    print("-----------------------------")


def main():
    print("Initializing Agent to fetch abilities schema...")
    try:
        agent = Agent(agent_id="ui_builder_agent")
        abilities_schema_dict = agent.get_abilities_schema()
        # Convert dict to list for indexed selection, and filter out any without display_name
        available_abilities_list = [
            v for k, v in abilities_schema_dict.items()
            if v.get("display_name") and v.get("key") and isinstance(v.get("parameters"), list)
        ]
        if not available_abilities_list:
            print("Error: No abilities found or schema is not in expected list format from agent.")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to initialize agent or get abilities schema: {e}")
        sys.exit(1)

    nodes = []
    edges = []
    node_counter = 0

    print("\n--- Visual Plan Builder (Text Simulation) ---")

    while True:
        print("\n--- Current Plan ---")
        if not nodes:
            print("No nodes yet.")
        else:
            print("Nodes:", [node['id'] for node in nodes])
            # print("Edges:", edges) # Edges can be verbose for this view

        print("\n--- Available Abilities ---")
        for i, ability_schema in enumerate(available_abilities_list):
            print(f"{i+1}: {ability_schema['display_name']}")
        print("0: Finish and Execute Plan")

        try:
            choice_str = input("Select an ability to add, or 0 to finish: ").strip()
            if not choice_str: continue
            choice = int(choice_str)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        except EOFError:
            print("\nExiting builder.")
            break

        if choice == 0:
            if not nodes:
                print("No plan to execute. Exiting.")
            else:
                print("Finishing plan and preparing for execution.")
            break

        if not 0 < choice <= len(available_abilities_list):
            print("Invalid choice. Please select a valid number from the list.")
            continue

        selected_ability_schema = available_abilities_list[choice - 1]
        current_node_id = f"node_{node_counter}"
        print(f"\nConfiguring: {selected_ability_schema['display_name']} (Node ID: {current_node_id})")

        parameters = {}

        for param_schema in selected_ability_schema["parameters"]:
            param_name = param_schema["name"]
            param_type = param_schema["type"]
            param_prompt = param_schema["prompt"]
            param_default = param_schema.get("default")

            if param_type == "choice":
                print(f"  {param_prompt}")
                choices = param_schema.get("choices", [])
                default_choice_idx = param_schema.get("default_choice_index", 0)

                for i, choice_option in enumerate(choices):
                    print(f"    {i+1}: {choice_option['display_name']}")

                user_choice_idx_str = input(f"    Enter your choice (1-{len(choices)}, default {default_choice_idx + 1}): ").strip()

                resolved_params_for_node = {}
                try:
                    if not user_choice_idx_str: # User pressed Enter for default
                        user_choice_idx = default_choice_idx
                    else:
                        user_choice_idx = int(user_choice_idx_str) - 1 # Adjust to 0-indexed

                    if 0 <= user_choice_idx < len(choices):
                        selected_choice_value = choices[user_choice_idx].get("value_for_node_parameters")
                        if isinstance(selected_choice_value, dict):
                            parameters.update(selected_choice_value) # Merge these into the node's main parameters
                            print(f"    Selected '{choices[user_choice_idx]['display_name']}'. Node parameters updated: {selected_choice_value}")
                        else: # Should be a dict, but handle if not
                            print(f"    Warning: Choice '{choices[user_choice_idx]['display_name']}' does not have valid 'value_for_node_parameters' dict.")
                    else:
                        print(f"    Invalid choice number. Using default choice ({default_choice_idx + 1}).")
                        selected_choice_value = choices[default_choice_idx].get("value_for_node_parameters")
                        if isinstance(selected_choice_value, dict):
                             parameters.update(selected_choice_value)
                        else: # Should be a dict
                            print(f"    Warning: Default choice '{choices[default_choice_idx]['display_name']}' does not have valid 'value_for_node_parameters' dict.")
                except ValueError:
                    print(f"    Invalid input. Using default choice ({default_choice_idx + 1}).")
                    selected_choice_value = choices[default_choice_idx].get("value_for_node_parameters")
                    if isinstance(selected_choice_value, dict):
                        parameters.update(selected_choice_value)
                    else: # Should be a dict
                        print(f"    Warning: Default choice (on error) '{choices[default_choice_idx]['display_name']}' does not have valid 'value_for_node_parameters' dict.")
                # This 'choice' pseudo-parameter itself is not added to 'parameters'.
                # Its selection *determines* other parameters. So, we 'continue' the loop
                # to not process this param_schema as a regular input field.
                continue

            # --- Logic for "str", "int", etc. types (non-choice) ---
            use_specific_output = False
            if nodes and param_name in selected_ability_schema.get("can_accept_previous_output_for", []):
                try:
                    link_choice = input(f"  Link '{param_name}' to output of a previous step? (y/n, default n): ").strip().lower()
                    if link_choice == 'y':
                        print("    Available previous nodes:")
                        for idx, prev_node in enumerate(nodes):
                            print(f"      {idx+1}: {prev_node['id']} ({prev_node['label']})")

                        source_node_idx_str = input(f"    Select source node number (1-{len(nodes)}): ").strip()
                        source_node_idx = int(source_node_idx_str) - 1

                        if 0 <= source_node_idx < len(nodes):
                            selected_source_node = nodes[source_node_idx]
                            source_ability_key = selected_source_node["ability_key"]
                            source_ability_meta = abilities_schema_dict.get(source_ability_key)

                            if source_ability_meta and source_ability_meta.get("produces_outputs"):
                                available_outputs = source_ability_meta["produces_outputs"]
                                if len(available_outputs) == 1: # Auto-select if only one output
                                    selected_output_name = available_outputs[0]["name"]
                                    print(f"    Auto-selected output '{selected_output_name}' from {selected_source_node['id']}.")
                                else: # Prompt if multiple outputs
                                    print(f"    Available outputs from {selected_source_node['id']} ({selected_source_node['label']}):")
                                    for jdx, out_def in enumerate(available_outputs):
                                        print(f"      {jdx+1}: {out_def['name']} ({out_def.get('description', 'N/A')})")
                                    output_idx_str = input(f"    Select output number (1-{len(available_outputs)}): ").strip()
                                    output_idx = int(output_idx_str) - 1
                                    if 0 <= output_idx < len(available_outputs):
                                        selected_output_name = available_outputs[output_idx]["name"]
                                    else:
                                        print("    Invalid output selection. Cannot link.")
                                        selected_output_name = None

                                if selected_output_name:
                                    parameters[param_name] = f"{{{{{selected_source_node['id']}.{selected_output_name}}}}}"
                                    use_specific_output = True
                                    print(f"    Parameter '{param_name}' will use output from {selected_source_node['id']}.{selected_output_name}")
                            else:
                                print(f"    Warning: Source node {selected_source_node['id']} or its ability schema/outputs not found. Cannot link.")
                        else:
                            print("    Invalid source node selection. Cannot link.")
                except (ValueError, EOFError, IndexError) as e: # Catch more errors during linking
                    print(f"\nError during linking input: {e}. Proceeding with manual input for '{param_name}'.")

            if not use_specific_output: # Changed from use_previous_output
                user_val = get_user_input(f"  {param_prompt}", param_type, param_default)
                if user_val is None: # EOF detected
                    print(f"Cancelled input for {param_name}.")
                    parameters[param_name] = param_default if param_default is not None else ""
                else:
                    parameters[param_name] = user_val

        node_data = {
            "id": current_node_id,
            "label": selected_ability_schema["display_name"],
            "ability_key": selected_ability_schema["key"],
            "parameters": parameters,
            "ui_position": {"x": 100 * (node_counter + 1), "y": 100}
        }
        nodes.append(node_data)

        if node_counter > 0:
            edges.append({
                "id": f"edge_{node_counter-1}_{node_counter}",
                "from_node": nodes[node_counter-1]["id"],
                "to_node": current_node_id,
                "label": "output"
            })

        node_counter += 1

    if not nodes: # If user chose to finish without adding any nodes
        return

    visual_plan = {
        "plan_name": "My Simulated Visual Plan",
        "nodes": nodes,
        "edges": edges,
        "execution_mode": "sequential"
    }

    print("\n--- Generated Visual Plan (JSON Preview) ---")
    print(json.dumps(visual_plan, indent=2))
    print("------------------------------------")

    print("\nExecuting visual plan with the agent...")
    execution_results = agent.execute_visual_plan(visual_plan)
    print_execution_results(execution_results)


if __name__ == '__main__':
    main()
