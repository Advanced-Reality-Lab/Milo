import requests


if __name__ == '__main__':
    URL = "https://api.eleuther.ai/completion"
    PARAMS = {"context": "this is a test", "top_p": 0.9, "temp": 0.8, 'response_length': 128, 'remove_input': "true"}
    HEADERS = {'accept': "application/json","Content-Type": "application/json"}
    r = requests.post(url = URL,headers=HEADERS , json = PARAMS)
    print(r.content.decode('utf-8'))
    pass