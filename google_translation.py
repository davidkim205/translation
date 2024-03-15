import argparse
import json
import os
from tqdm.asyncio import tqdm
from deep_translator import GoogleTranslator
import asyncio
import aiofiles
import concurrent.futures
from stem import Signal
from stem.control import Controller
from utils.bleu_score import simple_score


def gen_output_filename(filename):
    name, extension = os.path.splitext(os.path.basename(filename))
    return f"data/{name}_google{extension}"


async def load_json(filename, start, end):
    json_data = []
    count = 0
    async with aiofiles.open(filename, "r", encoding="utf-8") as f:
        if os.path.splitext(filename)[1] != ".jsonl":
            json_data = json.load(f)
        else:
            async for line in f:
                if count < start:
                    count += 1
                    continue
                # if count < n + a:
                #     break
                if count >= end:
                    break
                count += 1
                json_data.append(json.loads(line))

    return json_data


async def save_json(json_data, filename, option="a"):
    filename = filename.replace(" ", "_")
    async with aiofiles.open(filename, option, encoding="utf-8") as f:
        for data in json_data:
            await f.write(json.dumps(data, ensure_ascii=False) + "\n")


async def translate_task(
    en2ko_translator, ko2en_translator, output_filename, row, attrs
):
    loop = asyncio.get_running_loop()
    try:
        for attr in attrs:
            row[f"ko_{attr}"] = await loop.run_in_executor(
                None, en2ko_translator.translate, row[attr]
            )
            row[f"en_{attr}"] = await loop.run_in_executor(
                None, ko2en_translator.translate, row[attr]
            )
            bleu = simple_score(row[attr], row[f"en_{attr}"])
            if bleu < 0.8:
                print("no!")
                return
            print("yes!")
    except Exception as e:
        print(e)
        return
    await save_json([row], output_filename)


def renew_connection():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="aiteam00")
        controller.signal(Signal.NEWNYM)


async def main():
    parser = argparse.ArgumentParser("argument")
    parser.add_argument("--input_file", type=str, help="input_file")
    parser.add_argument("--dataset", type=str, help="dataset")
    args = parser.parse_args()
    json_data = await load_json(args.input_file, 0, 500)
    output_filename = gen_output_filename(args.input_file)

    dataset_attr = {
        "MetaMathQA-395K": ["original_question", "response", "query"],
        "OpenOrca": ["question", "response"],
        # "python-codes-25k": ["output"],
    }

    # # result_data = await load_json(output_filename)
    # # result_data = sorted(result_data, key=lambda x: x["idx"])
    # # await save_json(result_data, output_filename, "w")
    # # return

    # # try:
    # #     result_data = await load_json(output_filename)
    # #     json_data = json_data[len(result_data):]
    # # except FileNotFoundError:
    # #     pass

    en2ko_translator = GoogleTranslator(
        source="en",
        target="ko",
        proxies={"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"},
    )
    ko2en_translator = GoogleTranslator(
        source="ko",
        target="en",
        proxies={"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"},
    )
    # executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    loop = asyncio.get_running_loop()
    tasks = []
    for i, row in enumerate(json_data):
        asyncio.create_task(
            translate_task(
                en2ko_translator,
                ko2en_translator,
                output_filename,
                row,
                dataset_attr[args.dataset],
            )
        )
        await loop.run_in_executor(None, renew_connection)

    async for task in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
        await task


if __name__ == "__main__":
    asyncio.run(main())
