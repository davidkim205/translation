from tqdm import tqdm
from translation import gen_output_filename, load_json, save_json

json_data1 = load_json("/work/translation/llm_ko_datasets/truthful_qa-multiple_choice-validation.jsonl")
json_data2 = load_json("/work/translation/llm_ko_datasets/ko_truthful_qa-multiple_choice-validation.jsonl")

def copy_data(data1, data2):
    keys1 = data1.keys()
    keys2 = data2.keys()
    data1[keys1[0]] = data2[keys2[0]]

for i in tqdm(range(len(json_data1))):
    data1 = json_data1[i]
    data2 = json_data2[i]
    keys1 = data1.keys()
    keys2 = data2.keys()
    for i, key in enumerate(keys1):
        if key == "question":
            data1[key] = data2[keys2[i]]
        else:
            copy_data(data1[key], data2[keys2[i]])

save_json(json_data1, gen_output_filename("ko_truthful_qa-multiple_choice-validation.jsonl", ""), "w")