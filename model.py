from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList
import torch
from utils.simple_bleu import simple_score
import torch

templates = {
    'davidkim205/iris-7b': {
        'stop_words': ['</s>'],
        'ko2en': '[INST] 다음 문장을 영어로 번역하세요.{0} [/INST]',
        'en2ko': '[INST] 다음 문장을 한글로 번역하세요.{0} [/INST]',
        'trim_keywords': ['</s>'],
    },
    'squarelike/Gugugo-koen-7B-V1.1': {
        'stop_words': ['</s>', '</끝>'],
        'ko2en': '### 한국어: {0}</끝>\n### 영어:',
        'en2ko': "### 영어: {0}</끝>\n### 한국어:",
        'trim_keywords': ['</s>', '</끝>'],
    },
    'maywell/Synatra-7B-v0.3-Translation': {
        'stop_words': ['</s>', '</끝>', '<|im_end|>'],
        'ko2en': '<|im_start|>system\n주어진 문장을 영어로 번역해라.<|im_end|>\n<|im_start|>user\n{0}<|im_end|>\n<|im_start|>assistant',
        'en2ko': '<|im_start|>system\n주어진 문장을 한국어로 번역해라.<|im_end|>\n<|im_start|>user\n{0}<|im_end|>\n<|im_start|>assistant',
        'trim_keywords': ['<|im_end|>'],
    },
    'Unbabel/TowerInstruct-7B-v0.1': {
        'stop_words': ['</s>', '</끝>', '<|im_end|>'],
        'ko2en': '<|im_start|>user\nTranslate the following text from English into Korean.\nKorean: {0}\nEnglish:<|im_end|>\n<|im_start|>assistant',
        'en2ko': '<|im_start|>user\nTranslate the following text from Korean into English.\nEnglish: {0}\nKorean:<|im_end|>\n<|im_start|>assistant',
        'trim_keywords': ['<|im_end|>'],
    },
}

model_info = {'model': None, 'tokenizer': None, 'stopping_criteria': None}


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


def trim_sentence(sentence, keywords):
    for keyword in keywords:
        if keyword in sentence:
            # 키워드를 찾은 경우, 해당 인덱스를 기준으로 문장을 자름
            index = sentence.find(keyword)
            trimmed_sentence = sentence[:index]
            sentence = trimmed_sentence.strip()  # 좌우 공백 제거 후 반환
    return sentence


def load_model(path, template_name=None):
    global model_info
    print('load_model', path)
    if template_name == None:
        template_name = path
    if templates.get(template_name) == None:
        template_name = 'davidkim205/iris-7b'
    model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16, device_map='auto')
    tokenizer = AutoTokenizer.from_pretrained(path)

    model_info['model'] = model
    model_info['tokenizer'] = tokenizer
    model_info['template'] = templates[template_name]

    stop_words = templates[template_name]['stop_words']
    stopping_criteria = StoppingCriteriaList([LocalStoppingCriteria(tokenizer=tokenizer, stop_words=stop_words)])
    model_info['stopping_criteria'] = stopping_criteria


def generate(prompt):
    global model_info
    if model_info['model'] == None:
        print('model is null, load the model first.')
        return ''
    model = model_info['model']
    tokenizer = model_info['tokenizer']
    stopping_criteria = model_info['stopping_criteria']
    encoding = tokenizer(
        prompt,
        return_tensors='pt',
        return_token_type_ids=False
    ).to("cuda")
    gen_tokens = model.generate(
        **encoding,
        max_new_tokens=2048,
        temperature=1.0,
        num_beams=5,
        stopping_criteria=stopping_criteria
    )
    prompt_end_size = encoding.input_ids.shape[1]
    result = tokenizer.decode(gen_tokens[0, prompt_end_size:])
    result = trim_sentence(result, model_info['template']['trim_keywords'])
    return result


def translate_ko2en(text):
    global model_info
    prompt = model_info['template']['ko2en'].format(text)
    return generate(prompt)


def translate_en2ko(text):
    global model_info
    prompt = model_info['template']['en2ko'].format(text)
    return generate(prompt)


def main():
    load_model("davidkim205/iris-7b")
    # load_model("squarelike/Gugugo-koen-7B-V1.1")
    # load_model("maywell/Synatra-7B-v0.3-Translation")
    # load_model("Unbabel/TowerInstruct-7B-v0.1")
    while True:
        text = input('>')
        en_text = translate_ko2en(text)
        ko_text = translate_en2ko(en_text)
        print('------------------')
        print('en_text', en_text)
        print('ko_text', ko_text)
        print('score', simple_score(text, ko_text))


if __name__ == "__main__":
    main()
