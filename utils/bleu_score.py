from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
from utils.tokenizer import tokenize
def simple_score(text1, text2):
    reference = tokenize(text1)
    candidate = tokenize(text2)
    base = sentence_bleu([reference], reference)
    score = sentence_bleu([reference], candidate)
    return score
