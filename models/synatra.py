from utils.simple_bleu import simple_score
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

device = "cuda" # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained("maywell/Synatra-7B-v0.3-Translation", torch_dtype=torch.bfloat16, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("maywell/Synatra-7B-v0.3-Translation")


def translate_ko2en(text):
    messages = [
        {"role": "system", "content": "주어진 문장을 영어로 번역해라."},
        {"role": "user", "content": text},
    ]

    encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")

    model_inputs = encodeds.to(device)
    model.to(device)

    generated_ids = model.generate(model_inputs, max_new_tokens=2048, do_sample=True)
    output = tokenizer.batch_decode(generated_ids)[0]
    if output.endswith("<|im_end|>"):
        output = output[:-len("<|im_end|>")]
    output =  output.split('<|im_end|>')[-1]
    return output



def translate_en2ko(text):
    messages = [
        {"role": "system", "content": "주어진 문장을 한국어로 번역해라."},
        {"role": "user", "content": text},
    ]

    encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")

    model_inputs = encodeds.to(device)
    model.to(device)

    generated_ids = model.generate(model_inputs, max_new_tokens=2048, do_sample=True)
    output = tokenizer.batch_decode(generated_ids)[0]
    if output.endswith("<|im_end|>"):
        output = output[:-len("<|im_end|>")]
    output =  output.split('<|im_end|>')[-1]
    return output

def main():
    while True:
        text = input('>')
        en_text = translate_ko2en(text)
        ko_text = translate_en2ko(en_text)
        print('------en_text--------')
        print(en_text)
        print('------ko_text--------')
        print(ko_text)

        print('score', simple_score(text, ko_text))


if __name__ == "__main__":
    main()
