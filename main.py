"""This script contains the main application logic for the Desktop GPT application."""

# pylint: disable=no-name-in-module
# pylint: disable=no-member
# pylint: disable=import-error
# God pylint is annoying sometimes

# TODO: Add a note that says if api is connected
# TODO: Fix scroll bar
# TODO: Make things rounder
# TODO: Remove summary for settings screen with apikey input

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QPushButton
from openai_caller import OpenAIReply
from syntax_highlighter import syntax

class OpenAIWorker(QtCore.QThread):
    """A worker thread for running OpenAI API calls in the background"""
    result_ready = QtCore.pyqtSignal(str)
    tokens_updated = QtCore.pyqtSignal(int)

    def __init__(self, openai_reply, method, prompt=None):
        super().__init__()
        self.openai_reply = openai_reply
        self.method = method
        self.prompt = prompt

    def run(self):
        """Run the OpenAI API call in the background"""
        # Generate the AI reply
        response = self.openai_reply.generate_openai_reply(self.prompt)
        # Emit the result
        self.result_ready.emit(response)
        # Emit the updated token count
        self.tokens_updated.emit(self.openai_reply.context_tokens)

class MainWindow(QtWidgets.QMainWindow):
    """The main application window for Desktop GPT"""
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)

        # Get the screen size
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Calculate the window size as one-third of the screen size
        window_width = screen_width // 2
        window_height = screen_height // 2

        # Set the window size
        self.resize(window_width, window_height)
        self.setStyleSheet("background-color: rgb(135, 135, 135);")

        self.setWindowTitle("Desktop GPT")

        self.settings_window = QtWidgets.QMessageBox()
        self.settings_window.setWindowTitle("Settings")
        self.settings_window.setText("Settings Placeholder")

        self.openai_reply = OpenAIReply()

        self.chat_history = self.findChild(QtWidgets.QTextEdit, 'chatHistory')
        self.chat_history.setReadOnly(True)

        self.user_input = self.findChild(QtWidgets.QTextEdit, 'userText')
        # Disable rich text formatting in user input
        self.user_input.setAcceptRichText(False)
        self.user_input.textChanged.connect(self.input_resizing)
        self.user_input.installEventFilter(self)

        self.user_input_frame = self.findChild(QtWidgets.QWidget, 'userInputs')
        self.uif_init_size = 0

        self.send_button = self.findChild(QPushButton, 'sendButton')
        self.send_button.clicked.connect(self.send_button_clicked)

        self.settings_button = self.findChild(QPushButton, 'settingsButton')
        self.settings_button.clicked.connect(self.settings_button_clicked)

        self.token_label = self.findChild(QtWidgets.QLabel, 'tokenCount')

        # Set the styles for the widgets

        self.chat_history.setStyleSheet("""
                                        background-color: lightgrey;
                                        font-size: 40px;
                                        border: 2px solid black;
                                        border-radius: 10px;
                                        font-family: 'Myriad Pro';
                                        """)

        self.user_input.setStyleSheet("""
                                        background-color: lightgrey;
                                        font-size: 32px;
                                        border: 2px solid black;
                                        border-radius: 75px;
                                        padding: 30px 10px 30px 25px;
                                        font-family: 'Myriad Pro';
                                        """)

        self.send_button.setStyleSheet("""
                                        QPushButton {
                                            font-size: 28px;
                                            color: white;
                                            border: 2px solid black;
                                            border-radius: 25px;
                                            padding: 10px;
                                            background-color: grey;
                                        }
                                        QPushButton:hover {
                                            background-color: dimgrey;
                                        }
                                        QPushButton:pressed {
                                            background-color: #585858; /* Darker grey */
                                            border-style: inset;
                                        }
                                    """)

        self.settings_button.setStyleSheet("""
                                        font-size: 28px;
                                        color: white;
                                        """)

        self.token_label.setStyleSheet("""
                                        font-size: 28px;
                                        color: white;
                                        """)
        self.dinit_flag = False

    def delayed_init(self):
        """Geometry is not set until the window is updated"""
        if self.dinit_flag:
            return
        self.uif_init_size = self.user_input_frame.geometry().size()

        self.dinit_flag = True

    def eventFilter(self, obj, event):
        """Event filter for the user input box"""
        if obj is self.user_input and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                self.send_button_clicked()
                return True
        return super().eventFilter(obj, event)

    def settings_button_clicked(self):
        """When the button is clicked, open a window with the settings"""
        self.settings_window.show()
        self.settings_window.exec()

    def send_button_clicked(self):
        """When the button is clicked, get the user's message and generate an AI response"""
        user_text = self.user_message()
        # If the user's message is empty, do not generate a response
        if user_text:
            self.start_ai_worker(user_text)

    def user_message(self):
        """Get the user's message from the user_input box"""
        user_text = self.user_input.toPlainText()

        # Append the text to the chatHistory widget
        user_message_html = (
            f'<table width="100%" cellspacing="0" cellpadding="0">'
            f'<tr><td align="right" style="background-color: lightgrey; color: black; padding: 5px;'
            f'margin-bottom: 10px;">{user_text}</td></tr></table>'
        )
        self.chat_history.append(user_message_html)

        # Erase the text from the user_input box
        self.user_input.setText('')

        return user_text

    def start_ai_worker(self, prompt):
        """Start the worker thread to generate the AI response"""
        self.worker = OpenAIWorker(self.openai_reply, method="reply", prompt=prompt)
        self.worker.result_ready.connect(self.display_ai_response)
        self.worker.tokens_updated.connect(self.update_token_count)
        self.worker.start()

    def display_ai_response(self, response):
        """Display the AI response in the chat history"""

        # Format the response for display
        response = self.format_text(response)

        ai_message_html = (
            f'<table width="100%" cellspacing="0" cellpadding="0">'
            f'<tr><td align="left" style="background-color: darkgrey; color: black; padding: 5px; '
            f'margin-bottom: 10px;">{response}</td></tr></table>'
        )
        self.chat_history.append(ai_message_html)

    def update_token_count(self, token_count):
        """Update the token count in the UI"""
        self.token_label.setText(f"Context Tokens: {token_count}")

    def format_text(self, resp):
        """Format the text for display in the chat history"""
        return syntax(resp)

    def input_resizing(self):
        """Resize the user input box"""
        # Delay the initialization until this is updated:
        self.delayed_init()

        text_height = int(self.user_input.document().size().height())
        text_height = int(text_height+50)

        if text_height < self.uif_init_size.height():
            text_height = self.uif_init_size.height()
        if text_height > 500:
            text_height = 500
        self.user_input_frame.resize(self.user_input_frame.width(), text_height)
        # Set the maximum height of the frame
        self.user_input_frame.setMaximumHeight(text_height)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
