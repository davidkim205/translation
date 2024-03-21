import argparse
import json
import os
from tqdm import tqdm
from utils.bleu_score import simple_score
from utils.tokenizer import text_tokenize
from utils.man_file import load_json, save_json


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
    elif args.model == "synatra":
        from models.synatra import translate_ko2en, translate_en2ko
    results = []
    for index, data in tqdm(enumerate(json_data)):
        # {"conversations": [{"from": "human", "value": "다음 문장을 한글로 번역하세요.\nDior is giving me all of my fairytale fantasies."}, {"from": "gpt", "value": "디올이 나에게 모든 동화적 환상을 심어주고 있어."}], "src": "aihub-MTPE"}
        chat = data["conversations"]
        src = chat[0]["value"]
        dst = chat[1]["value"]
        if chat[0]["value"].find("한글로 번역하세요.") != -1:
            lang = "en"
        else:
            lang = "ko"
        if lang == "en":
            src = src.split("한글로 번역하세요.\n", 1)[-1]
            try:
                trans = translate_en2ko(src)
            except Exception as e:
                trans = ""
        elif lang == "ko":
            src = src.split("영어로 번역하세요.\n", 1)[-1]
            try:
                trans = translate_ko2en(src)
            except Exception as e:
                trans = ""
        bleu = simple_score(dst, trans, lang)
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
        save_json([result], f"results_2/result_{args.model}.jsonl")


if __name__ == "__main__":
    main()
