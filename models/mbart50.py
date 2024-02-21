from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

from utils.bleu_score import simple_score

model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt", device_map="auto")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")


def translate_ko2en(text):
    tokenizer.src_lang = "ko_KR"
    input_ids = tokenizer(text, return_tensors="pt").input_ids.to(model.device)
    outputs = model.generate(input_ids=input_ids, forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"])

    outputs = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return outputs


def translate_en2ko(text):
    tokenizer.src_lang = "en_XX"
    input_ids = tokenizer(text, return_tensors="pt").input_ids.to(model.device)
    outputs = model.generate(input_ids=input_ids, forced_bos_token_id=tokenizer.lang_code_to_id["ko_KR"], max_new_tokens=2048)

    outputs = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return outputs


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
en_text It has over 30 million files and 2.5 billion tokens, accesses the data set configuration of Phi1.5, but uses an open-source model, Mixtral 8x7B, and is licensed under the Apache 2.0 license.
ko_text 30만개의 파일과 2.5억개의 토큰을 가지고 있고, Phi1.5의 데이터 세트 configuration에 접근하지만, 오픈소스 모델인 Mixtral 8x7B를 사용하고, Apache 2.0 라이센스 아래 licenc를 가지고 있습니다.
score 0.14724623770949022
    """

if __name__ == "__main__":
    main()
