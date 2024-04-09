import argparse
import json
import os
from tqdm import tqdm
from utils.simple_bleu import simple_score
from model import load_model, translate_en2ko, translate_ko2en
from utils.file_handler import load_json, save_json
           

def task_bleu(data):
    input = data['en']
    reference = data['ko']
    generation = translate_en2ko(input)

    bleu = simple_score(reference, generation)
    bleu = round(bleu, 3)
    result = {
        "reference": reference,
        "generation": generation,
        "bleu": bleu,
        "lang": 'en',
        "domain": data['domain'],
        'origin': data
    }
    return input, result


def task_self_bleu(data):
    reference = data['input']
    generation1 = data['generation']
    generation = translate_ko2en(generation1)

    bleu = simple_score(reference, generation)
    bleu = round(bleu, 3)
    result = {
        "reference": reference,
        "generation": generation,
        "generation1": generation1,
        "bleu": bleu,
        'lang': data['lang'],
        'domain': data['domain'],
        'origin': data['origin']
    }
    return result


def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument(
        "--input_file",
        default="./data/komt-1810k-test.jsonl",
        type=str,
        help="input_file",
    )
    parser.add_argument("--output", default=None, type=str, help="model path")
    parser.add_argument("--model", default="davidkim205/iris-7b", type=str, help="model")
    parser.add_argument("--template_name", default=None, type=str, help="template_name")
    args = parser.parse_args()
    json_data = load_json(args.input_file)[:5]

    load_model(args.model, args.template_name)

    def make_output(args, prefix):
        if args.output:
            output = args.output
        else:
            filename = args.model.split('/')[-1]
            output = f"results_{prefix}/{filename}-domain.jsonl"
        return output
    
    results = []
    # task bleu
    print('task bleu ')
    for index, data in tqdm(enumerate(json_data)):

        input, result = task_bleu(data)
        result['index'] = index
        result['model'] = args.model

        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        save_json([result], make_output(args, 'domain_bleu'))
        result['input'] = input
        results.append(result)

    # task self bleu 
    print('task self bleu')
    for index, data in tqdm(enumerate(results)):
        
        result = task_self_bleu(data)
        result['index'] = index
        result['model'] = args.model

        print(json.dumps(result, ensure_ascii=False, indent=2))
        save_json([result], make_output(args, 'domain_self'))


if __name__ == "__main__":
    main()