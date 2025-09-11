# AI Agent Application Design

This document outlines the proposed application structure, key UI design elements, and user flows for an AI agent application with a simple web interface for its initial version.

## 1. Application Structure

The application will be composed of three main parts: Frontend, Backend, and the AI Agent Core.

### 1.1. Frontend

*   **Description:** The client-side interface that users interact with. For the initial version, this will be a simple web-based UI.
*   **Responsibilities:**
    *   Presenting the user interface elements (input areas, controls, output displays).
    *   Capturing user input (prompts, commands, configuration settings).
    *   Sending user requests to the Backend.
    *   Receiving responses and updates from the Backend.
    *   Displaying agent progress, generated content, logs, and any requests for human intervention.
    *   Managing local UI state (e.g., toggling display elements, managing form inputs).
*   **Technology (Initial Thoughts):**
    *   HTML, CSS, JavaScript.
    *   A simple JavaScript framework/library (e.g., Vanilla JS with Fetch API, or a lightweight option like Svelte or Preact) to manage UI updates dynamically.

### 1.2. Backend

*   **Description:** The server-side logic that handles requests from the Frontend, interacts with the AI Agent Core, and manages application state.
*   **Responsibilities:**
    *   **API Endpoints:** Exposing HTTP API endpoints for the Frontend to communicate with (e.g., `/submit_task`, `/get_status`, `/provide_feedback`).
    *   **Request Handling & Validation:** Receiving requests from the Frontend, validating inputs.
    *   **Session Management:** (If needed) Managing user sessions or task contexts.
    *   **Task Queuing/Management:** (Potentially) Managing a queue for tasks submitted to the AI Agent Core, especially for long-running operations.
    *   **Communication Bridge:** Relaying tasks and data between the Frontend and the AI Agent Core. This might involve WebSockets for real-time updates if the AI Agent Core supports it, or polling mechanisms.
    *   **Data Persistence (Basic):** Storing task history, user preferences (if any), or basic logs. More complex knowledge would reside in the AI Agent's Knowledge Base.
*   **Technology (Initial Thoughts):**
    *   Python (e.g., Flask, FastAPI) due to its strong AI/ML ecosystem and ease of integration with the AI Agent Core if it's also Python-based.
    *   Alternatively, Node.js (e.g., Express.js) if real-time communication (WebSockets) is a primary concern.

### 1.3. AI Agent Core

*   **Description:** This is the intelligent part of the application, based on the `ai_agent_architecture.md` document. It processes tasks, interacts with AI models (like Gemini), and manages its own operations.
*   **Responsibilities:**
    *   Implementing the core logic defined in `ai_agent_architecture.md` (Orchestration Engine, Interaction Layer (internal), Knowledge Base).
    *   Receiving tasks from the Backend.
    *   Executing tasks based on the configured autonomy level.
    *   Interacting with external services and AI models (e.g., Google Gemini API via `gemini_interaction.py`).
    *   Managing its internal state and knowledge.
    *   Sending results, progress updates, and requests for human input back to the Backend.
*   **Technology (Initial Thoughts):**
    *   Python, leveraging libraries like `google-generativeai`.
    *   The components (Orchestration, Knowledge Base access, etc.) will be Python modules/classes.
    *   Communication with the Backend could be via direct function calls (if co-located), an internal API, or a message queue.

## 2. Key UI Design Elements (Simple Web Interface)

The initial web interface will be kept simple and functional.

### 2.1. Input Area

*   **Description:** A primary text area where users can type their main prompt or command for the AI agent.
*   **Elements:**
    *   Large, multi-line text input field.
    *   "Submit" or "Run Agent" button.

### 2.2. Generation Controls / Configuration

*   **Description:** Controls to configure the agent's behavior for the current task.
*   **Elements:**
    *   **Autonomy Level Selector:** A dropdown or radio buttons to select:
        *   "Fully Autonomous"
        *   "Human-in-the-Loop (Confirm Steps)"
        *   "Assistant Mode (Execute Explicit Commands)"
    *   **(Optional/Advanced)** Model selection dropdown (if multiple models are available).
    *   **(Optional/Advanced)** Parameters for specific tools or tasks (e.g., creativity level, max output length). Initially, these might be hardcoded or implicitly handled.

### 2.3. Progress/Output Display Area

*   **Description:** An area to display the agent's current status, ongoing actions, generated content, logs, and any prompts for user interaction.
*   **Elements:**
    *   **Status Indicator:** A text field or icon showing current status (e.g., "Idle", "Processing...", "Waiting for Input", "Task Completed", "Error").
    *   **Main Output/Content Area:** Displays the primary output from the agent (e.g., generated text, summarized information, code snippets).
    *   **Log/Thought Process Area:** (Collapsible or separate tab) Shows a more detailed log of the agent's actions, decisions, tool usage, and intermediate results. This is crucial for transparency and debugging.
    *   **Human Input Prompt:** If in HITL mode, this area will clearly display the question or options the agent needs human feedback on, along with input fields or buttons for the user to respond.

## 3. User Flow for Each Autonomy Level

### 3.1. Fully Autonomous Mode

1.  **User Input:** User types a high-level goal/prompt into the **Input Area** (e.g., "Research current AI trends in healthcare and write a summary").
2.  **Configuration:** User selects "Fully Autonomous" from the **Autonomy Level Selector**.
3.  **Submission:** User clicks "Submit".
4.  **Frontend to Backend:** Frontend sends the prompt and autonomy setting to the Backend.
5.  **Backend to AI Agent Core:** Backend forwards the task to the AI Agent Core.
6.  **AI Agent Processing:**
    *   Orchestration Engine decomposes the task, plans steps, selects tools (e.g., web search, text generation via Gemini API).
    *   Agent executes all steps without pausing for user confirmation.
    *   Progress and intermediate steps (optional, based on verbosity settings) are streamed to the **Progress/Output Display Area** (via Backend & Frontend).
7.  **Output Display:**
    *   The final result (e.g., the summary report) is displayed in the **Main Output/Content Area**.
    *   The **Status Indicator** shows "Task Completed".
    *   Detailed logs are available in the **Log/Thought Process Area**.

### 3.2. Human-in-the-Loop (HITL) Mode

1.  **User Input:** User types a prompt (e.g., "Draft an email to a client about project delays, then find three potential solutions to propose").
2.  **Configuration:** User selects "Human-in-the-Loop" from the **Autonomy Level Selector**.
3.  **Submission:** User clicks "Submit".
4.  **Frontend to Backend & AI Agent Core:** Request flows as above.
5.  **AI Agent Processing (with Pauses):**
    *   Agent starts processing (e.g., drafts the email).
    *   At a pre-defined checkpoint (e.g., after drafting the email but before sending or before researching solutions), the Orchestration Engine pauses.
    *   The agent sends the draft email and a question like "Review the draft email. Approve or suggest edits?" to the Backend.
6.  **User Interaction:**
    *   Frontend displays the draft email and the question in the **Progress/Output Display Area** (specifically in a human input section).
    *   **Status Indicator** shows "Waiting for Input".
    *   User reviews the draft, potentially edits it in a provided text box, and clicks "Approve" or "Submit Feedback".
7.  **Feedback to Agent:** Frontend sends user's feedback/approval to the Backend, which relays it to the AI Agent Core.
8.  **Agent Resumes:**
    *   AI Agent Core receives the feedback and continues to the next step (e.g., researches solutions).
    *   It might pause again for confirmation on the proposed solutions.
9.  **Output Display:** Process repeats until the task is complete. Final output and logs are displayed.

### 3.3. Assistant Mode

1.  **User Input:** User types a specific command (e.g., "Generate Python code to read a CSV file using pandas").
2.  **Configuration:** User selects "Assistant Mode" from the **Autonomy Level Selector**.
3.  **Submission:** User clicks "Submit".
4.  **Frontend to Backend & AI Agent Core:** Request flows as above.
5.  **AI Agent Processing (Direct Execution):**
    *   The Orchestration Engine treats the input as a direct instruction for a tool or capability (e.g., code generation via Gemini API).
    *   The agent executes this specific command.
    *   The **Log/Thought Process Area** might show which tool was directly invoked.
6.  **Output Display:**
    *   The generated code snippet is displayed in the **Main Output/Content Area**.
    *   **Status Indicator** shows "Task Completed".
7.  **Follow-up (User-driven):** The user then provides the next explicit command (e.g., "Now, write a function to calculate the average of a column named 'value' from that CSV data"). The agent doesn't proactively plan multiple steps ahead.

This design focuses on a clear separation of concerns and provides a flexible framework for developing the AI agent application, starting with a simple yet functional web interface.
