import json
from utils.bot.GPT3 import GPT3


def validate_config(config):
    pass

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def read_config_file(conf_json='./config/conf.json'):
    with open(conf_json, 'r') as config_file:
        config = json.load(config_file)
    return AttrDict(config)

# old use of openai sdk - ignore
GPT3_model_names = ["davinci","ada","Babbage", "Curie" ]

def load_model(name):
     # if name in GPT3_model_names:
     # model = GPT3.GPT3()
     model = GPT3()
     # else:
         # model = GPT2.GPT2(name=name)

     return model