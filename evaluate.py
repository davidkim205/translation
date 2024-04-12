import argparse
import os
import re

from collections import defaultdict, Counter
from utils.file_handler import load_json


def is_duplicated(text, top_k=10, min_word_len=0):
    words = re.findall(r'\b\w+\b', text)
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
    return not (min_ratio <= (len(generation) / len(reference)) <= max_ratio)

def get_average(a):
    return round(sum(a) / len(a), 2)


# 모델, 요소별로 평가
def eval_criteria(json_data, eval_dict, criteria):
    for data in json_data:
        model = data['model']
        eval_dict[model]['average'] = []
        element = data[criteria]
        bleu_score = data['bleu']
        eval_dict[model][element].append(bleu_score)
    
    # 요소별 평균 및 전체 평균 집계
    for element in eval_dict[model]:
        if element == 'average':
            continue
        eval_dict[model]['average'] += eval_dict[model][element]
        eval_dict[model][element] = get_average(eval_dict[model][element])
    eval_dict[model]['average'] = get_average(eval_dict[model]['average'])


# length_exceeds, duplicate 평가
def eval_problem(json_data, model_length_exceeds, model_duplicated):
    model = json_data[0]['model']
    model_length_exceeds[model] = []
    model_duplicated[model] = []
    for index, data in enumerate(json_data):
        # check_length
        if is_length_exceed(data['reference'], data['generation']):
            model_length_exceeds[model].append({'index': index, 'ratio': round(len(data['generation']) / len(data['reference']), 2)})

        # check duplication
        word_count = is_duplicated(data['generation'])
        if word_count:
            model_duplicated[model].append({'index':index, 'count':word_count})


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "directory",
        type=str,
        help="input_file",
    )
    parser.add_argument('--detail', action='store_true', help='detail')
    args = parser.parse_args()
    
    criteria_list = [
        'length',
        'domain',
        'src',
    ]
    model_bleu_scores = defaultdict(lambda: defaultdict(list))
    model_length_exceeds = defaultdict(list)
    model_duplicated = defaultdict(list)

    # 집계
    for filename in os.listdir(args.directory):
        if not filename.endswith('.jsonl'): # JSONL 파일인 경우에만 처리
            continue

        file_path = os.path.join(args.directory, filename)
        json_data = load_json(file_path)
        for criteria in criteria_list:
            if criteria not in json_data[0]:
                continue
            cur_criteria = criteria
            eval_criteria(json_data, model_bleu_scores, criteria)
            eval_problem(json_data, model_length_exceeds, model_duplicated)
            break

    # 출력
    print(f'{cur_criteria} per model')
    sorted_model = dict(sorted(model_bleu_scores.items(), key=lambda x: x[1]['average']))
    for model in sorted_model:
        bleu_scores = sorted_model[model]
        length_exceeds = model_length_exceeds[model]
        duplication = model_duplicated[model]
        if not args.detail:
            print(f"***{model}: {bleu_scores['average']:.2f}, out_of_range_count={len(length_exceeds)}, duplicate={len(duplication)}")
        else:
            print(f'\n***{model}')
            print(f'average: {bleu_scores["average"]}')
            print(f'per {cur_criteria}')
            for criteria in bleu_scores:
                print(f' - {criteria}: {bleu_scores[criteria]}')
            print(f'length exceeds: {len(length_exceeds)}')
            if length_exceeds:
                for exceed in length_exceeds:
                    print(f' - {exceed}')
            print(f'duplication: {len(duplication)}')
            if duplication:
                for dup in duplication:
                    print(f' - {dup}')


if __name__ == "__main__":
    main()