import argparse
import os
import json
from utils.bleu_score import simple_score


def gen_output_filename(filename):
    name, extension = os.path.splitext(os.path.basename(filename))
    return f'llm_datasets_bleu/{name}{extension}'


def load_json(filename):
    json_data = []
    with open(filename, 'r', encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != '.jsonl':
            json_data = json.load(f)
        else:
            for line in f:
                json_data.append(json.loads(line))
    return json_data


def save_json(json_data, filename, option="w"):
    filename = filename.replace(' ', '_')
    with open(filename, option, encoding="utf-8") as f:
        if not filename.endswith('.jsonl'):
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            for data in json_data:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument("--input_file", default="./llm_datasets/conversation_arc.jsonl", type=str, help="input_file")
    args = parser.parse_args()

    json_data = load_json(args.input_file)
    bleu = []
    count = 0
    perfect = 0
    for row in json_data:
        q, a = row['qna'].split('###')
        en_q, en_a = row['en_qna'].split('###')
        # q_score = round(simple_score(q, en_q), 2)
        # a_score = round(simple_score(a, en_a), 2)
        score = round(simple_score(row['qna'], row['en_qna']), 2)
        # row['q_score'] = q_score
        # row['a_score'] = a_score
        # score = (q_score + a_score) / 2
        row['score'] = score
        if row['score'] >= 0.1:
            bleu.append(score)
            if score == 1:
                perfect += 1
        else:
            count += 1
    

    print(sum(bleu) / len(bleu))
    
    json_data.sort(key=lambda x: x['score'])
    for row in json_data:
        print(f"qna: {row['qna']}")
        print(f"ko_qna: {row['ko_qna']}")
        print(f"en_qna: {row['en_qna']}")
        print(f"score: {row['score']}")
        # print(f"q_score: {row['q_score']}")
        # print(f"a_score: {row['a_score']}")
        print()
    save_json(sorted(json_data, key=lambda x: x['score']), gen_output_filename(args.input_file))
    print(perfect)
    print(count)
if __name__ == "__main__":
    main()