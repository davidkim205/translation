from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize

def simple_score(text1, text2):
    reference = word_tokenize(text1)
    candidate = word_tokenize(text2)
    base = sentence_bleu([reference], reference)
    score = sentence_bleu([reference], candidate)
    return score
