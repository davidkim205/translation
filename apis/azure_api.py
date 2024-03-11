from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError
import logging
key = "70aaaa169c234bf4b5f756e65942ef0f"
endpoint = "https://api.cognitive.microsofttranslator.com/"
region = "koreacentral"

credential = TranslatorCredential(key, region)
text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)


def translate_en2ko(text):
    return False
    source_language = "en"
    target_languages = ["ko"]
    input_text_elements = [ InputTextItem(text = text) ]
    try:
        response = text_translator.translate(content = input_text_elements, to = target_languages, from_parameter = source_language)
        translation = response[0]
        translated_text = translation.translations[0]
        return translated_text.text
    except Exception as e:
        print(e.args[0])
        return False
    

def main():
    while True:
        text = input('>')
        ko_text = translate_en2ko(text)
        print('ko_text', ko_text)


if __name__ == "__main__":
    main()