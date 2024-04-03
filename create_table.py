import os
import pandas as pd

from collections import defaultdict
from evaluate import is_duplicated, is_length_exceed, get_average
from utils.decorate import cloud_model, decorate_model_name
from utils.file_handler import load_json


# results_bleu/에서 집계
def aggregate_bleu(json_data, bleu_table, src_table, length_table):
    duplicate_count = defaultdict(int)
    length_exceeds_count = defaultdict(int)

    for data in json_data:
        src_table[data["model"]]["Average"].append(data["bleu"])
        src_table[data["model"]][data["src"]].append(data["bleu"])
        if is_duplicated(data["generation"]):
            duplicate_count[data["model"]] += 1
        if is_length_exceed(data["reference"], data["generation"]):
            length_exceeds_count[data["model"]] += 1
    for model, row in src_table.items():
        src_table[model] = dict((attr, get_average(val)) for attr, val in row.items())

    # bleu, duplicate, length exceeds 추가
    for model in src_table:
        bleu_table[model]["Average"].append(src_table[model]["Average"])
        bleu_table[model]["Bleu"] = src_table[model]["Average"]
        bleu_table[model]["Duplicate"] = duplicate_count[model]
        bleu_table[model]["Length Exceeds"] = length_exceeds_count[model]


# results_self/에서 집계
def aggregate_self(json_data, bleu_table, src_table, length_table):
    sbleu_score = defaultdict(list)
    for data in json_data:
        sbleu_score[data["model"]].append(data["bleu"])

    # sbleu 추가
    for model in sbleu_score:
        bleu_table[model]["SBleu"] = get_average(sbleu_score[model])
        bleu_table[model]["Average"].append(bleu_table[model]["SBleu"])


# results_length/에서 집계
def aggregate_length(json_data, bleu_table, src_table, length_table):
    for data in json_data:
        length_table[data["model"]]["Average"].append(data["bleu"])
        length_table[data["model"]][f"~{data['length']}"].append(data["bleu"])
    for model, row in length_table.items():
        length_table[model] = dict(
            (attr, get_average(val)) for attr, val in row.items()
        )

    # bleu-sl 추가
    for model in length_table:
        bleu_table[model]["Bleu-SL"] = length_table[model]["Average"]
        bleu_table[model]["Average"].append(bleu_table[model]["Bleu-SL"])
        bleu_table[model]["Average"] = get_average(bleu_table[model]["Average"])


def create():
    results_dirs = {
        "results_bleu/": aggregate_bleu,
        "results_self/": aggregate_self,
        "results_length/": aggregate_length,
    }

    bleu_table = defaultdict(lambda: defaultdict(list))
    src_table = defaultdict(lambda: defaultdict(list))
    length_table = defaultdict(lambda: defaultdict(list))
    tables = {
        "bleu_and_sbleu": bleu_table,
        "bleu_by_src": src_table,
        "bleu_by_length": length_table,
    }

    # bleu score 집계
    for dir, aggregate in results_dirs.items():
        json_data = []
        for filename in os.listdir(dir):
            if not filename.endswith(".jsonl"):
                continue
            file_path = os.path.join(dir, filename)
            json_data += load_json(file_path)
        aggregate(json_data, *tables.values())

    # table dataframe 생성
    for table in tables:
        df = pd.DataFrame.from_dict(tables[table], orient="index")
        if table == "bleu_and_sbleu":
            df["Duplicate"] = df.pop("Duplicate")
            df["Length Exceeds"] = df.pop("Length Exceeds")
        df.reset_index(inplace=True, names="Model")
        df["Model"] = list(map(decorate_model_name, df["Model"]))
        df.insert(
            0,
            "Type",
            list(
                map(
                    lambda x: "Cloud" if x in cloud_model else "HuggingFace",
                    df["Model"],
                )
            ),
        )
        df.insert(
            0, "Rank", df["Average"].rank(method="min", ascending=False).astype(int)
        )
        df = df.sort_values(by="Rank")
        tables[table] = df

    return tables.values()


def main():
    tables = list(create())
    print("# dataframe")
    print(tables[0], "\n\n")
    print("# markdown")
    print(tables[0].to_markdown(index=False))


if __name__ == "__main__":
    main()
