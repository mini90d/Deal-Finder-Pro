# Main class for AI Agents
from .understanding.parser import Parser
from .understanding.knowledge_base import KnowledgeBase
from .planning.planner import Planner
from .planning.task_decomposer import TaskDecomposer
from .action.action_executor import ActionExecutor
from .action.abilities import ABILITIES_REGISTRY # Assuming abilities are registered here
from .communication.message_bus import MessageBus

class Agent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        print(f"Initializing Agent {self.agent_id}...")

        # Initialize components
        self.parser = Parser()
        self.knowledge_base = KnowledgeBase()
        self.task_decomposer = TaskDecomposer()
        self.planner = Planner()
        # ActionExecutor needs a way to access abilities.
        # This could be a registry passed from abilities package or a direct import.
        self.action_executor = ActionExecutor(ABILITIES_REGISTRY)
        self.message_bus = MessageBus() # Optional, depending on architecture

        # Example: Subscribe to a general request topic
        self.message_bus.subscribe(f"agent/{self.agent_id}/request", self.handle_message_bus_request)

        print(f"Agent {self.agent_id} initialized successfully.")

    def process_request(self, raw_request):
        """
        Processes a direct request to the agent.
        This is the primary entry point for synchronous interactions.
        """
        print(f"Agent {self.agent_id} received direct request: {raw_request}")

        # 1. Understanding Phase
        structured_request = self.parser.parse_request(raw_request)
        self.knowledge_base.update(f"request_history_{self.agent_id}", structured_request) # Store request

        # Check for parsing failure
        if structured_request.get("intent") == "unrecognized_request" or structured_request.get("error"):
            error_message = structured_request.get("error", "Request not understood by parser.")
            print(f"Agent {self.agent_id} could not understand request: {raw_request}. Error: {error_message}")
            final_response = {
                "agent_id": self.agent_id,
                "request": raw_request,
                "error": error_message,
                "parsed": structured_request,
                "plan": [],
                "execution_results": []
            }
            return final_response

        # 2. Planning Phase
        # For simplicity, assuming abilities are known or planner can query them.
        # In a more complex system, abilities might be discovered or dynamically loaded.
        plan = self.planner.create_plan(structured_request, self.action_executor.abilities_registry.keys())

        # (Optional) Task Decomposition if plan involves complex tasks
        # For now, assume planner produces executable actions directly or handles decomposition.
        # decomposed_tasks = self.task_decomposer.decompose_task(structured_request.get("task_description",""))
        # plan = self.planner.create_plan_from_decomposed_tasks(decomposed_tasks, ...)

        # If planning results in an empty plan (e.g., for unrecognized but not error-marked intents from parser,
        # or if planner itself decides it cannot plan), this could also be a point to return a specific message.
        # For now, an empty plan will lead to empty execution_results, which is handled by CLI.
        # The primary "unrecognized" case is handled above.

        # 3. Action Phase
        # The action_executor now has an execute_plan method
        execution_results = self.action_executor.execute_plan(plan)

        final_response = {"agent_id": self.agent_id, "request": raw_request, "parsed": structured_request, "plan": plan, "execution_results": execution_results}
        print(f"Agent {self.agent_id} finished processing request. Response: {final_response}")
        return final_response

    def handle_message_bus_request(self, message):
        """
        Handles requests received via the message bus.
        This allows for asynchronous interactions.
        """
        print(f"Agent {self.agent_id} received message bus request: {message}")
        # The message could be a raw_request or a more structured message
        # depending on your message bus protocol.
        # For this example, let's assume it's a raw_request string.
        response = self.process_request(message)
        # Optionally, publish the response back to the message bus
        self.message_bus.publish(f"agent/{self.agent_id}/response", response)

    def get_available_abilities(self):
        """Returns a list of available abilities."""
        return list(self.action_executor.abilities_registry.keys())

# Example Usage (for testing purposes, normally an agent would be run by a host system)
if __name__ == '__main__':
    # This part will likely cause an error if run directly without proper package setup
    # (e.g. `python -m ai_agent_core.agent`) or if the current directory is not the project root.
    # To run this:
    # 1. Ensure your PYTHONPATH includes the directory containing 'ai_agent_core'
    #    OR run from the parent directory of 'ai_agent_core' using:
    #    `python -m ai_agent_core.agent`

    print("--- Attempting to run Agent 'Hello, World!' Python generation example ---")
    try:
        test_agent = Agent(agent_id="test_py_agent_001")

        # Test direct request for Python Hello World
        # request_string = "Create a Python Hello World program"
        # More specific to trigger current parser:
        request_string = "Make a python program that prints hello world"

        print(f"\nSending request to agent: '{request_string}'")
        response = test_agent.process_request(request_string)

        print("\n--- Agent Response ---")
        import json
        print(json.dumps(response, indent=2))
        print("--- End of Agent Response ---")

        if response and response.get("execution_results"):
            for result in response["execution_results"]:
                if result.get("ability_name") == "python_coding_ability.generate_code" and \
                   result.get("status") == "success":
                    print("\nSuccessfully generated Python code:")
                    print(result.get("result"))
                elif result.get("ability_name") == "html_generation_ability.generate_html" and \
                   result.get("status") == "success":
                    print("\nSuccessfully generated HTML code:")
                    print(result.get("result"))
                elif result.get("status") == "error":
                    print(f"\nError during ability execution '{result.get('ability_name')}': {result.get('message')}")

        print("-" * 30)

        # Test HTML generation
        html_request_string = "Create an HTML page with title 'My AI Webpage', heading 'AI Generated HTML' and body 'This is a paragraph created by an AI agent.'"
        print(f"\nSending HTML generation request to agent: '{html_request_string}'")
        html_response = test_agent.process_request(html_request_string)

        print("\n--- Agent Response (HTML Generation) ---")
        print(json.dumps(html_response, indent=2))
        print("--- End of Agent Response (HTML Generation) ---")

        if html_response and html_response.get("execution_results"):
            for result in html_response["execution_results"]:
                if result.get("ability_name") == "html_generation_ability.generate_html" and \
                   result.get("status") == "success":
                    print("\nSuccessfully generated HTML code:")
                    print(result.get("result"))
                elif result.get("status") == "error":
                    print(f"\nError during HTML ability execution '{result.get('ability_name')}': {result.get('message')}")
                elif result.get("ability_name") == "python_coding_ability.generate_code" and \
                     result.get("status") == "success" and "random.randint" in result.get("result", ""): # Check for game code
                    print("\nSuccessfully generated Python Number Guessing Game code:")
                    print(result.get("result"))


        print("-" * 30)

        # Test Python Number Guessing Game generation
        game_request_string = "Make a Python number guessing game"
        print(f"\nSending game generation request to agent: '{game_request_string}'")
        game_response = test_agent.process_request(game_request_string)

        print("\n--- Agent Response (Game Generation) ---")
        print(json.dumps(game_response, indent=2))
        print("--- End of Agent Response (Game Generation) ---")

        if game_response and game_response.get("execution_results"):
            for result in game_response["execution_results"]:
                if result.get("ability_name") == "python_coding_ability.generate_code" and \
                   result.get("status") == "success" and "random.randint" in result.get("result", ""):
                    print("\nSuccessfully generated Python Number Guessing Game code:")
                    print(result.get("result"))
                elif result.get("status") == "error":
                    print(f"\nError during game code generation ability execution '{result.get('ability_name')}': {result.get('message')}")
                elif result.get("ability_name") == "music_generation_ability.generate_melody" and \
                     result.get("status") == "success":
                    print("\nSuccessfully generated Melody:")
                    print(result.get("result"))

        print("-" * 30)

        # Test Music Generation
        music_request_string = "Generate a simple musical melody with 12 notes"
        # music_request_string = "Generate a tune" # Simpler request
        print(f"\nSending music generation request to agent: '{music_request_string}'")
        music_response = test_agent.process_request(music_request_string)

        print("\n--- Agent Response (Music Generation) ---")
        print(json.dumps(music_response, indent=2))
        print("--- End of Agent Response (Music Generation) ---")

        if music_response and music_response.get("execution_results"):
            for result in music_response["execution_results"]:
                if result.get("ability_name") == "music_generation_ability.generate_melody" and \
                   result.get("status") == "success":
                    print("\nSuccessfully generated Melody:")
                    print(result.get("result"))
                elif result.get("status") == "error":
                    print(f"\nError during music generation ability execution '{result.get('ability_name')}': {result.get('message')}")

        print("-" * 30)
        print(f"Agent {test_agent.agent_id} available abilities: {test_agent.get_available_abilities()}")
        print("--- Example Run Finished ---")

    except ImportError as e:
        print(f"\nError running agent example: {e}")
        print("This script needs to be run as a module from its project's root directory.")
        print("Try: `python -m ai_agent_core.agent` from the directory containing `ai_agent_core`.")
        import os
        print(f"Current working directory: {os.getcwd()}")
        print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
