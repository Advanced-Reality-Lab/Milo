import logging
import os

import openai
# from utils.speech import TTSConVRSelf, STTConVRSelf
from utils.bot.content_filter import filter_output

logger = logging.getLogger(__name__)


def create_prompt_for_bartender_a(user_last_input, prev_in=["hi, I really need a drink; I had a terrible day."],
                                  prev_out=["Hi what would you like to drink?"]):
    sentence_bartender_ = ""
    for i in range(len(prev_in)):
        sentence_bartender_ += f"Customer: {prev_in[i]}\nBartender:{prev_out[i]}\n"
    sentence_bartender_ += f"Customer:{user_last_input}\nBartender:"
    return sentence_bartender_


class GPT3():
    def __init__(self, name="davinci", prompt_func=create_prompt_for_bartender_a, prefix_prompt=""):
        openai.api_key = os.getenv("OPENAI_KEY")
        self.prefix_prompt = prefix_prompt
        self.name = name
        self.prompt_func = prompt_func
        self.previous_input_sentences = []
        self.previous_output_sentences = []

    def predict_sentence(self, user_last_input, file_name=None, user_name=None):
        print(user_last_input)
        if user_name is not None:
            # self.name = user_name
            prompt = self.prompt_func(user_last_input,user_name=user_name,prev_in=self.previous_input_sentences)
        else:
            prompt = self.prefix_prompt + self.prompt_func(user_last_input, prev_in=self.previous_input_sentences,
                                                       prev_out=self.previous_output_sentences)
        response = openai.Completion.create(engine=self.name, prompt=prompt, max_tokens=50,
                                            stop=['\n', '.', '!', '?'])
        print("prompt: ", prompt)
        print(f"chat: file name -- {file_name}")
        should_filter = filter_output(response["choices"][0]["text"])
        if should_filter == "2":
            return "unsafe try to generate again", ""
        if file_name is not None:
            outF = open(file_name + ".txt", "w")
            # response = ''
            outF.write(response.choices[0].text)
            outF.close()
        self.previous_input_sentences.append(user_last_input)
        self.previous_output_sentences.append(response.choices[0].text)
        return response.choices[0].text, file_name + ".txt" if file_name is not None else ""


if __name__ == '__main__':
    class Object(object):
        pass


    openai.debug = True
    gpt = GPT3(prompt_func=create_prompt_for_bartender_a)
    input_sentence = "hi"
    res = gpt.predict_sentence(input_sentence)
    print(res)
