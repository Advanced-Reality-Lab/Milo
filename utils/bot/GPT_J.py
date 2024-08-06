
import logging
import openai

from utils.speech import TTSConVRSelf, STTConVRSelf
import requests

logger = logging.getLogger(__name__)



def create_promt_for_sentence(input_sentence):
    return f'The following is a conversation with an AI therapist. The therapist is helpful, creative, clever, and very friendly.\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: {input_sentence}.\nAI:'
    # return f"Below is a conversation I had with a nice bartentder\nme:{input_sentence}\nbartender:"
    # sentence_bartender_ = "The following is a conversation between a female bartender and a customer. The bartender encourages the customer to talk about their life problems and provides supportive feedback.\n\nCustomer: hi, I really need a drink; I had a terrible day. \nBartender:Hi what would you like to drink?\nCustomer:{input_sentence}\nBartender:"
    # return sentence_bartender_


def send_request(url,input_sentence):
    r = requests.get(url=url, params={"input_sentence":input_sentence})
    data = r.json()
    return data

def send_request_ssh(url,input_sentence):
    from sshtunnel import SSHTunnelForwarder
    import requests

    remote_user = 'ubuntu'
    remote_host = '194.153.101.135'
    remote_port = 22
    local_host = '127.0.0.1'
    local_port = 8543

    server = SSHTunnelForwarder(
        (remote_host, remote_port),
        ssh_username='ashoa',
        ssh_password='Var123456',
        remote_bind_address=(local_host, local_port),
        local_bind_address=(local_host, local_port),
    )

    server.start()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    r = requests.get('http://127.0.0.1:8543/predict', headers=headers,params={"input_sentence":input_sentence}).content
    print(r)
    server.stop()


class GPTj():
    def __init__(self, ip="194.153.101.135",port=8745):
        self.ip = ip
        self.port = port
        self.url = "http://{}:{}/predict"

    def predict_sentence(self, input_sentence, file_name=None):
        response = send_request_ssh(self.url.format(self.ip,self.port),create_promt_for_sentence(input_sentence))

        if file_name is not None:
            outF = open(file_name + ".txt", "w")
            outF.write(response.choices[0].text)
            outF.close()
        return response, file_name + ".txt" if file_name is not None else ""
