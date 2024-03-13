import argparse
from tqdm import tqdm
import json
import os
import pandas as pd
from utils.bleu_score import simple_score


def gen_filename(filename, model):
    return f"llm_ko_datasets/ko_{filename}_{model}.jsonl"


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


def main():
    dataset_attr = {
        "MetaMathQA-395K": ["original_question", "response", "query"],
        "OpenOrca": ["system_prompt", "question", "response"],
        "python-codes-25k": ["output"],
    }
    model_list = [
        "gugugo",
        "madlad400",
        "mbart50",
        "nllb200",
        "TowerInstruct",
    ]

    for dataset in dataset_attr:
        origin_filename = f"llm_datasets/{dataset}.jsonl"
        bleu_filename = f"llm_datasets_bleu/{dataset}.jsonl"
        bleu_line_count = get_line_count(bleu_filename)
        origin_data = load_json(origin_filename, bleu_line_count)
        json_data_list = {}

        # for model in model_list:
        #     filename = gen_filename(dataset, model)
        #     try:
        #         json_data_list[model] = load_json(filename, bleu_line_count)
        #     except FileNotFoundError as e:
        #         print(e)
        #         continue
        #     with open(filename, "w", encoding="utf-8") as f:
        #         pass
        #     for row in json_data_list[model]:
        #         for attr in dataset_attr[dataset]:
        #             text = row[attr]
        #             del row[attr]
        #             row[attr] = text
        #             if f"ko_{attr}" not in row:
        #                 continue
        #             text = row[f"ko_{attr}"]
        #             del row[f"ko_{attr}"]
        #             row[f"ko_{attr}"] = text
        #             if f"en_{attr}" not in row:
        #                 continue
        #             text = row[f"en_{attr}"]
        #             del row[f"en_{attr}"]
        #             row[f"en_{attr}"] = text
        #             ref_text = row[attr]
        #             cand_text = row[f"en_{attr}"]
        #             if f"bleu_{attr}" in row:
        #                 del row[f"bleu_{attr}"]
        #             row[f"bleu_{attr}"] = simple_score(ref_text, cand_text)
        #         save_json([row], filename, "a")

        for i, row in enumerate(origin_data):
            for attr in dataset_attr[dataset]:
                row[f"bleu_{attr}"] = -1
                for model in model_score:
                    if (
                        f"bleu_{attr}" in json_data_list[model][i]
                        and row[f"bleu_{attr}"]
                        < json_data_list[model][i][f"bleu_{attr}"]
                    ):
                        row[f"ko_{attr}"] = json_data_list[model][i][f"ko_{attr}"]
                        row[f"en_{attr}"] = json_data_list[model][i][f"en_{attr}"]
                        row[f"bleu_{attr}"] = json_data_list[model][i][f"bleu_{attr}"]
                        row[f"{attr}_translation"] = model
            save_json([row], f"llm_datasets_bleu/{dataset}.jsonl")
        df = pd.DataFrame(origin_data)
        df.to_excel(
            f"llm_ko_datasets_excel/{dataset}_{bleu_line_count//100}.xlsx", index=False
        )

    # for model in model_score:
    #     print(model)
    #     for dataset in model_score[model]:
    #         print(f"\t- {dataset}")
    #         for attr in model_score[model][dataset]:
    #             print(f"\t\t{attr}: {model_score[model][dataset][attr]}")


if __name__ == "__main__":
    main()
