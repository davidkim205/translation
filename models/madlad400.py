from transformers import T5ForConditionalGeneration, T5Tokenizer
from utils.simple_bleu import simple_score
import torch

model_name = 'jbochi/madlad400-10b-mt'
model = T5ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="auto")
tokenizer = T5Tokenizer.from_pretrained(model_name)


def translate_ko2en(text):
    text = f"<2en> {text}"
    input_ids = tokenizer(text, return_tensors="pt").input_ids.to(model.device)
    outputs = model.generate(input_ids=input_ids, max_new_tokens=2048)

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


def translate_en2ko(text):
    text = f"<2ko> {text}"
    input_ids = tokenizer(text, return_tensors="pt").input_ids.to(model.device)
    outputs = model.generate(input_ids=input_ids, max_new_tokens=2048)

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


def main():
    while True:
        text = input('>')
        en_text = translate_ko2en(text)
        ko_text = translate_en2ko(en_text)
        print('en_text', en_text)
        print('ko_text', ko_text)
        print('score', simple_score(text, ko_text))


if __name__ == "__main__":
    main()
