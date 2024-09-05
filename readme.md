# Desktop GPT Application
### Description
**Desktop GPT** is a desktop application built using Python and PyQt5 that integrates with OpenAI's API to provide an interactive chat experience. The application allows users to send prompts and receive AI-generated responses in real-time. It features a customizable user interface with text input, chat history, and a settings window for managing API settings.

### Key Features:
-**User Input & Chat History:** Users can enter text prompts in a custom QTextEdit widget. The chat history is displayed with both user inputs and AI responses, styled using HTML and CSS-like styles.
-**OpenAI Integration:** The application uses OpenAI's API to generate responses, with the API calls handled in a separate thread (OpenAIWorker) to keep the UI responsive.
-**UI Design:** The application employs a simple and modern UI, including rounded buttons, custom fonts, and adjustable window sizes based on screen resolution.
-**Real-time Token Count:** Displays the number of context tokens used in the conversation, which is updated in real-time.

### Technologies Used:
**Python:** Core language for logic and API integration.
**PyQt5:** For building the desktop interface and handling UI components.
**OpenAI API:** To generate and display AI-based responses.

### TODO List:
Add a notification for the API connection status.
Fix issues with the scroll bar in the chat history.
Improve UI aesthetics by making elements rounder.
Update the settings screen to remove unnecessary elements (e.g., the summary for API key input).

### Future Enhancements:
Additional settings and preferences for users to adjust the API behavior and UI styles.
Improved error handling and connection stability.