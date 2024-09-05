from PyQt5 import QtWidgets, uic, QtCore
from openai_caller import OpenAIReply
from PyQt5.QtWidgets import QPushButton


class OpenAIWorker(QtCore.QThread):
    result_ready = QtCore.pyqtSignal(str)
    tokens_updated = QtCore.pyqtSignal(int)

    def __init__(self, openai_reply, method, prompt=None):
        super().__init__()
        self.openai_reply = openai_reply
        self.method = method
        self.prompt = prompt

    def run(self):
        if self.method == "summary":
            # Generate the summary
            self.openai_reply.generate_openai_summary()
            # Emit the result
            self.result_ready.emit(self.openai_reply.summary)
        elif self.method == "reply":
            # Generate the AI reply
            response = self.openai_reply.generate_openai_reply(self.prompt)
            # Emit the result
            self.result_ready.emit(response)
        # Emit the updated token count
        self.tokens_updated.emit(self.openai_reply.context_tokens)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)

        self.setWindowTitle("Desktop GPT")

        self.summary_window = QtWidgets.QMessageBox()
        self.summary_window.setWindowTitle("Summary")
        self.summary_window.setText("Creating a summary of the conversation so far...")

        self.openai_reply = OpenAIReply()

        self.chat_history = self.findChild(QtWidgets.QTextEdit, 'chatHistory')
        self.user_input = self.findChild(QtWidgets.QTextEdit, 'userText')

        self.send_button = self.findChild(QPushButton, 'sendButton')
        self.send_button.clicked.connect(self.send_button_clicked)

        self.summary_button = self.findChild(QPushButton, 'summaryButton')
        self.summary_button.clicked.connect(self.summary_button_clicked)

        self.chat_history.setStyleSheet("background-color: lightgrey;")

    def summary_button_clicked(self):
        """When the button is clicked, open a window with the AI summary"""
        self.summary_window.show()

        # Start the worker thread for generating the summary
        self.worker = OpenAIWorker(self.openai_reply, method="summary")
        self.worker.result_ready.connect(self.display_summary)
        self.worker.start()

    def display_summary(self, summary):
        """Update the message box with the generated summary"""
        self.summary_window.setText(summary)
        self.summary_window.exec()

    def send_button_clicked(self):
        """When the button is clicked, get the user's message and generate an AI response"""
        user_text = self.user_message()
        self.start_ai_worker(user_text)

    def user_message(self):
        """Get the user's message from the user_input box"""
        user_text = self.user_input.toPlainText()

        # Append the text to the chatHistory widget
        user_message_html = (
            f'<table width="100%" cellspacing="0" cellpadding="0">'
            f'<tr><td align="right" style="background-color: lightgrey; color: black; padding: 5px; '
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
        ai_message_html = (
            f'<table width="100%" cellspacing="0" cellpadding="0">'
            f'<tr><td align="left" style="background-color: darkgrey; color: black; padding: 5px; '
            f'margin-bottom: 10px;">{response}</td></tr></table>'
        )
        self.chat_history.append(ai_message_html)

    def update_token_count(self, token_count):
        """Update the token count in the UI"""
        self.findChild(QtWidgets.QLabel, 'tokenCount').setText(f"Context Tokens: {token_count}")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
