# translation

## Installation
``` 
conda create -n translation python=3.10
conda activate translation

pip install -r requirements.txt

```
## usage
### example
``` 

CUDA_VISIBLE_DEVICES=0 python translation.py --input_file ./llm_datasets/conversation_arc.jsonl --model gugugo
```
