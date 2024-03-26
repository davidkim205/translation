from nltk.translate.bleu_score import sentence_bleu,SmoothingFunction
from utils.tokenizer import tokenize


def simple_score(text1, text2):
    reference = tokenize(text1)
    candidate = tokenize(text2)
    # base = sentence_bleu([reference], reference)
    score = sentence_bleu([reference], candidate, smoothing_function=SmoothingFunction().method2)
    return score


if __name__ == "__main__":
    while True:
        ref = input("ref: ")
        cand = input("cand: ")
        print('score',simple_score(ref, cand))
