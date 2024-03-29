import deepl


def load_model(api_key):
    global translator
    translator = deepl.Translator(api_key)


def translate_en2ko(text):
    try:
        result = translator.translate_text(text, target_lang="KO")
        return result.text
    except Exception as e:
        print(e)
        return False


def translate_ko2en(text):
    try:
        result = translator.translate_text(text, target_lang="EN-US")
        return result.text
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
