from collections import Counter, defaultdict
import json
import os
import re
import pandas as pd


results_dirs = [
    "results_bleu/",
    "results_self/",
    "results_length/",
]

cloud_model = {"google", "papago", "deepl", "azure"}


def is_duplicated(text, top_k=10, min_word_len=0):
    words = re.findall(r"\b\w+\b", text)
    word_freq = Counter(words)

    # 단어 최소 글자수 제한
    if min_word_len > 0:
        for word, count in list(word_freq.items()):
            if len(word) <= min_word_len:
                del word_freq[word]

    if len(word_freq) == 0:
        return False

    if len(word_freq) == 1 and word_freq.most_common(1)[0][1] > 5:
        return word_freq.most_common(1)

    top_items = word_freq.most_common(top_k)
    frequencies = [frequency for item, frequency in top_items]
    mean_frequency = sum(frequencies) / len(frequencies)

    prev_frequency = 0
    index = 0

    if mean_frequency < 5:
        return False

    for item, frequency in top_items:
        if (prev_frequency - frequency) > mean_frequency:
            if index <= 1:
                return False
            # print(prev_frequency, frequency, mean_frequency, item)
            return top_items

        prev_frequency = frequency
        index += 1

    return False


def is_length_exceed(reference, generation, min_ratio=0.2, max_ratio=2):
    return not min_ratio < (len(generation) / len(reference)) < max_ratio


def get_average(*a):
    return round(sum(a) / len(a), 2)


def decorate_model_name(model):
    if model in cloud_model:
        return model
    return f'<a style="color: var(--link-text-color);text-decoration: underline;text-decoration-style: dotted;" href="https://huggingface.co/{model}" target="_blank">{model}</a>'


def create():
    bleu_by_src = defaultdict(lambda: defaultdict(list))
    sbleu_total = defaultdict(list)
    bleu_by_length = defaultdict(lambda: defaultdict(list))
    duplicate_count = defaultdict(int)
    length_exceeds_count = defaultdict(int)

    for dir in results_dirs:
        for filename in os.listdir(dir):
            if not filename.endswith(".jsonl"):
                continue
            file_path = os.path.join(dir, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    data = json.loads(line)
                    if dir == "results_bleu/":
                        bleu_by_src[data["model"]]["Average"].append(data["bleu"])
                        bleu_by_src[data["model"]][data["src"]].append(data["bleu"])
                        if is_duplicated(data["generation"]):
                            duplicate_count[data["model"]] += 1
                        if is_length_exceed(data["reference"], data["generation"]):
                            length_exceeds_count[data["model"]] += 1
                    elif dir == "results_self/":
                        sbleu_total[data["model"]].append(data["bleu"])
                    elif dir == "results_length/":
                        bleu_by_length[data["model"]]["Average"].append(data["bleu"])
                        bleu_by_length[data["model"]][f"~{data['length']}"].append(
                            data["bleu"]
                        )

    avg_bleu = dict(
        sorted(
            [
                (model, get_average(*bleu_list["Average"]))
                for model, bleu_list in bleu_by_src.items()
            ],
            key=lambda x: x[1],
            reverse=True,
        )
    )
    avg_sbleu = {
        model: get_average(*bleu_list) for model, bleu_list in sbleu_total.items()
    }
    avg_bleu_sl = {
        model: get_average(*bleu_list["Average"])
        for model, bleu_list in bleu_by_length.items()
    }

    # bleu_and_sbleu 테이블 생성
    model_list = avg_bleu.keys()
    bleu_list = list(avg_bleu.values())
    sbleu_list = [avg_sbleu[model] for model in model_list]
    bleu_sl_list = [avg_bleu_sl[model] for model in model_list]
    type_list = [
        "Cloud" if model in cloud_model else "HuggingFace" for model in model_list
    ]
    average_list = [
        get_average(avg_bleu[model], avg_sbleu[model], avg_bleu_sl[model])
        for model in model_list
    ]
    duplicate_list = [duplicate_count[model] for model in model_list]
    length_exceeds_list = [length_exceeds_count[model] for model in model_list]

    bleu_and_sbleu_table = {}
    bleu_and_sbleu_table["Type"] = type_list
    bleu_and_sbleu_table["Model"] = list(map(decorate_model_name, model_list))
    bleu_and_sbleu_table["Average"] = average_list
    bleu_and_sbleu_table["Bleu"] = bleu_list
    bleu_and_sbleu_table["SBleu"] = sbleu_list
    bleu_and_sbleu_table["Bleu-SL"] = bleu_sl_list
    bleu_and_sbleu_table["Duplicate"] = duplicate_list
    bleu_and_sbleu_table["Length Exceeds"] = length_exceeds_list

    bleu_and_sbleu_table = pd.DataFrame.from_dict(bleu_and_sbleu_table)
    bleu_and_sbleu_table.insert(
        0,
        "Rank",
        bleu_and_sbleu_table["Average"].rank(method="min", ascending=False).astype(int),
    )
    bleu_and_sbleu_table = bleu_and_sbleu_table.sort_values(by="Rank")

    # bleu_by_src 테이블 생성
    for model in bleu_by_src:
        for src in bleu_by_src[model]:
            bleu_by_src[model][src] = get_average(*bleu_by_src[model][src])

    bleu_by_src_table = pd.DataFrame.from_dict(bleu_by_src, orient="index")
    model_list = bleu_by_src_table.index.to_list()
    type_list = [
        "Cloud" if model in cloud_model else "HuggingFace" for model in model_list
    ]
    bleu_by_src_table.insert(0, "Model", list(map(decorate_model_name, model_list)))
    bleu_by_src_table.insert(0, "Type", type_list)
    bleu_by_src_table.insert(
        0,
        "Rank",
        bleu_by_src_table["Average"].rank(method="min", ascending=False).astype(int),
    )
    bleu_by_src_table = bleu_by_src_table.sort_values(by="Rank")

    # bleu_by_length 테이블 생성
    for model in bleu_by_length:
        for src in bleu_by_length[model]:
            bleu_by_length[model][src] = get_average(*bleu_by_length[model][src])

    bleu_by_length_table = pd.DataFrame.from_dict(bleu_by_length, orient="index")
    model_list = bleu_by_length_table.index.to_list()
    type_list = [
        "Cloud" if model in cloud_model else "HuggingFace" for model in model_list
    ]
    bleu_by_length_table.insert(0, "Model", list(map(decorate_model_name, model_list)))
    bleu_by_length_table.insert(0, "Type", type_list)
    bleu_by_length_table.insert(
        0,
        "Rank",
        bleu_by_length_table["Average"].rank(method="min", ascending=False).astype(int),
    )
    bleu_by_length_table = bleu_by_length_table.sort_values(by="Rank")

    return bleu_and_sbleu_table, bleu_by_src_table, bleu_by_length_table
