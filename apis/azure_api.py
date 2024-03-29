from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError


def load_model(
    api_key,
    region="koreacentral",
    endpoint="https://api.cognitive.microsofttranslator.com/",
):
    credential = TranslatorCredential(api_key, region)
    global text_translator
    text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)


def translate_en2ko(text):
    source_language = "en"
    target_languages = ["ko"]
    input_text_elements = [InputTextItem(text=text)]
    try:
        response = text_translator.translate(
            content=input_text_elements,
            to=target_languages,
            from_parameter=source_language,
        )
        translation = response[0]
        translated_text = translation.translations[0]
        return translated_text.text
    except HttpResponseError as e:
        print(e)
        return False


def translate_en2ko(text):
    source_language = "ko"
    target_languages = ["en"]
    input_text_elements = [InputTextItem(text=text)]
    try:
        response = text_translator.translate(
            content=input_text_elements,
            to=target_languages,
            from_parameter=source_language,
        )
        translation = response[0]
        translated_text = translation.translations[0]
        return translated_text.text
    except HttpResponseError as e:
        print(e)
        return False


def main():
    while True:
        text = input(">")
        ko_text = translate_en2ko(text)
        print("ko_text", ko_text)


if __name__ == "__main__":
    main()
