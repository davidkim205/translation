import argparse
import json
import os
from man_file import load_json, save_json, get_file_list
from bleu_score import simple_score


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "--input_file",
        default="/work/translation/results_2",
        type=str,
        help="input_file",
    )
    parser.add_argument(
        "--test_file",
        default="/work/translation/data/komt-1810k-test.jsonl",
        type=str,
        help="test_file",
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
    model_src_score = {
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
    origin_file = "data/komt-1810k-test.jsonl"
    origin_json_data = load_json(origin_file)
    index_to_src = list(map(lambda x: x["src"], origin_json_data))
    file_list = get_file_list(args.input_file)
    for input_file in file_list:
        output_file = f"results_temp/{os.path.basename(input_file)}"
        model_score = []
        json_data = load_json(input_file)
        for data in json_data:

            # # results 데이터 리폼(src => text, src에 datatype)
            # if "text" in data:
            #     break
            # text = data["src"]
            # src = index_to_src[int(data["index"])]
            # result = {
            #     "index": data["index"],
            #     "lang": data["lang"],
            #     "text": text,
            #     "trans": data["trans"],
            #     "label": data["label"],
            #     "bleu": data["bleu"],
            #     "model": data["model"],
            #     "src": src,
            # }
            # save_json([result], output_file)

            # # translation(trans와 label을 비교)
            # if data["lang"] == "en":
            #     trans_lang = "ko"
            # else:
            #     trans_lang = "en"
            # data["bleu"] = round(
            #     simple_score(data["trans"], data["label"], trans_lang), 2
            # )
            # save_json([data], output_file)

            # # translation2(text와 re_trans를 비교)
            # data["bleu"] = round(
            #     simple_score(data["text"], data["re_trans"], trans_lang), 2
            # )
            # save_json([data], output_file)

            if data["src"] not in src_list:
                continue
            src_list[data["src"]].append(data["bleu"])
            model_src_score[data["src"]].append(data["bleu"])
            model_score.append(data["bleu"])
        name, _ = os.path.splitext(os.path.basename(input_file))
        name = name.split("result_", 1)[-1]
        print("\n", name)
        print("\tavg_bleu_score: ", round(sum(model_score) / len(model_score), 2))
        print()
        for key in src_list:
            score = round(sum(src_list[key]) / len(src_list[key]), 2)
            print(f"\t{key}: {score}")
            src_list[key] = []
        print()
    print("\n", "src별 평균 score")
    for key in model_src_score:
        score = round(sum(model_src_score[key]) / len(model_src_score[key]), 2)
        print(f"\t{key}: {score}")


if __name__ == "__main__":
    main()
