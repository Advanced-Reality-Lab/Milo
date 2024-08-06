import tkinter as tk
from collections import defaultdict

from utils.bot.GPT3 import GPT3


class InputSentenceUpdater():
    def __init__(self):
        self.observers = defaultdict(list)

    def register(self, event, observer):
        self.observers[event].append(observer)

    def unregister(self, event, observer):
        self.observers[event].remove(observer)

    def update_notify(self, new_text):
        for observer in self.observers['update']:
            observer(new_text)


def input_sentence_updater():
    return InputSentenceUpdater()


def tts_google(text):
    return None

def update_func(prev_text, new_text):
    return f"{prev_text}\n{new_text}"

class TextGenerator:
    def __init__(self, personality_prompt=None):
        self.gpt = GPT3(prefix_prompt=personality_prompt,prompt_func=update_func)
        pass

    def generate_text(self,text):
        return self.gpt.predict_sentence(text, user_name="davinci")

text_generator = TextGenerator(open("prompt.txt",'r').read())
def generate_text(text):
    return text_generator.generate_text(text)