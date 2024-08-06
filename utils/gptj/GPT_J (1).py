
import logging
import openai

from utils.speech import TTSConVRSelf, STTConVRSelf
import requests

logger = logging.getLogger(__name__)



def create_promt_for_sentence(input_sentence):
    return input_sentence



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
    local_port = 8745

    server = SSHTunnelForwarder(
        (remote_host, remote_port),
        ssh_username='ashoa',
        ssh_password='Var123456',
        remote_bind_address=(local_host, local_port),
        local_bind_address=(local_host, local_port),
    )

    server.start()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    r = requests.get(f'http://{local_host}:{local_port}/predict', headers=headers,params={"input_sentence":input_sentence}).content
    print(r)
    server.stop()


class GPTj():
    def __init__(self, ip="194.153.101.135",port=9845):
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


if __name__ == '__main__':
    gpt = GPTj()
    print(gpt.predict_sentence("Therapist: Come in. Hi, George?,\nPatient: Yeah, hi.\nTherapist: Nice to meet you. I am Christy.\nPatient: Nice to meet you.\nTherapist: Have a seat. I have all the paperwork to fill out and essay .\nPatient: Yes. I did not get all the way through it.\nTherapist: That is okay. Which ones did you have time to get through?\nPatient: This is the pile I finished.\nTherapist: You know, there is so much, so much.\nPatient: And I did not get to the essay ones.\nTherapist:"))