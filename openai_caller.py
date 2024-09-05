import os
from openai import OpenAI
import re

apikey = os.getenv("desktop_gpt_api_key")


class OpenAIReply:
    def __init__(self):
        self.summary = ""
        self.context = ""
        self.context_tokens = 0
        self.client = OpenAI()
        self.client.api_key = apikey

    def generate_openai_reply(self, prompt):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant."
                 f"Here is a summary of the conversation so far: {self.context}"},
                {"role": "user", "content": prompt},
            ]
        )

        resp = completion.choices[0].message.content

        self.context += "User Prompt: " + prompt + "\nAssistant Response: " + resp + "\n\n"
        self.context_tokens = int(len(self.context)*1.333) # estimated
        return resp

    def generate_openai_summary(self):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a summarizer."
                 "Summarize any text you are given into a short concise response. Summarize all the messages into a single response."},
                {"role": "user", "content": self.context},
            ]
        )

        resp = completion.choices[0].message.content

        self.summary = resp

if __name__ == "__main__":
    openai_reply = OpenAIReply()
    prompt = "give random python code, no explanation (shortish, with some comments)"
    x = openai_reply.generate_openai_reply(prompt)
    # openai_reply.generate_openai_summary()

    print(openai_reply.process_code_snippet(x))
