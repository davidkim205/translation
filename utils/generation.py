import torch
import argparse
import os
import random
import os
import json
import random, os
import numpy as np
import torch

from transformers import StoppingCriteria, StoppingCriteriaList
from transformers import TextStreamer, GenerationConfig


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

    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True


def generation(model, tokenizer, x, max_new_tokens=1024):
    
    stopping_criteria = StoppingCriteriaList(
    [LocalStoppingCriteria(tokenizer=tokenizer, stop_words=[tokenizer.eos_token])])
    streamer = TextStreamer(tokenizer)


    generation_config = GenerationConfig(
        temperature=1.0,
        top_p=0.8,
        top_k=100,
        max_new_tokens=max_new_tokens,
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
    return response
