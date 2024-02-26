import deepl

auth_key = "c4398d0c-aac0-9178-3e6c-83f70d96cfc5:fx"  # Replace with your key
translator = deepl.Translator(auth_key)


def translate_en2ko(text):
    try:
        result = translator.translate_text(text, target_lang="KO")
        return result.text
    except:
        return False
    

def main():
    while True:
        text = input('>')
        ko_text = translate_en2ko(text)
        print('ko_text', ko_text)


if __name__ == "__main__":
    main()
    