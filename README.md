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
python translation2.py --model davidkim205/iris-7b
```

## Evaluation

### BLEU 

| model                          | BLEU | SBLEU |
| ------------------------------ | ---- | ----- |
| ...                            |      |       |
| squarelike/Gugugo-koen-7B-V1.1 | 0.4  | 0.3   |
| davidkim205/iris-7b(**ours**)  | 0.5  | 0.4   |



| cloud api                     | BLEU | SBLEU |
| ----------------------------- | ---- | ----- |
| papago                        | 0.2  | 0.3   |
| google api                    | 0.4  | 0.3   |
| davidkim205/iris-7b(**ours**) | 0.5  | 0.4   |

* SBLEU: Self-evaluation BLEU

### BLEU by source


| model                          | MTPE | techsci2 | ..   | ..   | ..   |
| ------------------------------ | ---- | -------- | ---- | ---- | ---- |
| ...                            |      |          |      |      |      |
| squarelike/Gugugo-koen-7B-V1.1 | 0.4  | 0.3      |      |      |      |
| davidkim205/iris-7b(**ours**)  | 0.5  | 0.4      |      |      |      |

![src-bleu](./assets/src-bleu.png)



### BLEU by sentence length

| model                          | ~100 | ~500 | ~1000 | ~1500 | ~2000 |
| ------------------------------ | ---- | ---- | ----- | ----- | ----- |
| ...                            |      |      |       |       |       |
| squarelike/Gugugo-koen-7B-V1.1 | 0.4  | 0.3  | 0.2   | 0.3   | 0.4   |
| davidkim205/iris-7b(**ours**)  | 0.5  | 0.4  | 0.4   | 0.5   | 0.4   |