import unittest
from ai_agent_core.planning.planner import Planner
#ABILITIES_METADATA is needed to inform the planner and to verify its decisions
from ai_agent_core.action.abilities import ABILITIES_METADATA

class TestPlannerChaining(unittest.TestCase):

    def setUp(self):
        self.planner = Planner()
        # Ensure ABILITIES_METADATA is loaded and available if planner relies on it at init (it doesn't directly, but good for context)
        # For this test, we mainly care that the planner *uses* the keys from ABILITIES_METADATA correctly.

    def test_create_poem_then_html_chain(self):
        raw_request = "Generate a poem about 'sunsets' with 2 lines AND THEN create an HTML page titled 'Sunset Poem' with body from poem and heading 'Beautiful Sunsets'"

        # This is what the parser is expected to produce for such a request:
        structured_request = {
            "intent": "chained_actions",
            "raw": raw_request,
            "sub_requests": [
                {
                    "intent": "generate_poem",
                    "task": "generate_poem",
                    "details": {"topic": "sunsets", "num_lines": 2},
                    "raw": "Generate a poem about 'sunsets' with 2 lines"
                },
                {
                    "intent": "generate_html_page",
                    "task": "generate_html_page",
                    "details": {
                        "title": "Sunset Poem",
                        "heading_text": "Beautiful Sunsets",
                        # Parser might put "with body from poem" here, planner should override
                        "body_content": "with body from poem"
                    },
                    "raw": "create an HTML page titled 'Sunset Poem' with body from poem and heading 'Beautiful Sunsets'"
                }
            ]
        }

        plan = self.planner.create_plan(structured_request)

        self.assertIsNotNone(plan, "Plan should not be None")
        self.assertEqual(len(plan), 2, "Plan should have two actions for a two-step chain")

        # Action 1: Poem Generation
        action1 = plan[0]
        self.assertEqual(action1.get("ability_name"), "text_generation_ability.generate_poem")
        self.assertEqual(action1.get("topic"), "sunsets")
        self.assertEqual(action1.get("num_lines"), 2)
        self.assertIn("node_id", action1, "Action 1 should have a node_id")
        node_id_action1 = action1["node_id"] # e.g., "node_0"

        # Action 2: HTML Generation
        action2 = plan[1]
        self.assertEqual(action2.get("ability_name"), "html_generation_ability.generate_html")
        self.assertEqual(action2.get("title"), "Sunset Poem")
        self.assertEqual(action2.get("heading_text"), "Beautiful Sunsets")
        self.assertIn("node_id", action2, "Action 2 should have a node_id")

        # Check for placeholder linking output of action1 to input of action2
        # The poem ability produces "generated_poem"
        # The html ability can accept "body_content"
        expected_placeholder = f"{{{{{node_id_action1}.generated_poem}}}}"
        self.assertEqual(action2.get("body_content"), expected_placeholder,
                         f"HTML body_content should be placeholder '{expected_placeholder}'")

if __name__ == '__main__':
    unittest.main()
