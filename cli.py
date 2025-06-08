# Basic Command-Line Interface for the AI Agent
import json
import sys
import os

# Adjust Python path to find the ai_agent_core module
# This assumes cli.py is in the root and ai_agent_core is a subdirectory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from ai_agent_core.agent import Agent
except ImportError:
    print("Error: Could not import the Agent class. ")
    print("Ensure that 'ai_agent_core' is in your Python path or in the same directory.")
    print("If running from the root of the project, this script should find it.")
    sys.exit(1)

def print_agent_output(response):
    """Helper function to print the relevant part of the agent's response."""
    if not response:
        print("Agent did not return a response.")
        return

    print("\n--- Agent Output ---")
    if response.get("error"): # Check for top-level error first
        print(f"Sorry, I couldn't process that request: {response.get('error')}")
    elif response.get("execution_results"):
        all_successful = True
        for result in response["execution_results"]:
            if result.get("status") == "success":
                output = result.get("result")
                if output:
                    print(output) # Print successful output directly
                else:
                    # If 'result' is empty but success, maybe just confirm action name
                    print(f"Action '{result.get('ability_name', 'unknown action')}' completed successfully.")
            elif result.get("status") == "error":
                all_successful = False
                print(f"Error during agent execution: {result.get('message')}")
            else: # Fallback for other statuses or structure
                all_successful = False
                print(json.dumps(result, indent=2))

        if not response["execution_results"] and not response.get("error"): # Empty plan, no top-level error
             print("The agent processed your request, but there was nothing specific to output.")

    elif not response.get("execution_results") and not response.get("error"):
         print("The agent processed your request, but there was no specific output or error reported.")
    else:
        # Fallback for completely unexpected response structure
        print("Received an unusual response from the agent:")
        print(json.dumps(response, indent=2))
    print("--------------------")


def main():
    print("Initializing AI Agent...")
    try:
        agent = Agent(agent_id="cli_agent_001")
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        sys.exit(1)

    print("\nWelcome to the AI Creative Agent CLI!")

    while True:
        print("\nWhat would you like to do?")
        print("1: Generate Python \"Hello, World!\"")
        print("2: Generate Python Number Guessing Game")
        print("3: Create a simple HTML page")
        print("4: Compose a musical melody")
        print("5: Generate a short poem")
        print("6: Generate Poem and display on HTML Page")
        print("0: Exit")

        try:
            choice = input("Enter your choice: ").strip()
        except EOFError: # Handle Ctrl+D or redirected input ending
            print("\nExiting.")
            break

        if choice == '0':
            print("Exiting.")
            break
        elif choice == '1':
            request_string = "Make a python program that prints hello world" # REVERTED
            print(f"\nRequesting: {request_string}")
            response = agent.process_request(request_string)
            print_agent_output(response)
        elif choice == '2':
            request_string = "Make a Python number guessing game"
            print(f"\nRequesting: {request_string}")
            response = agent.process_request(request_string)
            print_agent_output(response)
        elif choice == '3':
            print("\n--- Create HTML Page ---")
            try:
                title = input("Enter page title: ")
                heading_text = input("Enter heading text: ")
                body_content = input("Enter body content: ")
                request_string = f"Create an HTML page with title '{title}', heading '{heading_text}' and body '{body_content}'"
                print(f"\nRequesting: HTML page generation...")
                response = agent.process_request(request_string)
                print_agent_output(response)
            except EOFError:
                print("\nHTML creation cancelled. Returning to main menu.")
            except Exception as e:
                print(f"An error occurred during HTML page creation: {e}")
        elif choice == '4':
            print("\n--- Compose Musical Melody ---")
            num_notes_str = input("Enter number of notes (default is 8, press Enter): ").strip()
            num_notes = 8 # Default
            if num_notes_str:
                try:
                    num_notes = int(num_notes_str)
                    if num_notes <= 0:
                        print("Number of notes must be positive. Using default (8).")
                        num_notes = 8
                except ValueError:
                    print("Invalid input for number of notes. Using default (8).")

            request_string = f"Generate a simple musical melody with {num_notes} notes"
            print(f"\nRequesting: {request_string}")
            response = agent.process_request(request_string)
            print_agent_output(response)
        elif choice == '5':
            print("\n--- Generate Poem ---")
            topic = input("Enter a topic for the poem (optional, press Enter to skip): ").strip()
            num_lines_str = input("Enter number of lines (default is 4, press Enter): ").strip()
            num_lines = 4 # Default

            if num_lines_str:
                try:
                    num_lines = int(num_lines_str)
                    if num_lines <= 0:
                        print("Number of lines must be positive. Using default (4).")
                        num_lines = 4
                except ValueError:
                    print("Invalid input for number of lines. Using default (4).")

            request_parts = ["Compose a poem"]
            if topic:
                request_parts.append(f"about \"{topic}\"")
            request_parts.append(f"with {num_lines} lines")
            request_string = " ".join(request_parts)

            print(f"\nRequesting: {request_string}")
            response = agent.process_request(request_string)
            print_agent_output(response)
        elif choice == '6':
            print("\n--- Generate Poem and Display on HTML Page ---")
            num_lines_poem_str = input("Enter number of lines for the poem (default 4): ").strip()
            num_lines_poem = 4
            if num_lines_poem_str:
                try:
                    num_lines_poem = int(num_lines_poem_str)
                    if num_lines_poem <=0: num_lines_poem = 4
                except ValueError:
                    print("Invalid number for poem lines, using default 4.")

            html_title = input("Enter HTML page title (default 'My Poem Page'): ").strip()
            if not html_title: html_title = "My Poem Page"

            # Construct the chained request
            # The HTML body will use the placeholder {{PREVIOUS_SUCCESSFUL_OUTPUT}}
            # The HTML heading will be derived from the title or a default.
            html_heading = html_title # Simple choice for heading

            request_string = (
                f"Generate a poem with {num_lines_poem} lines "
                f"AND THEN create an HTML page titled '{html_title}' "
                f"with heading '{html_heading}' " # Using title as heading for simplicity
                f"and body '{{{{PREVIOUS_SUCCESSFUL_OUTPUT}}}}'" # Escaped curly braces for f-string
            )
            print(f"\nRequesting chained action: {request_string}")
            response = agent.process_request(request_string)
            print_agent_output(response) # Should print the final HTML

        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
