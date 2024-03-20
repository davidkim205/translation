import torch
import argparse
import os
import random
import os
import json

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from transformers import StoppingCriteria, StoppingCriteriaList
from transformers import TextStreamer, GenerationConfig


args_model_name="davidkim205/iris-qwen-14b-v0.1"
args_max_new_tokens=1024

class LocalStoppingCriteria(StoppingCriteria):

    def __init__(self, tokenizer, stop_words=[]):
        super().__init__()

        stops = [tokenizer(stop_word, return_tensors='pt', add_special_tokens=False)['input_ids'].squeeze() for
                 stop_word in stop_words]
        print('stop_words', stop_words)
        print('stop_words_ids', stops)
        self.stop_words = stop_words
        self.stops = [stop.cuda() for stop in stops]
        self.tokenizer = tokenizer

    def _compare_token(self, input_ids):
        for stop in self.stops:
            if len(stop.size()) != 1:
                continue
            stop_len = len(stop)
            if torch.all((stop == input_ids[0][-stop_len:])).item():
                return True

        return False

    def _compare_decode(self, input_ids):
        input_str = self.tokenizer.decode(input_ids[0])
        for stop_word in self.stop_words:
            if input_str.endswith(stop_word):
                return True
        return False

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        return self._compare_decode(input_ids)


def seed_everything(seed: int):
    import random, os
    import numpy as np
    import torch

    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

model = AutoModelForCausalLM.from_pretrained(args_model_name, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(args_model_name, use_fast=True)
model.eval()

stopping_criteria = StoppingCriteriaList(
    [LocalStoppingCriteria(tokenizer=tokenizer, stop_words=[tokenizer.eos_token])])
streamer = TextStreamer(tokenizer)

def generation(x):
    generation_config = GenerationConfig(
        temperature=1.0,
        top_p=0.8,
        top_k=100,
        max_new_tokens=args_max_new_tokens,
        early_stopping=True,
        do_sample=True,
    )
    gened = model.generate(
        **tokenizer(
            x,
            return_tensors='pt',
            return_token_type_ids=False
        ).to('cuda'),
        generation_config=generation_config,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        stopping_criteria=stopping_criteria,
        streamer=streamer,
    )
    response = tokenizer.decode(gened[0])
    only_gen_text = response.split(x)
    if len(only_gen_text) == 2:
        response = only_gen_text[-1]
    response = response.replace(tokenizer.eos_token, '')
    tmp_respose = response.split('<|im_start|> assistant')
    if len(tmp_respose) > 1:
        response = tmp_respose[1]
    return response

def translate_ko2en(text):
    query = f"<|im_start|>user\n다음 문장을 영어로 번역하세요.\n{text}<|im_end|>\n<|im_start|>assistant\n"
    return generation(query)


def translate_en2ko(text):
    query = f"<|im_start|>user\n다음 문장을 한글로 번역하세요.\n{text}<|im_end|>\n<|im_start|>assistant\n"
    return generation(query)

def main():
    while True:
        text = input('>')
        en_text = translate_ko2en(text)
        ko_text = translate_en2ko(en_text)
        print('------input----------')
        print(text)
        print('------en_text--------')
        print(en_text)
        print('------ko_text--------')
        print(ko_text)



if __name__ == '__main__':
    main()
