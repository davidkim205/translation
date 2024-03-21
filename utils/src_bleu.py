import argparse
import json
import os


def load_json(filename):
    json_data = []
    with open(filename, "r", encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != ".jsonl":
            json_data = json.load(f)
        else:
            for line in f:
                json_data.append(json.loads(line))
    return json_data


def save_json(json_data, filename):
    filename = filename.replace(" ", "_")
    with open(filename, "a", encoding="utf-8") as f:
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
        default="/work/translation/results/result_google.jsonl",
        type=str,
        help="input_file",
    )
    args = parser.parse_args()
    src_list = {
        "aihub-MTPE": [],
        "aihub-techsci2": [],
        "aihub-expertise": [],
        "aihub-humanities": [],
        "sharegpt-deepl-ko-translation": [],
        "aihub-MT-new-corpus": [],
        "aihub-socialsci": [],
        "korean-parallel-corpora": [],
        "aihub-parallel-translation": [],
        "aihub-food": [],
        "aihub-techsci": [],
        "para_pat": [],
        "aihub-speechtype-based-machine-translation": [],
        "koopus100": [],
        "aihub-basicsci": [],
        "aihub-broadcast-content": [],
        "aihub-patent": [],
        "aihub-colloquial": [],
    }
    origin_json_data = load_json("/work/translation/data/komt-1810k-test.jsonl")
    json_data = load_json(args.input_file)
    for i in range(len(origin_json_data)):
        src_list[origin_json_data[i]["src"]].append(json_data[i]["bleu"])
    name, _ = os.path.splitext(os.path.basename(args.input_file))
    print("\n", name)
    for key, val in src_list.items():
        score = round(sum(val) / len(val), 2)
        print(f"\t{key}: {score}")


if __name__ == "__main__":
    main()
