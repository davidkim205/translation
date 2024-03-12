from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
import re


def simple_score(text1, text2):
    text1 = re.sub(r"\n+", " ", text1)
    text2 = re.sub(r"\n+", " ", text2)
    reference = list(map(lambda x: x.lower(), word_tokenize(text1)))
    # print(reference)
    candidate = list(map(lambda x: x.lower(), word_tokenize(text2)))
    # print(candidate)
    base = sentence_bleu([reference], reference)
    # print(base)
    score = sentence_bleu([reference], candidate)
    # print(score)
    return score


def main():
    while True:
        ref = input(">")
        cand = input(">")
        score = simple_score(ref, cand)
        print(score)


if __name__ == "__main__":
    main()
