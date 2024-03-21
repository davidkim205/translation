from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
from utils.tokenizer import tokenize


def simple_score(text1, text2, lang):
    if lang == "ko":
        reference = tokenize(text1)
        candidate = tokenize(text2)
    elif lang == "en":
        reference = word_tokenize(text1.lower())
        candidate = word_tokenize(text2.lower())
    # base = sentence_bleu([reference], reference)
    score = sentence_bleu([reference], candidate)
    return score


# if __name__ == "__main__":
#     while True:
#         ref = input("ref: ")
#         cand = input("cand: ")
#         simple_score(ref, cand)
