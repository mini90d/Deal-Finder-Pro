# Ability for generating simple musical melodies.
import random

class MusicGenerationAbility:
    def __init__(self):
        self.scales = {
            'C_major': ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        }
        self.durations = {
            'Q': 'Quarter',
            'H': 'Half',
            'W': 'Whole',
            'E': 'Eighth' # Added Eighth note for more variety
        }

    def generate_melody(self, num_notes: int = 8, scale_name: str = 'C_major', base_octave: int = 4) -> str:
        """
        Generates a simple musical melody as a string of notes.
        Example output: "C4 Q, E4 Q, G4 H, ..."
        """
        if scale_name not in self.scales:
            return f"Error: Scale '{scale_name}' not recognized. Available: {list(self.scales.keys())}"

        scale_notes = self.scales[scale_name]
        duration_chars = list(self.durations.keys())

        melody_parts = []
        print(f"MusicGenerationAbility generating melody with {num_notes} notes from {scale_name} scale.")

        for _ in range(num_notes):
            note = random.choice(scale_notes)
            duration_char = random.choice(duration_chars)
            melody_parts.append(f"{note}{base_octave} {duration_char}")

        melody_string = ", ".join(melody_parts)
        print(f"Generated melody: {melody_string}")
        return melody_string

# Function to make the method easily discoverable for registration
def get_generate_melody_method():
    return MusicGenerationAbility().generate_melody
