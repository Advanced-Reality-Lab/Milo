## ///////////////////
## this is a script to run a custom LLM on a remote server
## model can be fetched from huggingface or loaded from disk using the huggingface api
## ///////////

from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteriaList
import logging
from flask import Flask, request

import torch
from transformers import StoppingCriteria


class SequenceStop(StoppingCriteria):
    def _init_(self, tokens, batch_size: int):
        super()._init_()

        self.tokens = tokens[:]
        self.batch_size = batch_size
        self.seq = torch.LongTensor([tokens[:] for _ in range(batch_size)])
        self.seq_len = len(tokens)
        self.found = [False] * batch_size

    def reset(self):
        self.found = [False] * len(self.found)

    def _call_(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if input_ids.device.type != self.seq.device.type:
            device = f'cuda:{input_ids.device.index}' if input_ids.device.type == 'cuda' else 'cpu'
            self.seq = self.seq.to(device)

        for i in range(input_ids.shape[0]):
            if self.found[i]:
                continue
            self.found[i] = True if ( False not in torch.eq(input_ids[i, -self.seq_len:], self.seq)) else False

        return all(self.found)

    def clone(self):
        return SequenceStop(tokens=self.tokens[:], batch_size=self.batch_size)
logger = logging.getLogger(__name__)
api = Flask(__name__)


class GPTj():
    def __init__(self, name="EleutherAI/gpt-j-6B"):
        self.name = name
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForCausalLM.from_pretrained(name)
        assert self.tokenizer is not None and self.model is not None, \
            "error loading tokenizer or model from huggingface"
        self.model.bfloat16()
        self.model.eval()
        self.model.parallelize(device_map={0:[i for i in range(self.model.n_layer) ]})
        _stopping_list = StoppingCriteriaList()
        _stopping_list.append(SequenceStop(tokens=[12130, 1153, 25], batch_size=1))
        _stopping_list.append(SequenceStop(tokens=[35048, 41690, 25], batch_size=1))
        self.stopping_criteria_list = _stopping_list


    def predict_sentence(self, input_sentence=''):
        input_ids = self.tokenizer(input_sentence, return_tensors="pt").input_ids
        
        gen_tokens = self.model.generate(
            input_ids,
            do_sample=True,
            temperature=0.9,
            max_length=100,
            stopping_criteria=self.stopping_criteria_list
        
        )
        sentence = self.tokenizer.batch_decode(gen_tokens)[0]
        return sentence



@api.route("/predict",methods=["GET", "POST"])
def predict():
    sentence_ = request.args.get('input_sentence')
    print(sentence_)
    return model.predict_sentence(sentence_)

if __name__ == '__main__':
    global model
    model = GPTj()
    print("model loaded")
    api.run(debug=False,host='0.0.0.0',port=8745)
