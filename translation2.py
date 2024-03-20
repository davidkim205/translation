import argparse
import json
import os
from tqdm import tqdm
from utils.bleu_score import simple_score
from utils.tokenizer import text_tokenize


# 결과 파일 경로이름을 생성
def gen_output_filename(filename, model):
    name, extension = os.path.splitext(os.path.basename(filename))
    return f"ko_data/{name}_{model}{extension}"


def load_json(filename):
    json_data = []
    with open(filename, "r", encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != ".jsonl":
            json_data = json.load(f)
        else:
            for line in f:
                json_data.append(json.loads(line))
    return json_data


# 파일이 존재하면 마지막 줄 뒤에 추가합니다.
def save_json(json_data, filename):
    filename = filename.replace(" ", "_")
    with open(filename, "a", encoding="utf-8") as f:
        if not filename.endswith(".jsonl"):
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            for data in json_data:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")


# 대화 번역 트랜잭션
def cloud_translation(translate_en2ko, api, conversations):
    for conversation in conversations:
        text = conversation["value"]
        if ko_text := translate_en2ko(api, text):
            conversation["ko"] = ko_text
        else:
            return False
    return True


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "--input_file",
        default="/work/translation/data/komt-1810k-test.jsonl",
        type=str,
        help="input_file",
    )
    parser.add_argument("--model", default="iris_mistral", type=str, help="model")
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
    results = []
    for index, data in tqdm(enumerate(json_data)):
        # {"conversations": [{"from": "human", "value": "다음 문장을 한글로 번역하세요.\nDior is giving me all of my fairytale fantasies."}, {"from": "gpt", "value": "디올이 나에게 모든 동화적 환상을 심어주고 있어."}], "src": "aihub-MTPE"}
        chat = data["conversations"]
        src = chat[0]["value"]
        dst = chat[1]["value"]
        if chat[0]["value"].find("다음 문장을 한글로 번역하세요.") != -1:
            lang = "en"
        else:
            lang = "ko"
        if lang == "en":
            src = src.split("다음 문장을 한글로 번역하세요.\n")[-1]
            trans = translate_en2ko(src)
        elif lang == "ko":
            src = src.split("다음 문장을 영어로 번역하세요.\n")[-1]
            trans = translate_ko2en(src)
        bleu = simple_score(dst, trans)
        bleu = round(bleu, 2)
        result = {
            "index": index,
            "lang": lang,
            "src": src,
            "trans": trans,
            "label": dst,
            "bleu": bleu,
            "model": args.model,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        save_json([result], f"ko_data/result_{args.model}.jsonl")


if __name__ == "__main__":
    main()
