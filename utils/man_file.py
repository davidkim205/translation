import json
import os


def get_file_list(input_file):
    file_list = []

    if os.path.isdir(input_file):
        # 입력 파일이 디렉토리인 경우
        for root, dirs, files in os.walk(input_file):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)
    else:
        # 입력 파일이 디렉토리가 아닌 경우
        file_list.append(input_file)

    return file_list


def load_json(filename):
    json_data = []
    with open(filename, "r", encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != ".jsonl":
            json_data = json.load(f)
        else:
            for line in f:
                json_data.append(json.loads(line))
    return json_data


def save_json(json_data, filename, option="a"):
    filename = filename.replace(" ", "_")
    with open(filename, option, encoding="utf-8") as f:
        if not filename.endswith(".jsonl"):
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            for data in json_data:
                json.dump(data, f, ensure_ascii=False)
                f.write("\n")
