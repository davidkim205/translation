from kiwipiepy import Kiwi

kiwi = Kiwi()


def text_tokenize(src):
    token_list = kiwi.tokenize(src, normalize_coda=True)
    results=''
    for token in token_list:
        results += f" {token.form}"
    return results

def tokenize(src):
    token_list = kiwi.tokenize(src, normalize_coda=True)
    results=[]
    for token in token_list:
        results.append(token.form)
    return results

def main():
    while True:
        text = input('>')
        result = text_tokenize(text)
        print(result)

if __name__ == "__main__":
    main()
