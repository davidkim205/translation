from kiwipiepy import Kiwi
from nltk.tokenize import word_tokenize
import re
kiwi = Kiwi()


def is_korean(text):
    for char in text:
        if "가" <= char <= "힣":
            return True
    return False


def text_tokenize(src):
    token_list = kiwi.tokenize(src, normalize_coda=True)
    results=''
    for token in token_list:
        results += f" {token.form}"
    return results


def tokenize(src):
    src = re.sub("\n+", " ", src)
    if is_korean(src):
        token_list = kiwi.tokenize(src, normalize_coda=True)
        results=[]
        for token in token_list:
            results.append(token.form)
        return results
    else:
        return word_tokenize(src.lower())
    

def main():
    while True:
        text = input('>')
        result = tokenize(text)
        print(result)

if __name__ == "__main__":
    main()
