import argparse
import json
import os
from tqdm import tqdm
from utils.bleu_score import simple_score

def load_json(filename):
    json_data = []
    with open(filename, 'r', encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != '.jsonl':
            json_data = json.load(f)
        else:
            for line in f:
                json_data.append(json.loads(line))
    return json_data


def save_json(json_data, filename):
    filename = filename.replace(' ', '_')
    with open(filename, "w", encoding="utf-8") as f:
        if not filename.endswith('.jsonl'):
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            for data in json_data:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")

def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument("--input_file", default="./llm_datasets/conversation_arc.jsonl", type=str, help="input_file")
    parser.add_argument("--model", default="nllb200", type=str, help="model")
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
    elif args.mode=="TowerInstruct":
        from models.TowerInstruct import translate_ko2en, translate_en2ko

    result=[]
    for data in tqdm(json_data):
        for conversation in data['conversations']:
            text = conversation['value']
            #print(text)
            ko_text = translate_en2ko(text)
            en_text = translate_ko2en(ko_text)
            #print('ko_text', ko_text)
            conversation['ko'] = ko_text
            conversation['en'] = en_text
        data['translation'] = 'args.model'
        result.append(data)

    save_json(result, f'llm_ko_datasets/conversation_arc_{args.model}.jsonl')


if __name__ == "__main__":
    main()
