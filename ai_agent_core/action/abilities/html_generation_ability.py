# Ability for generating simple HTML webpages.

class HtmlGenerationAbility:
    def __init__(self):
        pass

    def generate_html(self, title: str, heading_text: str, body_content: str) -> str:
        """
        Generates a basic HTML page string with the given title, heading, and body content.
        """
        print(f"HtmlGenerationAbility generating HTML page with:")
        print(f"  Title: {title}")
        print(f"  Heading: {heading_text}")
        print(f"  Body: {body_content}")

        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
</head>
<body>
    <h1>{heading_text}</h1>
    <p>{body_content}</p>
</body>
</html>"""
        return html_template

# Function to make the method easily discoverable for registration.
def get_generate_html_method():
    return HtmlGenerationAbility().generate_html
