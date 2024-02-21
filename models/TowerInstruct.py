import torch
from transformers import pipeline
from utils.bleu_score import simple_score

pipe = pipeline("text-generation", model="Unbabel/TowerInstruct-v0.1", torch_dtype=torch.bfloat16, device_map="auto")

def translate_ko2en(text):
    messages = [
        {"role": "user", "content": f"Translate the following text from Korean into English.\n: Korean:{text}\nEnglish:"},
    ]
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=2048, do_sample=False)
    result = outputs[0]["generated_text"]
    result = result.split('<|im_start|>assistant')[1]
    result = result.replace('\n:', '')
    result = result.lstrip('\n')
    result = result.lstrip(':')
    return result



def translate_en2ko(text):
    messages = [
        {"role": "user",
         "content": f"Translate the following text from English into Korean.\nEnglish: {text} \nKorean:"},
    ]
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=2048, do_sample=False)
    result = outputs[0]["generated_text"]
    result = result.split('<|im_start|>assistant')[1]
    result = result.replace('\n:', '')
    result = result.lstrip('\n')
    result = result.lstrip(':')
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
