import argparse
import json
import os
from man_file import load_json


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
