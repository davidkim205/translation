import argparse
import json
import os
from tqdm.asyncio import tqdm
from random import uniform
from deep_translator import GoogleTranslator
from swiftshadow.classes import Proxy
from fp.fp import FreeProxy
import asyncio
import aiofiles
import concurrent.futures
import random


def gen_output_filename(filename):
    name, extension = os.path.splitext(os.path.basename(filename))
    return f'llm_ko_datasets/google_{name}{extension}'


async def load_json(filename):
    json_data = []
    async with aiofiles.open(filename, 'r', encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != '.jsonl':
            json_data = json.load(f)
        else:
            async for line in f:
                json_data.append(json.loads(line))
    return json_data


# 파일이 존재하면 마지막 줄 뒤에 추가합니다.
async def save_json(json_data, filename, option="a"):
    filename = filename.replace(' ', '_')
    async with aiofiles.open(filename, option, encoding="utf-8") as f:
        for data in json_data:
            await f.write(json.dumps(data, ensure_ascii=False) + "\n")


# arc 번역
def translate_arc(translator, row):
    question = row['question']
    choices = row['choices']['text']
    try:
        result = translator.translate_batch([question, *choices])
        row['question'] = result[:1]
        row['choices']['text'] = result[1:]
    except:
        return False
    return True


def translate_hellaswag(translator, row):
    result = {}
    try:
        for k, v in list(row.items())[1:6]:
            if v:
                if type(v) == str:
                    result[k] = translator.translate(v)
                else:
                    result[k] = translator.translate_batch(v)
    except:
        return False
    for key in result:
        row[key] = result[key]
    return True


def translate_truthfulqa_gen(translator, row):
    result = {}
    try:
        for attr in list(row.keys())[:-1]:
            if type(row[attr]) == str:
                result[attr] = translator.translate(row[attr])
            else:
                result[attr] = translator.translate_batch(row[attr])
    except:
        return False
    for key in result:
        row[key] = result[key]
    return True


async def translate_truthfulqa_mc1(en2ko_translator, ko2en_translator, row):
    text = f"{row['question']}###{row['mc1_targets']['choices'][0]}"
    loop = asyncio.get_running_loop()
    try:
        ko_text = await loop.run_in_executor(None, en2ko_translator.translate, text)
        await asyncio.sleep(uniform(1, 2))
        en_text = await loop.run_in_executor(None, ko2en_translator.translate, ko_text)
        # await asyncio.sleep(uniform(0.3, 0.6))
        # mc1_choices = await loop.run_in_executor(None, translator.translate_batch, row['mc1_targets']['choices'])
        # await asyncio.sleep(uniform(1, 2))
        # mc2_choices = await loop.run_in_executor(None, translator.translate_batch, row['mc2_targets']['choices'])
        
    except Exception as e:
        print(e)
        return False
    q, a = text.split("\#\#\#")
    row['q'] = text
    row['ko_qna'] = ko_text
    row['en_qna'] = en_text
    return True


async def translate_task(executor, output_filename, free_proxy, translate_dataset, row, idx):
    loop = asyncio.get_running_loop()
    proxy = await loop.run_in_executor(executor, free_proxy.get)

    en2ko_translator = GoogleTranslator(source="en", target="ko", proxies={proxy.split(":")[0]: proxy})
    ko2en_translator = GoogleTranslator(source="ko", target="en", proxies={proxy.split(":")[0]: proxy})

    while not (await translate_dataset(en2ko_translator, ko2en_translator, row)):
        await asyncio.sleep(5)
        proxy = await loop.run_in_executor(executor, free_proxy.get)
        en2ko_translator = GoogleTranslator(source="en", target="ko", proxies={proxy.split(":")[0]: proxy})
        ko2en_translator = GoogleTranslator(source="ko", target="en", proxies={proxy.split(":")[0]: proxy})
    else:
        # row['idx'] = idx
        await save_json([row], output_filename)


async def main():
    # free_proxy = FreeProxy(rand=True, elite=True)
    # proxy = free_proxy.get()
    # ko_translator = GoogleTranslator(source="en", target="ko", proxies={proxy.split(":")[0]: proxy})
    # en_translator = GoogleTranslator(source="ko", target="en", proxies={proxy.split(":")[0]: proxy})
    # while True:
    #     text = input('>')
    #     ko_text = ko_translator.translate(text=text)
    #     print(ko_text)
    #     en_text = en_translator.translate(text=ko_text)
    #     print(en_text)
        

    parser = argparse.ArgumentParser("argument")
    parser.add_argument("--input_file", type=str, help="input_file")
    parser.add_argument("--dataset", type=str, help="dataset")
    parser.add_argument("--translator", default="google", type=str, help="translator")
    args = parser.parse_args()

    json_data = await load_json(args.input_file)
    json_data = random.sample(json_data, 100)
    output_filename = gen_output_filename(args.input_file)

    # # result_data = await load_json(output_filename)
    # # result_data = sorted(result_data, key=lambda x: x["idx"])
    # # await save_json(result_data, output_filename, "w")
    # # return

    # # try:
    # #     result_data = await load_json(output_filename)
    # #     json_data = json_data[len(result_data):]
    # # except FileNotFoundError:
    # #     pass

    translate_dataset = {
        "arc": translate_arc,
        "hellaswag": translate_hellaswag,
        "truthfulqa_mc1": translate_truthfulqa_mc1,
        "truthfulqa_gen": translate_truthfulqa_gen,
    }

    # # json_data = json_data[:10]
    free_proxy = FreeProxy(rand=True, elite=True)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    tasks = []
    for i, row in enumerate(json_data):
        asyncio.create_task(translate_task(executor, output_filename, free_proxy, translate_dataset[args.dataset], row, i))
        await asyncio.sleep(uniform(1, 2))

    # tasks = [asyncio.create_task(translate_task(executor, output_filename, free_proxy, translate_dataset[args.dataset], row, i)) for i, row in enumerate(json_data)]
    async for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        await task


    # 번역 데이터 정합성 검증
    # en_json_data = load_json(args.input_file)
    # ko_json_data = deque(load_json(translator_output_filename))
    # while len(en_json_data) != len(ko_json_data):
    #     for i in range(len(en_json_data)):
    #         if i >= len(ko_json_data) or en_json_data[i]['id'] != ko_json_data[i]['id']:
    #             row = en_json_data[i]
    #             while True:
    #                 if translate_dataset[args.dataset](translator, row):
    #                     save_json([row], f"temp_{output_filename}")
    #                     row['translation'] = f"{args.translator}_api"
    #                     save_json([row], f"temp_{translator_output_filename}")
    #                     ko_json_data.appendleft(None)
    #                     sleep(uniform(0.1, 0.2))
    #                     break
    #                 else:
    #                     translator = gen_translator(*translator_dict[args.translator])
    #         else:
    #             save_json([ko_json_data[i]], f"temp_{output_filename}")
    #             save_json([ko_json_data[i]], f"temp_{translator_output_filename}")
    #     os.rename(f"temp_{output_filename}", output_filename)
    #     os.rename(f"temp_{translator_output_filename}", translator_output_filename)
    #     en_json_data = load_json(args.input_file)
    #     ko_json_data = deque(load_json(output_filename))

if __name__ == "__main__":
    asyncio.run(main())