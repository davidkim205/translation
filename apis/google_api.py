from google.cloud import translate_v2 as translate
from html import unescape

client = translate.Client(client_options={"api_key": "AIzaSyA4dTP95X5hhPZ-UptV_50bYrbldAVwDUw", "quota_project_id": "	influential-kit-414205"})


def translate_en2ko(text):
    # return False
    try:
        result = client.translate(text, source_language="en", target_language="ko")
        return result["translatedText"]
    except:
        return False
    

def main():
    while True:
        text = input('>')
        ko_text = translate_en2ko(text)
        print('ko_text', ko_text)


if __name__ == "__main__":
    main()