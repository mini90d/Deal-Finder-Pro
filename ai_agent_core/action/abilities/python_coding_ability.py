# Ability for generating Python code.

class PythonCodingAbility:
    def __init__(self):
        # Any initialization if needed, e.g., loading templates or linters
        pass

    def generate_code(self, code_details: str, language: str = "python"):
        """
        Generates Python code based on the details provided.
        For "Hello, World!", it directly returns the print statement.
        """
        if language.lower() != "python":
            raise ValueError(f"This ability only supports Python, not {language}")

        print(f"PythonCodingAbility generating code for: {code_details}")
        # In a real scenario, this would involve more complex generation logic
        # based on 'code_details' which might be a more structured input.
        # For "Hello, World!", the planner already provides the exact code.
        return code_details

    def execute_code(self, code_string: str):
        """
        (Optional) Executes a given Python code string.
        NOTE: This is a dangerous operation and should be heavily sandboxed
        or disabled in production environments.
        For this prototype, it's included for demonstration.
        """
        print(f"PythonCodingAbility attempting to execute code:\n{code_string}")
        try:
            # Using a restricted scope for exec
            # In a real system, use a proper sandbox (e.g., Docker container, restricted interpreter)
            exec_globals = {}
            exec(code_string, exec_globals)
            return {"status": "success", "output": "Code executed (no direct output captured)."}
        except Exception as e:
            print(f"Error executing code: {e}")
            return {"status": "error", "message": str(e)}

# It's good practice to also have a function to register this ability
# or make it easily discoverable by the abilities.__init__.py
def get_ability():
    return PythonCodingAbility()

def get_generate_code_method():
    return PythonCodingAbility().generate_code
