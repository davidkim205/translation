import argparse
from tqdm import tqdm
from utils.bleu_score import simple_score
from translation import load_json, save_json


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument("--input_file", default="./llm_ko_datasets/conversation_arc_nllb200.jsonl", type=str, help="input_file")
    args = parser.parse_args()

    json_data = load_json(args.input_file)[:90]
    bleu = []
    result = []
    count = 0
    perfect = 0
    for data in tqdm(json_data):
        for conversation in data['conversations']:
            ref_text = conversation['value']
            cand_text = conversation['en']
            conversation['bleu'] = simple_score(ref_text, cand_text)
            score = round(conversation['bleu'], 2)
            if score > 0:
                bleu.append(score)
                if score == 1:
                    perfect += 1
            else:
                count += 1
        result.append(data)
    if result:
        save_json(result, f"{args.input_file}_bleu.jsonl")
    print(sum(bleu) / len(bleu))
    print(perfect)
    print(count)

if __name__ == "__main__":
    main()