import os
import pandas as pd

from collections import defaultdict
from evaluate import eval_criteria, eval_problem
from utils.decorate import cloud_model, decorate_model_name
from utils.file_handler import load_json


def aggregate(criteria):
    dir_per_criteria = {
        'domain': [
            'results_domain_bleu/',
            'results_domain_self/',
        ],
        'length': [
            'results_length/',
        ],
        'src': [
            'results_src_bleu/',
            'results_src_self/',
        ]
    }
    results = []
    for dir in dir_per_criteria[criteria]:
        model_bleu_scores = defaultdict(lambda: defaultdict(list))
        model_length_exceeds = defaultdict(list)
        model_duplicated = defaultdict(list)
        for filename in os.listdir(dir):
            if not filename.endswith('.jsonl'): # JSONL 파일인 경우에만 처리
                continue

            file_path = os.path.join(dir, filename)
            json_data = load_json(file_path)
            eval_criteria(json_data, model_bleu_scores, criteria)
            eval_problem(json_data, model_length_exceeds, model_duplicated)
        for model in model_duplicated:
            model_duplicated[model] = len(model_duplicated[model])
            model_length_exceeds[model] = len(model_length_exceeds[model])
    
        duplicated = pd.DataFrame.from_dict(model_duplicated, orient='index', columns=['Duplicate'])
        length_exceeds = pd.DataFrame.from_dict(model_length_exceeds, orient='index', columns=['Length Exceeds'])
        df = pd.DataFrame.from_dict(model_bleu_scores, orient='index')
        df = df.join(duplicated)
        df = df.join(length_exceeds)
        df.rename(columns={'average': 'Average'}, inplace=True)
        df.reset_index(inplace=True, names="Model")
        df["Model"] = list(map(decorate_model_name, df["Model"]))
        df.insert(
            0,
            "Type",
            list(
                map(lambda x: "Cloud" if x in cloud_model else "HuggingFace",
                df["Model"])
            ),
        )
        df.insert(
            0, "Rank", df["Average"].rank(method="min", ascending=False).astype(int)
        )
        # df = df.sort_values(by="Rank")
        results.append(df)
    return results


def create():
    criteria_list = [
        'domain',
        'src',
        'length',
    ]
    bleu_tables = []
    sbleu_tables = []
    for criteria in criteria_list:
        results = aggregate(criteria)
        bleu_tables.append(results[0])
        if criteria != 'length':
            sbleu_tables.append(results[1])
    bleu_and_sbleu = bleu_tables[0][['Type', 'Model', 'Average']].copy()
    bleu_and_sbleu.rename(columns={'Average': 'Bleu'}, inplace=True)

    
    sbleu_score = sbleu_tables[0][['Average']].copy()
    sbleu_score.rename(columns={'Average': 'SBleu'}, inplace=True)
    bleu_and_sbleu = bleu_and_sbleu.join(sbleu_score)

    bleu_sl_score = bleu_tables[2][['Average']].copy()
    bleu_sl_score.rename(columns={'Average': 'Bleu-SL'}, inplace=True)
    bleu_and_sbleu = bleu_and_sbleu.join(bleu_sl_score)

    problem = bleu_tables[0][['Duplicate', 'Length Exceeds']].copy()
    bleu_and_sbleu = bleu_and_sbleu.join(problem)
    bleu_and_sbleu['Average'] = bleu_and_sbleu[['Bleu', 'SBleu', 'Bleu-SL']].mean(axis=1).round(2)
    bleu_and_sbleu.insert(2, 'Average', bleu_and_sbleu.pop('Average'))
    bleu_and_sbleu.insert(
            0, "Rank", bleu_and_sbleu["Average"].rank(method="min", ascending=False).astype(int)
        )
    bleu_tables.insert(0, bleu_and_sbleu)
    bleu_tables = list(map(lambda x: x.sort_values(by='Rank'), bleu_tables))
    return bleu_tables


def main():
    tables = create()
    for table in tables:
        print("\n==============\n - ***DF!")
        print(table)
        print('\n - ***markdown!')
        print(table.to_markdown())


if __name__ == "__main__":
    main()
