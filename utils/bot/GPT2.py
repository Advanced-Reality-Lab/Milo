from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logger = logging.getLogger(__name__)


class GPT2():

    def __init__(self, name="microsoft/DialoGPT-medium"):
        self.name = name
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForCausalLM.from_pretrained(name)
        assert self.tokenizer is not None and self.model is not None, \
            "error getting tokenizer or model from huggingface"


    def predict_sentence(self, input_sentence, file_name):

        new_user_input_ids = self.tokenizer.encode(input_sentence + self.tokenizer.eos_token, return_tensors='pt')
        chat_history_ids = self.model.generate(new_user_input_ids, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
        sentence = self.tokenizer.decode(chat_history_ids[:, new_user_input_ids.shape[-1]:][0], skip_special_tokens=True)

        outF = open(file_name + ".txt", "w")
        outF.write(sentence)
        outF.close()
        return sentence, file_name + ".txt"
