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
python translation.py --input_file <파일 경로> --model <모델명>
```
#### Default Value
- filename: `./llm_datasets/conversation_arc.jsonl`
- model: `TowerInstruct`

### gpu 2개 이상
```
[CUDA_VISIBLE_DEVICES=0] python translation.py --input_file <파일 경로> --model <모델명>
```

### 모델 종류
- `gugugo`
- `madlad400`
- `mbart50`
- `nllb200`
- `TowerInstruct`

### Cloud 번역 API 사용
모델명에 `cloud_api` 입력