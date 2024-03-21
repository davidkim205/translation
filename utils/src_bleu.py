import argparse
import json
import os
from man_file import load_json, get_file_list


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
        "aihub-parallel-translation": [],
        "aihub-food": [],
        "aihub-techsci": [],
        "para_pat": [],
        "aihub-speechtype-based-machine-translation": [],
        "aihub-basicsci": [],
        "aihub-broadcast-content": [],
        "aihub-patent": [],
        "aihub-colloquial": [],
    }
    file_list = get_file_list(args.input_file)
    for input_file in file_list:
        arr = []
        json_data = load_json(input_file)
        for data in json_data:
            if data["src"] not in src_list:
                continue
            src_list[data["src"]].append(data["bleu"])
            arr.append(data["bleu"])
        name, _ = os.path.splitext(os.path.basename(input_file))
        print("\n", name)
        for key, val in src_list.items():
            score = round(sum(val) / len(val), 2)
            print(f"\t{key}: {score}")
            src_list[key] = []
        print(len(arr))
        print("\n\tavg: ", round(sum(arr) / len(arr), 2))


if __name__ == "__main__":
    main()
