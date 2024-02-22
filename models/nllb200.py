from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from utils.bleu_score import simple_score
import torch

model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-1.3B", torch_dtype=torch.bfloat16, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-1.3B")


def translate_ko2en(text):
    batched_input = [text]
    inputs = tokenizer(batched_input, return_tensors="pt", padding=True)

    translated_tokens = model.generate(
        **inputs.to(model.device), forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"]
    )
    result = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    return result


def translate_en2ko(text):
    batched_input = [text]
    inputs = tokenizer(batched_input, return_tensors="pt", padding=True)

    translated_tokens = model.generate(
        **inputs.to(model.device), forced_bos_token_id=tokenizer.lang_code_to_id["kor_Hang"], max_new_tokens=2048)

    result = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    return result


def main():
    while True:
        text = input('>')
        en_text = translate_ko2en(text)
        ko_text = translate_en2ko(en_text)
        print('en_text', en_text)
        print('ko_text', ko_text)
        print('score', simple_score(text, ko_text))
    """
    >>? 3천만 개가 넘는 파일과 250억 개의 토큰이 있습니다. Phi1.5의 데이터 세트 구성에 접근하지만 오픈 소스 모델인 Mixtral 8x7B를 사용하고 Apache2.0 라이선스에 따라 라이선스가 부여됩니다. 
en_text There are over 30 million files and 250 billion tokens. Phi1.5's data set configuration is accessible but uses the open source model Mixtral 8x7B and is licensed under the Apache 2.0 license.
ko_text 300만 개 이상의 파일과 25억 개의 토큰이 있습니다. Phi1.5의 데이터 세트 구성은 액세스 가능하지만 오픈 소스 모델 Mixtral 8x7B를 사용하고 Apache 2.0 라이선스에 따라 라이선스됩니다.
score 0.3090015909429233
    """


if __name__ == "__main__":
    main()
