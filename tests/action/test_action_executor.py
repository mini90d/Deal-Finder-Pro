import unittest
from unittest.mock import MagicMock
from ai_agent_core.action.action_executor import ActionExecutor
# Import ABILITIES_METADATA to correctly structure mock outputs based on schema
from ai_agent_core.action.abilities import ABILITIES_METADATA

class TestActionExecutorChaining(unittest.TestCase):

    def setUp(self):
        # Mock abilities registry
        self.mock_abilities_registry = {
            "text_generation_ability.generate_poem": MagicMock(return_value="This is a lovely poem."),
            "html_generation_ability.generate_html": MagicMock(return_value="<html><body>Poem</body></html>")
        }
        self.action_executor = ActionExecutor(self.mock_abilities_registry)

        # Ensure the mock abilities have metadata if ActionExecutor uses it to determine output names
        # This is crucial for the execute_plan's output capturing logic.
        # We are directly using ABILITIES_METADATA imported, assuming it's accurate.
        # If ABILITIES_METADATA was also mocked, these would need to align.

    def test_execute_poem_to_html_chain(self):
        # This plan structure is what the Planner is expected to create
        test_plan = [
            {
                "node_id": "node_0",
                "ability_name": "text_generation_ability.generate_poem",
                "topic": "dreams", # Example param
                "num_lines": 2      # Example param
            },
            {
                "node_id": "node_1",
                "ability_name": "html_generation_ability.generate_html",
                "title": "Dream Poem", # Example param
                # This placeholder links to the output of node_0's poem generation
                "body_content": "{{node_0.generated_poem}}"
            }
        ]

        # Mock the ABILITIES_METADATA entries for the abilities used in this test
        # to ensure the ActionExecutor correctly names the outputs.
        # This is important because ActionExecutor.execute_plan uses ABILITIES_METADATA
        # to determine the key for storing the output (e.g., "generated_poem").
        original_metadata = ABILITIES_METADATA.copy() # Keep a copy to restore later if needed
        ABILITIES_METADATA['text_generation_ability.generate_poem'] = {
            "key": "text_generation_ability.generate_poem",
            "produces_outputs": [{"name": "generated_poem", "type": "str"}]
            # Other metadata fields omitted for brevity in test setup
        }
        ABILITIES_METADATA['html_generation_ability.generate_html'] = {
            "key": "html_generation_ability.generate_html",
            "parameters": [ # Parameters that the ability expects
                {"name": "title", "type": "str"},
                {"name": "body_content", "type": "str"}
            ],
            "produces_outputs": [{"name": "html_document", "type": "str"}]
            # Other metadata fields omitted
        }


        execution_results = self.action_executor.execute_plan(test_plan)

        self.assertEqual(len(execution_results), 2, "Should have two execution results")
        self.assertEqual(execution_results[0]["status"], "success")
        self.assertEqual(execution_results[0]["result"], "This is a lovely poem.")

        self.assertEqual(execution_results[1]["status"], "success")
        self.assertEqual(execution_results[1]["result"], "<html><body>Poem</body></html>")

        # Verify that the generate_html ability was called with the poem from the first step
        # The actual call to generate_html_mock will have parameters resolved from placeholders
        html_generation_call_args = self.mock_abilities_registry["html_generation_ability.generate_html"].call_args
        self.assertIsNotNone(html_generation_call_args, "HTML generation ability should have been called")

        # call_args is a tuple ((args), {kwargs}). We are interested in kwargs.
        called_kwargs = html_generation_call_args.kwargs
        self.assertEqual(called_kwargs.get("body_content"), "This is a lovely poem.")
        self.assertEqual(called_kwargs.get("title"), "Dream Poem")

        # Restore original ABILITIES_METADATA if modified.
        # In a real test suite with many tests, better to use unittest.mock.patch.dict
        # For this single subtask, direct modification and restoration is simpler.
        ABILITIES_METADATA.clear()
        ABILITIES_METADATA.update(original_metadata)


if __name__ == '__main__':
    unittest.main()
