import argparse
import json
import os
from tqdm import tqdm
from utils.bleu_score import simple_score


# 결과 파일 경로이름을 생성
def gen_output_filename(filename, model):
    name, extension = os.path.splitext(os.path.basename(filename))
    return f'llm_ko_datasets/{name}_{model}{extension}'


def load_json(filename):
    json_data = []
    with open(filename, 'r', encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != '.jsonl':
            json_data = json.load(f)
        else:
            for line in f:
                json_data.append(json.loads(line))
    return json_data[:2]


# 파일이 존재하면 마지막 줄 뒤에 추가합니다.
def save_json(json_data, filename):
    filename = filename.replace(' ', '_')
    with open(filename, "a", encoding="utf-8") as f:
        if not filename.endswith('.jsonl'):
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            for data in json_data:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")


# 대화 번역 트랜잭션
def cloud_translation(translate_en2ko, api, conversations):
    for conversation in conversations:
        text = conversation['value']
        if ko_text := translate_en2ko(api, text):
            conversation['ko'] = ko_text
        else:
            return False
    return True


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument("--input_file", default="./llm_datasets/conversation_arc.jsonl", type=str, help="input_file")
    parser.add_argument("--model", default="TowerInstruct", type=str, help="model")
    args = parser.parse_args()

    json_data = load_json(args.input_file)

    result = []
    removed_data_count = 0
    if args.model=="gugugo":
        from models.gugugo import translate_en2ko, translate_ko2en
    elif args.model=="madlad400":
        from models.madlad400 import translate_ko2en,translate_en2ko
    elif args.model=="mbart50":
        from models.mbart50 import translate_en2ko, translate_ko2en
    elif args.model=="nllb200":
        from models.nllb200 import translate_ko2en, translate_en2ko
    elif args.model=="TowerInstruct":
        from models.TowerInstruct import translate_ko2en, translate_en2ko
    elif args.model=="cloud_api":
        from cloud_api import translate_en2ko
        # 해당 순서대로 소진 시 다음 API 호출
        api_list = ["deepl", "papago", "azure", "google"]
        # 이미 번역된 데이터는 다시 번역하지 않게 구현
        result_data = load_json(gen_output_filename(args.input_file, args.model))
        json_data = json_data[len(result_data):]

    result = []
    # 번역 API 사용
    if args.model == "cloud_api":
        api_idx = 0
        api = api_list[api_idx]
        for data in tqdm(json_data):
            try:
                while not cloud_translation(translate_en2ko, api, data['conversations']):
                    api_idx += 1
                    api = api_list[api_idx]
                else:
                    data['translation'] = f"{api}_api"
                    result.append(data)
            except IndexError:
                break
    # 로컬 모델 사용
    else:
        for data in tqdm(json_data):
            for conversation in data['conversations']:
                text = conversation['value']
                #print(text)
                ko_text = translate_en2ko(text)
                en_text = translate_ko2en(ko_text)
                #print('ko_text', ko_text)
                conversation['ko'] = ko_text
                conversation['en'] = en_text
            data['translation'] = args.model
            result.append(data)
    # 저장
    if result:
        save_json(result, gen_output_filename(args.input_file, args.model))


if __name__ == "__main__":
    main()
