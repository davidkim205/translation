import argparse
import json
import os
from tqdm import tqdm
from utils.simple_bleu import simple_score


def load_json(filename):
    json_data = []
    with open(filename, "r", encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != ".jsonl":
            json_data = json.load(f)
        else:
            for line in f:
                json_data.append(json.loads(line))
    return json_data


def save_json(json_data, filename, option="a"):
    directory, _ = os.path.split(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = filename.replace(" ", "_")
    with open(filename, option, encoding="utf-8") as f:
        if not filename.endswith(".jsonl"):
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            for data in json_data:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")

def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "--input_file",
        default="./data/komt-1810k-test.jsonl",
        type=str,
        help="input_file",
    )
    parser.add_argument(
        "--model_path",
        default=None,
        type=str,
        help="model path",
    )
    parser.add_argument("--output", default="", type=str, help="model path")
    parser.add_argument("--model", default="iris_7b", type=str, help="model")
    args = parser.parse_args()
    json_data = load_json(args.input_file)

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
    elif args.model == "synatra":
        from models.synatra import translate_ko2en, translate_en2ko
    elif args.model == "iris_7b":
        from models.iris_7b import translate_ko2en, translate_en2ko
        if args.model_path:
            from models.iris_7b import load_model
            load_model(args.model_path)

    for index, data in tqdm(enumerate(json_data)):
        chat = data["conversations"]
        src = data["src"]
        input = chat[0]["value"]
        reference = chat[1]["value"]
        
        def clean_text(text):
            if chat[0]["value"].find("한글로 번역하세요.") != -1:
                cur_lang = "en"
            
            else:
                cur_lang = "ko"
            text = text.split("번역하세요.\n", 1)[-1]
            return text, cur_lang
        input, cur_lang = clean_text(input)
        def do_translation(text, cur_lang):
            trans = ""
            try:
                if cur_lang == "en":
                    trans = translate_en2ko(text)
                else:
                    trans = translate_ko2en(text)
            except Exception as e:
                    trans = ""
            return trans
        generation = do_translation(input, cur_lang)

        bleu = simple_score(reference, generation)
        bleu = round(bleu, 3)
        result = {
            "index": index,
            "reference": reference,
            "generation": generation,
            "bleu": bleu,
            "lang": cur_lang,
            "model": args.model,
            "src": src,
            'conversations':chat
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.output:
            output = args.output
        else:
            if args.model_path:
                filename = args.model_path.split('/')[-1]
            else:
                filename = args.model
            output = f"results/result-{args.model}-{filename}.jsonl"
        save_json([result], output)


if __name__ == "__main__":
    main()
