import argparse
import json
import os
from tqdm import tqdm
from utils.bleu_score import simple_score
from utils.man_file import load_json, save_json


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "--input_file", default="./data/orca_samples.jsonl", type=str, help="input_file"
    )
    parser.add_argument("--model", default="iris_mistral", type=str, help="model")
    args = parser.parse_args()

    if args.model == "gugugo":
        from models.gugugo import translate_en2ko, translate_ko2en
    elif args.model == "madlad400":
        from models.madlad400 import translate_ko2en, translate_en2ko
    elif args.model == "mbart50":
        from models.mbart50 import translate_en2ko, translate_ko2en
    elif args.model == "nllb200":
        from models.nllb200 import translate_ko2en, translate_en2ko
    elif args.model == "TowerInstruct":
        from models.TowerInstruct import translate_ko2en, translate_en2ko
    elif args.model == "iris_qwen_14b":
        from models.iris_qwen_14b import translate_ko2en, translate_en2ko
    elif args.model == "iris_qwen_7b":
        from models.iris_qwen_7b import translate_ko2en, translate_en2ko
    elif args.model == "iris_qwen_4b":
        from models.iris_qwen_4b import translate_ko2en, translate_en2ko
    elif args.model == "iris_solar":
        from models.iris_solar import translate_ko2en, translate_en2ko
    elif args.model == "iris_mistral":
        from models.iris_mistral import translate_ko2en, translate_en2ko

    output_file = os.path.basename(args.input_file)
    json_data = load_json(args.input_file)
    result = []
    for data in tqdm(json_data):
        try:
            if data["lang"] == "en":
                re_trans = translate_ko2en(data["trans"])
            else:
                re_trans = translate_en2ko(data["trans"])
        except:
            re_trans = ""
        result = {
            "index": data["index"],
            "lang": data["lang"],
            "text": data["text"],
            "trans": data["trans"],
            "re_trans": re_trans,
            "label": data["label"],
            "bleu": simple_score(data["text"], re_trans, lang=data["lang"]),
            "model": data["model"],
            "src": data["src"],
        }
        # text = data["src"]
        # data["src"] = origin_json_data[i]["src"]
        # print(text)
        # ko_text = translate_en2ko(text)
        # en_text = translate_ko2en(ko_text)
        # print('ko_text', ko_text)
        # data[args.model + "-ko"] = ko_text
        # data[args.model + "-en"] = en_text
        # data["translation"] = args.model

        save_json([result], f"results1/{output_file}")


if __name__ == "__main__":
    main()
