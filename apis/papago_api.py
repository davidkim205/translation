import urllib.request
import json

client_id = "u42tmgtxjq" # 개발자센터에서 발급받은 Client ID 값
client_secret = "QzpXdcLF0ixKrI0LKiDIrSBheg6ATkpuvkOlXDuV" # 개발자센터에서 발급받은 Client Secret 값
url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
request = urllib.request.Request(url)
request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
request.add_header("X-NCP-APIGW-API-KEY",client_secret)


def translate_en2ko(text):
    encText = urllib.parse.quote(text)
    data = "source=en&target=ko&text=" + encText
    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        result = json.loads(response.read().decode('utf-8'))
        return result['message']['result']['translatedText']
    except:
        return False
    

def main():
    while True:
        text = input('>')
        ko_text = translate_en2ko(text)
        print('ko_text', ko_text)


if __name__ == "__main__":
    main()