import argparse
import json
import os
from tqdm import tqdm
from utils.simple_bleu import simple_score
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
    parser.add_argument(
        "--model_path",
        default=None,
        type=str,
        help="model path",
    )
    parser.add_argument("--output", default="", type=str, help="model path")
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

        if args.model_path:
            from models.iris_mistral import load_model

            load_model(args.model_path)
    elif args.model == "synatra":
        from models.synatra import translate_ko2en, translate_en2ko
        
    for index, data in tqdm(enumerate(json_data)):
        # {"conversations": [{"from": "human", "value": "다음 문장을 한글로 번역하세요.\nDior is giving me all of my fairytale fantasies."}, {"from": "gpt", "value": "디올이 나에게 모든 동화적 환상을 심어주고 있어."}], "src": "aihub-MTPE"}
        chat = data["conversations"]
        src = data["src"]
        input = chat[0]["value"]

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
        generation1 = do_translation(input, cur_lang)
        next_lang = "ko" if cur_lang == "en" else "en"
        generation2 = do_translation(generation1, next_lang)

        bleu = simple_score(input, generation2)
        bleu = round(bleu, 3)
        result = {
            "index": index,
            "reference": input,
            "generation": generation2,
            "generation1": generation1,
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
            output = f"results_self/result_self-{args.model}-{filename}.jsonl"
        save_json([result], output)


if __name__ == "__main__":
    main()
