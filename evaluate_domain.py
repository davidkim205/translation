import os
import json
from collections import defaultdict
from nltk.translate.bleu_score import corpus_bleu
import statistics
import argparse
import json
import os
import re
from collections import Counter

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
    return not min_ratio <= (len(generation) / len(reference)) <= max_ratio

def get_average(a):
    return round(sum(a) / len(a), 2)


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "directory",
        type=str,
        help="input_file",
    )
    parser.add_argument('--detail', action='store_true', help='detail')
    args = parser.parse_args()
    
    # 각 파일별로 src에 대한 bleu 점수를 저장할 딕셔너리
    model_domain_bleu_scores = defaultdict(lambda: defaultdict(list))
    model_length_ratio = defaultdict(list)
    model_duplicated = defaultdict(list)
    model_duplicated_detail = defaultdict(list)
    # 디렉토리 내의 모든 파일에 대해 반복
    for filename in os.listdir(args.directory):
        if filename.endswith('.jsonl'):  # JSONL 파일인 경우에만 처리
            file_path = os.path.join(args.directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                for index, line in enumerate(file):
                    data = json.loads(line)
                    # src = data['src']
                    model = data['model']
                    domain = data['domain']
                    bleu_score = data['bleu']
                    model_domain_bleu_scores[model][domain].append(bleu_score)

                    # check_length
                    reference_length = len(data['reference'])
                    generation_length = len(data['generation'])
                    model_length_ratio[model].append(round(generation_length / reference_length, 1))

                    # check duplication
                    word_count = is_duplicated(data['generation'])
                    model_duplicated[model].append(0 if word_count is False else 1)
                    if word_count != False:
                        model_duplicated_detail[model].append({'index':index, 'count':word_count,'generation':data['generation']})
                for domain in model_domain_bleu_scores[model]:
                    model_domain_bleu_scores[model][domain] = get_average(model_domain_bleu_scores[model][domain])

    # 각 파일별로 src에 대한 bleu 평균 계산
    print('bleu scores')
    for model, domain_bleu_scores in model_domain_bleu_scores.items():
        avg_bleu = get_average(list(domain_bleu_scores.values()))
        length_raio=[]
        cur_length_ratio = model_length_ratio[model]
        ratio_mean = round(statistics.mean(cur_length_ratio), 1)
        for index, ratio in enumerate(cur_length_ratio):
            if ratio < 0.2 or ratio > 2.0:
                length_raio.append((index,ratio))
        print(f"{model}: {avg_bleu:.2f}, out_of_range_count={len(length_raio)}, duplicate={sum(model_duplicated[model])}")
        for domain in domain_bleu_scores:
            print(f'\t{domain}: {domain_bleu_scores[domain]}')
        if args.detail:
            print(f'\t error length:{length_raio}')
        if args.detail:
            print(f"\t duplication")
            for info in model_duplicated_detail[model]:
                print('\t\t', info)

if __name__ == "__main__":
    main()