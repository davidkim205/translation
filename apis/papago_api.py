import urllib.request
import json


def load_model(
    client_id,
    client_secret,
    url="https://naveropenapi.apigw.ntruss.com/nmt/v1/translation",
):
    global request
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request.add_header("X-NCP-APIGW-API-KEY", client_secret)


def translate_en2ko(text):
    encText = urllib.parse.quote(text)
    data = "source=en&target=ko&text=" + encText
    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        result = json.loads(response.read().decode("utf-8"))
        return result["message"]["result"]["translatedText"]
    except Exception as e:
        print(e)
        return False


def translate_ko2en(text):
    encText = urllib.parse.quote(text)
    data = "source=ko&target=en&text=" + encText
    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        result = json.loads(response.read().decode("utf-8"))
        return result["message"]["result"]["translatedText"]
    except Exception as e:
        print(e)
        return False


def main():
    while True:
        text = input(">")
        ko_text = translate_en2ko(text)
        print("ko_text", ko_text)


if __name__ == "__main__":
    main()
