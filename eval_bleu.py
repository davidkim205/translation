import argparse
from tqdm import tqdm
import json
import os
import pandas as pd
from utils.bleu_score import simple_score
import re


def gen_filename(filename, model):
    return f"llm_ko_datasets/ko_{filename}_{model}.jsonl"


def load_json(filename, n, a):
    json_data = []
    with open(filename, "r", encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != ".jsonl":
            json_data = json.load(f)
        else:
            for i, line in enumerate(f):
                if i < n:
                    continue
                elif i >= n + a:
                    break
                json_data.append(json.loads(line))
    return json_data


def get_line_count(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except FileNotFoundError as e:
        print(e)
        return 0


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


def main():
    dataset_attr = {
        # "MetaMathQA-395K": ["original_question", "response", "query"],
        "OpenOrca": ["question", "response"],
        # "python-codes-25k": ["output"],
    }
    model_list = [
        "gugugo",
        "madlad400",
        "mbart50",
        "nllb200",
        "TowerInstruct",
    ]
    json_line = 100
    for dataset in dataset_attr:
        origin_filename = "/work/translation/data/OpenOrca_6048_google.jsonl"
        # bleu_filename = f"llm_datasets_bleu/{dataset}.jsonl"
        # bleu_line_count = get_line_count(bleu_filename)
        bleu_line_count = 0
        origin_data = load_json(origin_filename, bleu_line_count, json_line)
        json_data_list = {}
        output_filename = f"data/orca_samples.jsonl"
        result = {}
        for row in origin_data:
            string_temp = []
            for attr in dataset_attr[dataset]:
                result["en"] = row[attr]
                save_json([result], output_filename)
                string_temp.append(row[attr])
            result["en"] = "\n".join(string_temp)
            save_json([result], output_filename)
        return
        for model in model_list:
            filename = gen_filename(dataset, model)
            try:
                json_data_list[model] = load_json(filename, bleu_line_count, json_line)
            except FileNotFoundError as e:
                print(e)
                continue
        korean_pattern = re.compile("[가-힣]")
        for i, row in enumerate(origin_data):
            for attr in dataset_attr[dataset]:
                text = row[attr]
                del row[attr]
                row[attr] = text
                row[f"ko_{attr}"] = ""
                row[f"en_{attr}"] = ""
                row[f"bleu_{attr}"] = -1
                row[f"{attr}_translation"] = ""
                for model in model_list:
                    if (
                        f"bleu_{attr}" in json_data_list[model][i]
                        and (
                            row[f"bleu_{attr}"]
                            < json_data_list[model][i][f"bleu_{attr}"]
                        )
                        and korean_pattern.search(
                            json_data_list[model][i][f"ko_{attr}"]
                        )
                    ):
                        row[f"ko_{attr}"] = json_data_list[model][i][f"ko_{attr}"]
                        row[f"en_{attr}"] = json_data_list[model][i][f"en_{attr}"]
                        row[f"bleu_{attr}"] = json_data_list[model][i][f"bleu_{attr}"]
                        row[f"{attr}_translation"] = model
            save_json([row], f"llm_datasets_bleu/{dataset}.jsonl")
        df = pd.DataFrame(origin_data)
        df.to_excel(f"llm_ko_datasets_excel/{dataset}.xlsx", index=False)

    # for model in model_score:
    #     print(model)
    #     for dataset in model_score[model]:
    #         print(f"\t- {dataset}")
    #         for attr in model_score[model][dataset]:
    #             print(f"\t\t{attr}: {model_score[model][dataset][attr]}")


if __name__ == "__main__":
    main()
