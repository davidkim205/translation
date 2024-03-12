import argparse
import json
import os
from tqdm import tqdm
from utils.bleu_score import simple_score


# 결과 파일 경로이름을 생성
def gen_output_filename(filename, model):
    if model:
        model = f"_{model}"
    name, extension = os.path.splitext(os.path.basename(filename))
    return f"llm_ko_datasets/ko_{name}{model}{extension}"


def load_json(filename, n):
    json_data = []
    with open(filename, "r", encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != ".jsonl":
            json_data = json.load(f)
        else:
            for i, line in enumerate(f):
                if i < n:
                    continue
                elif i >= n + 100:
                    break
                json_data.append(json.loads(line))
    return json_data


def get_line_count(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


# 파일이 존재하면 마지막 줄 뒤에 추가합니다.
def save_json(json_data, filename, option="a"):
    filename = filename.replace(" ", "_")
    with open(filename, option, encoding="utf-8") as f:
        if not filename.endswith(".jsonl"):
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            for data in json_data:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")


# 대화 번역 트랜잭션
# def cloud_translation(translate_en2ko, api, conversations):
#     for conversation in conversations:
#         text = conversation['value']
#         if ko_text := translate_en2ko(api, text):
#             conversation['ko'] = ko_text
#         else:
#             return False
#     return True


def translate_ko_arc_challenge(translate_en2ko, api, row):
    question = row["question"]
    if not (ko_question := translate_en2ko(api, question)):
        return False
    else:
        choices = row["choices"]["text"]
        ko_choices = []
        for choice in choices:
            if ko_choice := translate_en2ko(api, choice):
                ko_choices.append(ko_choice)
            else:
                return False
    row["question"] = ko_question
    row["choices"]["text"] = ko_choices
    return True


def translate_ko_truthfulaq_mc1(translate_en2ko, api, row):
    question = row["question"]
    if not (ko_question := translate_en2ko(api, question)):
        return False
    else:
        choices = row["mc1_targets"]["choices"]
        ko_choices1 = []
        for choice in choices:
            if ko_choice := translate_en2ko(api, choice):
                ko_choices1.append(ko_choice)
            else:
                return False
        else:
            choices = row["mc2_targets"]["choices"]
            ko_choices2 = []
            for choice in choices:
                if ko_choice := translate_en2ko(api, choice):
                    ko_choices2.append(ko_choice)
                else:
                    return False
    row["question"] = ko_question
    row["mc1_targets"]["choices"] = ko_choices1
    row["mc2_targets"]["choices"] = ko_choices2
    return True


def translate_ko_hellaswag(translate_en2ko, api, row):
    if (ko_activity_label := row["activity_label"]) and not (
        ko_activity_label := translate_en2ko(api, row["activity_label"])
    ):
        return False
    if (ko_ctx_a := row["ctx_a"]) and not (
        ko_ctx_a := translate_en2ko(api, row["ctx_a"])
    ):
        return False
    if (ko_ctx_b := row["ctx_b"]) and not (
        ko_ctx_b := translate_en2ko(api, row["ctx_b"])
    ):
        return False
    if (ko_ctx := row["ctx"]) and not (ko_ctx := translate_en2ko(api, row["ctx"])):
        return False
    ko_endings = []
    for ending in row["endings"]:
        if (ko_ending := ending) and not (ko_ending := translate_en2ko(api, ending)):
            return False
        ko_endings.append(ko_ending)
    row["activity_label"] = ko_activity_label
    row["ctx_a"] = ko_ctx_a
    row["ctx_b"] = ko_ctx_b
    row["ctx"] = ko_ctx
    row["endings"] = ko_endings
    return True


def translate_mathqa(translate_en2ko, translate_ko2en, row):
    keys = ["original_question", "response", "query"]
    try:
        for key in keys:
            row[f"ko_{key}"] = translate_en2ko(row[key])
            row[f"en_{key}"] = translate_ko2en(row[f"ko_{key}"])
    except Exception as e:
        print(e)
        return False
    return True


def translate_python_code(translate_en2ko, translate_ko2en, row):
    keys = ["output"]
    try:
        for key in keys:
            row[f"ko_{key}"] = translate_en2ko(row[key])
            row[f"en_{key}"] = translate_ko2en(row[f"ko_{key}"])
    except Exception as e:
        print(e)
        return False
    return True


def translate_openorca(translate_en2ko, translate_ko2en, row):
    keys = ["system_prompt", "question", "response"]
    try:
        for key in keys:
            row[f"ko_{key}"] = translate_en2ko(row[key])
            row[f"en_{key}"] = translate_ko2en(row[f"ko_{key}"])
    except Exception as e:
        print(e)
        return False
    return True


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "--input_file",
        default="./llm_datasets/conversation_arc.jsonl",
        type=str,
        help="input_file",
    )
    parser.add_argument("--model", default="TowerInstruct", type=str, help="model")
    parser.add_argument(
        "--dataset", default="ko_arc_challenge", type=str, help="dataset"
    )
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
    elif args.model == "cloud_api":
        from cloud_api import translate_en2ko

        # 해당 순서대로 소진 시 다음 API 호출
        api_list = ["azure", "google"]
        # 이미 번역된 데이터는 다시 번역하지 않게 구현
        try:
            result_data = load_json(gen_output_filename(args.input_file, args.model))

        except FileNotFoundError:
            result_data = []
            pass
        cloud_translation = {
            "ko_arc_challenge": translate_ko_arc_challenge,
            "ko_truthfulqa_mc1": translate_ko_truthfulaq_mc1,
            "hellaswag": translate_ko_hellaswag,
            "mathqa": translate_mathqa,
            "python_code": translate_python_code,
            "openorca": translate_openorca,
        }
    local_translate = {
        "mathqa": translate_mathqa,
        "python_code": translate_python_code,
        "openorca": translate_openorca,
    }
    # 번역 API 사용
    if args.model == "cloud_api":
        # json_data = json_data[:21]
        json_data = json_data[len(result_data) :]
        api_idx = 0
        api = api_list[api_idx]
        output_filename = gen_output_filename(args.input_file, "")
        cloud_output_filename = gen_output_filename(args.input_file, args.model)
        for data in tqdm(json_data):
            try:
                while not cloud_translation[args.dataset](translate_en2ko, api, data):
                    api_idx += 1
                    api = api_list[api_idx]
                else:
                    save_json([data], output_filename, "a")
                    data["translation"] = f"{api}_api"
                    save_json([data], cloud_output_filename, "a")
            except IndexError:
                break
    # 로컬 모델 사용
    else:
        output_filename = gen_output_filename(args.input_file, args.model)
        line_count = get_line_count(output_filename)
        json_data = load_json(args.input_file, line_count)
        for data in tqdm(json_data):
            local_translate[args.dataset](translate_en2ko, translate_ko2en, data)
            save_json([data], output_filename)

            # for conversation in data['conversations']:
            #     text = conversation['value']
            #     #print(text)
            #     try:
            #         ko_text = translate_en2ko(text)
            #         en_text = translate_ko2en(ko_text)
            #     except:
            #         ko_text = ""
            #         en_text = ""
            #     #print('ko_text', ko_text)
            #     conversation['ko'] = ko_text
            #     conversation['en'] = en_text
            # data['translation'] = args.model


if __name__ == "__main__":
    main()
