import os
import json
from collections import defaultdict
from nltk.translate.bleu_score import corpus_bleu
import statistics
import argparse
import json
import os



def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "directory",
        type=str,
        help="input_file",
    )
    args = parser.parse_args()
    
    # 각 파일별로 src에 대한 bleu 점수를 저장할 딕셔너리
    file_src_bleu_scores = defaultdict(list)

    src_bleu_scores = defaultdict(list)

    # 디렉토리 내의 모든 파일에 대해 반복
    for filename in os.listdir(args.directory):
        if filename.endswith('.jsonl'):  # JSONL 파일인 경우에만 처리
            file_path = os.path.join(args.directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    data = json.loads(line)
                    src = data['src']
                    bleu_score = data['bleu']
                    src_bleu_scores[src].append(bleu_score)
                    file_src_bleu_scores[filename].append(bleu_score)

    sorted_items = sorted(file_src_bleu_scores.items(), key=lambda x: statistics.mean(x[1]))
    # 각 파일별로 src에 대한 bleu 평균 계산
    print('bleu scores')
    for filename, src_bleu_scores in sorted_items:
        avg_bleu = sum(src_bleu_scores) / len(src_bleu_scores)
        print(f"'{filename}': {avg_bleu:.2f}")

if __name__ == "__main__":
    main()
