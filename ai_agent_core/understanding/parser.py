# This module will be responsible for parsing incoming requests and data.
# It will transform raw input into a structured format that the agent can understand.

class Parser:
    def __init__(self):
        # Initialize parser-specific settings or models
        pass

    def parse_request(self, raw_request: str):
        """
        Parses a raw request string to identify language and task.
        Looks for keywords like "python" and "hello world".
        Handles chained commands via " AND THEN ".
        """
        print(f"Parsing request: {raw_request}")

        # Check for chained commands first using " AND THEN " as a delimiter.
        # This allows users to specify sequences of actions, e.g., "Generate a poem AND THEN make an HTML page with it."
        # The Planner will later be responsible for potentially linking the output of the first action
        # to the input of the second action if their abilities are compatible.
        import re
        chain_delimiter_match = re.search(r"\s+AND\s+THEN\s+", raw_request, re.IGNORECASE)

        if chain_delimiter_match:
            delimiter = chain_delimiter_match.group(0) # Get the actual matched delimiter (e.g., " AND THEN ")
            parts = raw_request.split(delimiter, 1) # Split into two parts at the first occurrence

            if len(parts) == 2:
                print(f"Chained command detected. Part 1: '{parts[0]}', Part 2: '{parts[1]}'")
                # Recursively parse each part of the chained command.
                # This creates a nested structure where each sub-request is itself a parsed command.
                # Example: parsed_part1 = {"intent": "generate_poem", ...}, parsed_part2 = {"intent": "generate_html_page", ...}
                parsed_part1 = self.parse_request(parts[0].strip())
                parsed_part2 = self.parse_request(parts[1].strip())

                # The overall intent is "chained_actions", and it holds the sub-requests.
                return {
                    "intent": "chained_actions",
                    "raw": raw_request, # The original full request string
                    "sub_requests": [parsed_part1, parsed_part2], # List of parsed sub-requests
                    "chain_delimiter": delimiter.strip()
                }
            else: # Should not happen with split(..., 1) on a successful match, but as a safeguard.
                print(f"Warning: Chained command delimiter found, but split resulted in {len(parts)} parts. Proceeding as single command.")
                # Fall through to normal parsing for the whole raw_request

        # If not a chained command (or if split failed unexpectedly), proceed with normal parsing
        raw_request_lower = raw_request.lower()
        structured_request = {"language": None, "task": None, "raw": raw_request}

        # Default intent
        structured_request["intent"] = "unknown"

        if "python" in raw_request_lower:
            structured_request["language"] = "python"
            if "hello world" in raw_request_lower or "helloworld" in raw_request_lower:
                structured_request["task"] = "hello_world"
                structured_request["intent"] = "hello_world_python"
            elif ("number guessing game" in raw_request_lower or \
                  ("game" in raw_request_lower and "number" in raw_request_lower and "guess" in raw_request_lower)):
                structured_request["task"] = "generate_number_guessing_game"
                structured_request["intent"] = "generate_number_guessing_game_python"

        elif "html" in raw_request_lower or "webpage" in raw_request_lower:
            structured_request["language"] = "html"
            structured_request["task"] = "generate_html_page"
            structured_request["intent"] = "generate_html_page"

            details = {"title": "My Page", "heading_text": "Welcome", "body_content": "Default content."}

            import re

            # Regex patterns for HTML generation
            # Pattern to capture intent and all params if explicitly quoted or using colon
            html_pattern_keywords = re.compile(r"""
                (?:make|create|generate|build)\s*(?:an?\s*)?(html|webpage|page) # Intent keywords
                (?: # Parameters section
                    # Option 1: Parameters introduced by a keyword like "with", "featuring", etc. followed by colons/equals
                    \s*(?:with|for|having|featuring|called|named|using)\s*:
                    (?: # Optional title
                        \s*title\s*[:=]?\s*['\"]?(?P<title>[^'\"]*?)['\"]?
                    )?
                    (?: # Optional heading
                        \s*(?:and|,)?\s*(?:heading|header)\s*[:=]?\s*['\"]?(?P<heading>[^'\"]*?)['\"]?
                    )?
                    (?: # Optional body
                        \s*(?:and|,)?\s*(?:body|content)\s*[:=]?\s*['\"]?(?P<body_content>[^'\"]*?)['\"]?
                    )?
                | # Option 2: Less structured parameters appearing after the main intent phrase
                    (?: # Optional title alt
                        \s*title\s*[:=]?\s*['\"](?P<title_alt>[^'\"]+)['\"]?
                    )?
                    (?: # Optional heading alt
                        \s*(?:and|,)?\s*(?:heading|header)\s*[:=]?\s*['\"](?P<heading_alt>[^'\"]+)['\"]?
                    )?
                    (?: # Optional body_content alt
                        \s*(?:and|,)?\s*(?:body|content)\s*[:=]?\s*['\"](?P<body_content_alt>[^'\"]+)['\"]?
                    )?
                )? # End of parameters section (making the whole section optional after intent)
                """, re.IGNORECASE | re.VERBOSE # VERBOSE allows comments and nicer formatting
            )

            # Simpler patterns for individual parameters, useful if main pattern doesn't get all
            title_pattern = re.compile(r"(?:title|titled)\s*[:=]?\s*['\"](?P<title>[^'\"]+)['\"]", re.IGNORECASE)
            heading_pattern = re.compile(r"(?:heading|header)\s*[:=]?\s*['\"](?P<heading>[^'\"]+)['\"]", re.IGNORECASE)
            body_pattern = re.compile(r"(?:body|content)\s*[:=]?\s*['\"](?P<body_content>[^'\"]+)['\"]", re.IGNORECASE)

            match = html_pattern_keywords.search(raw_request) # Use raw_request for case-sensitive original values if needed, or raw_request_lower

            if match:
                # If primary pattern matched, use its groups, preferring explicit over alt
                title = match.group("title") or match.group("title_alt")
                heading = match.group("heading") or match.group("heading_alt")
                body = match.group("body_content") or match.group("body_content_alt")

                if title: details["title"] = title.strip()
                if heading: details["heading_text"] = heading.strip()
                if body: details["body_content"] = body.strip()

            # If primary pattern didn't capture some, or didn't match, try individual ones
            # (This ensures we still capture details even if the main sentence structure isn't perfectly matched)
            if not details.get("title") or details["title"] == "My Page": # Try to find if not set or default
                title_m = title_pattern.search(raw_request)
                if title_m: details["title"] = title_m.group("title").strip()

            if not details.get("heading_text") or details["heading_text"] == "Welcome":
                heading_m = heading_pattern.search(raw_request)
                if heading_m: details["heading_text"] = heading_m.group("heading").strip()

            if not details.get("body_content") or details["body_content"] == "Default content.":
                body_m = body_pattern.search(raw_request)
                if body_m: details["body_content"] = body_m.group("body_content").strip()

            structured_request["details"] = details

        elif "music" in raw_request_lower or "melody" in raw_request_lower or \
             ("generate" in raw_request_lower and ("tune" in raw_request_lower or "song" in raw_request_lower)):
            structured_request["task"] = "generate_melody"
            structured_request["intent"] = "generate_melody"
            details = {"num_notes": 8} # Default num_notes

            import re
            num_notes_match = re.search(r"(\d+)\s*notes", raw_request_lower)
            if num_notes_match:
                try:
                    details["num_notes"] = int(num_notes_match.group(1))
                except ValueError:
                    pass # Keep default if conversion fails

            # Could add scale and octave parsing here if needed
            structured_request["details"] = details

        elif "poem" in raw_request_lower or \
             ("write" in raw_request_lower and "text" in raw_request_lower) or \
             ("generate" in raw_request_lower and "verse" in raw_request_lower) or \
             ("compose" in raw_request_lower and "text" in raw_request_lower):
            structured_request["task"] = "generate_poem"
            structured_request["intent"] = "generate_poem"
            details = {"topic": None, "num_lines": 4} # Default num_lines

            import re
            # Try to extract number of lines
            num_lines_match = re.search(r"(\d+)\s*(?:lines|verses)", raw_request_lower)
            if num_lines_match:
                try:
                    details["num_lines"] = int(num_lines_match.group(1))
                except ValueError:
                    pass # Keep default

            # Try to extract topic (simple "about X" or "on Y" for now)
            topic_match = re.search(r"(?:about|on|regarding)\s+['\"]?([^'\"]+)['\"]?", raw_request_lower)
            if topic_match:
                details["topic"] = topic_match.group(1).strip()

            structured_request["details"] = details

        # If by this point intent is still unknown, mark it as unrecognized
        if structured_request.get("intent") == "unknown" and structured_request.get("task") is None:
            structured_request["intent"] = "unrecognized_request"
            structured_request["error"] = "Could not understand the core task of the request."

        print(f"Parsed request: {structured_request}")
        return structured_request
