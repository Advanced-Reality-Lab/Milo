import os

import openai


class GPT3():
    def __init__(self, name="davinci", prefix_prompt=""):
        openai.api_key = os.getenv("OPENAI_KEY")
        self.prefix_prompt = prefix_prompt
        self.name = name
        # self.prompt_func =
        self.previous_sentences = []
        # self.previous_output_sentences = []

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
