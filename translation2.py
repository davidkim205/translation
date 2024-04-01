import argparse
import json
import os
from tqdm import tqdm
from utils.simple_bleu import simple_score
from model import load_model, translate_en2ko, translate_ko2en

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
                

def task_bleu(data):
    chat = data["conversations"]
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
        "reference": reference,
        "generation": generation,
        "bleu": bleu,
        "lang": cur_lang,
    }
    return result


def task_self_bleu(data):
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
        "reference": input,
        "generation": generation2,
        "generation1": generation1,
        "bleu": bleu,
        "lang": cur_lang,
    }
    return result


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "--input_file",
        default="./data/komt-1810k-test.jsonl",
        type=str,
        help="input_file",
    )
    parser.add_argument("--output", default=None, type=str, help="model path")
    parser.add_argument("--model", default="davidkim205/iris-7b", type=str, help="model")
    args = parser.parse_args()
    json_data = load_json(args.input_file)

    load_model(args.model)

    def make_output(args, prefix):
        if args.output:
            output = args.output
        else:
            filename = args.model.split('/')[-1]
            output = f"results_{prefix}/{filename}-result.jsonl"
        return output
    # task bleu
    print('task bleu ')
    for index, data in tqdm(enumerate(json_data)):

        result = task_bleu(data)
        result['index'] = index
        result['model'] = args.model
        result['src'] = data["src"]
        result['conversations'] = data["conversations"]

        print(json.dumps(result, ensure_ascii=False, indent=2))
        save_json([result], make_output(args, 'bleu'))

    # task self bleu 
    print('task self bleu')
    for index, data in tqdm(enumerate(json_data)):
        
        result = task_self_bleu(data)
        result['index'] = index
        result['model'] = args.model
        result['src'] = data["src"]
        result['conversations'] = data["conversations"]

        print(json.dumps(result, ensure_ascii=False, indent=2))
        save_json([result], make_output(args, 'self'))


if __name__ == "__main__":
    main()
