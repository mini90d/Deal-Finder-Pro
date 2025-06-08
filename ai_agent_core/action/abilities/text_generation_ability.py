# Ability for generating simple text, like poems.
import random

class TextGenerationAbility:
    def __init__(self):
        self.nouns = ["world", "cat", "sun", "moon", "flower", "river", "dream", "star", "sky", "tree"]
        self.adjectives = ["bright", "happy", "silent", "gentle", "mystic", "clear", "golden", "velvet"]
        self.verbs = ["shines", "sleeps", "flows", "dreams", "watches", "glows", "whispers", "dances"]

        self.templates = [
            "The {adjective} {noun} {verb}.",
            "A {noun} so {adjective} and free.",
            "{adjective_cap} {noun}s, a sight to see.", # adjective_cap will be capitalized
            "In {adjective} light, the {noun} {verb}.",
            "Beneath the {adjective} {noun}, secrets {verb}.",
            "Oh, {adjective} {noun}, how you {verb}!"
        ]

    def _get_random_word(self, word_type):
        if word_type == "noun":
            return random.choice(self.nouns)
        elif word_type == "adjective":
            return random.choice(self.adjectives)
        elif word_type == "verb":
            return random.choice(self.verbs)
        return ""

    def generate_poem(self, topic: str = None, num_lines: int = 4) -> str:
        """
        Generates a simple poem using templates and random word choices.
        The 'topic' parameter is noted but not deeply integrated into this simple version.
        """
        if topic:
            print(f"TextGenerationAbility generating poem about: {topic} ({num_lines} lines)")
            # Basic topic influence: add topic to nouns list if not too complex
            # This is a very naive way to include a topic.
            # For a real implementation, topic would influence word choices more deeply or select different templates.
            if topic.lower() not in self.nouns and len(topic.split()) == 1: # Only add single-word topics for simplicity
                temp_nouns = self.nouns + [topic.lower()]
            else:
                temp_nouns = self.nouns
        else:
            print(f"TextGenerationAbility generating poem ({num_lines} lines)")
            temp_nouns = self.nouns

        poem_lines = []
        for _ in range(num_lines):
            template_choice = random.choice(self.templates)
            line = template_choice # Make a copy to modify

            # Replace placeholders
            if "{adjective_cap}" in line:
                adj = self._get_random_word("adjective")
                line = line.replace("{adjective_cap}", adj.capitalize(), 1)

            # Standard replacements
            # Iterate to replace multiple occurrences of the same placeholder type if any template uses them
            while "{adjective}" in line:
                 line = line.replace("{adjective}", self._get_random_word("adjective"), 1)
            while "{noun}" in line: # Use temp_nouns which might include the topic
                 current_noun = random.choice(temp_nouns)
                 line = line.replace("{noun}", current_noun, 1)
            while "{verb}" in line:
                 line = line.replace("{verb}", self._get_random_word("verb"), 1)

            poem_lines.append(line)

        return "\n".join(poem_lines)

# Function to make the method easily discoverable for registration
def get_generate_poem_method():
    return TextGenerationAbility().generate_poem
