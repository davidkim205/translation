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

| TYPE        | Model                            | BLEU | SBLEU |
| ----------- | :------------------------------- | ---- | ----- |
| HuggingFace | facebook/nllb-200-distilled-1.3B | 0.26 | 0.30  |
| HuggingFace | jbochi/madlad400-10b-mt          | 0.29 | 0.38  |
| HuggingFace | Unbabel/TowerInstruct-7B-v0.1    | 0.32 | 0.39  |
| HuggingFace | squarelike/Gugugo-koen-7B-V1.1   | 0.32 | 0.36  |
| Cloud       | Deepl                            | 0.39 | 0.45  |
| Cloud       | Azure                            | 0.40 | 0.49  |
| Cloud       | Google                           | 0.40 | 0.49  |
| HuggingFace | davidkim205/iris-7b(**ours**)    | 0.40 | 0.43  |

* SBLEU: Self-evaluation BLEU

### BLEU by source

| Type        | Model                            | aihub-MTPE | aihub-techsci2 | aihub-expertise | aihub-humanities | sharegpt-deepl-ko-translation | aihub-MT-new-corpus | aihub-socialsci | korean-parallel-corpora | aihub-parallel-translation | aihub-food | aihub-techsci | para_pat | aihub-speechtype-based-machine-translation | koopus100 | aihub-basicsci | aihub-broadcast-content | aihub-patent | aihub-colloquial |
| ----------- | :------------------------------- | ---------: | -------------: | --------------: | ---------------: | ----------------------------: | ------------------: | --------------: | ----------------------: | -------------------------: | ---------: | ------------: | -------: | -----------------------------------------: | --------: | -------------: | ----------------------: | -----------: | ---------------: |
| HuggingFace | squarelike/Gugugo-koen-7B-V1.1   |       0.46 |           0.27 |            0.28 |             0.22 |                          0.66 |                0.33 |            0.36 |                     0.1 |                       0.29 |       0.45 |          0.34 |     0.24 |                                       0.42 |      0.22 |           0.23 |                    0.42 |          0.2 |             0.26 |
| HuggingFace | jbochi/madlad400-10b-mt          |       0.45 |           0.29 |             0.2 |             0.29 |                           0.4 |                0.36 |            0.39 |                    0.12 |                       0.22 |       0.46 |           0.3 |     0.23 |                                       0.48 |      0.23 |           0.19 |                    0.36 |         0.01 |             0.33 |
| HuggingFace | Unbabel/TowerInstruct-7B-v0.1    |       0.46 |           0.33 |            0.28 |             0.27 |                           0.3 |                0.39 |            0.37 |                    0.14 |                       0.35 |       0.47 |          0.39 |     0.29 |                                       0.41 |      0.21 |           0.22 |                    0.36 |         0.15 |             0.33 |
| HuggingFace | facebook/nllb-200-distilled-1.3B |       0.44 |           0.28 |            0.16 |             0.23 |                          0.44 |                0.34 |            0.27 |                     0.1 |                       0.23 |       0.37 |          0.28 |     0.19 |                                       0.29 |      0.23 |           0.15 |                    0.33 |         0.09 |             0.29 |
| Cloud       | Azure                            |       0.57 |           0.36 |            0.35 |             0.29 |                          0.63 |                0.46 |            0.39 |                    0.16 |                       0.38 |       0.56 |          0.39 |     0.33 |                                       0.54 |      0.22 |           0.29 |                    0.52 |         0.35 |             0.41 |
| Cloud       | Google                           |       0.62 |           0.39 |            0.32 |             0.32 |                           0.6 |                0.45 |            0.45 |                    0.14 |                       0.38 |       0.59 |          0.43 |     0.34 |                                       0.45 |      0.22 |           0.28 |                    0.47 |         0.39 |             0.36 |
| Cloud       | Deepl                            |       0.59 |           0.33 |            0.31 |             0.32 |                           0.7 |                0.48 |            0.38 |                    0.14 |                       0.38 |       0.55 |          0.41 |     0.33 |                                       0.48 |      0.24 |           0.28 |                    0.42 |         0.37 |             0.36 |
| HuggingFace | davidkim205/iris-7b(**ours**)    |       0.49 |           0.37 |            0.34 |             0.31 |                          0.72 |                0.48 |            0.43 |                    0.11 |                       0.33 |       0.56 |          0.46 |     0.34 |                                       0.43 |       0.2 |            0.3 |                    0.47 |         0.41 |              0.4 |

![src-bleu](./assets/src-bleu.png)



### BLEU by sentence length

| model                          | ~100 | ~500 | ~1000 | ~1500 | ~2000 |
| ------------------------------ | ---- | ---- | ----- | ----- | ----- |
| ...                            |      |      |       |       |       |
| squarelike/Gugugo-koen-7B-V1.1 | 0.4  | 0.3  | 0.2   | 0.3   | 0.4   |
| davidkim205/iris-7b(**ours**)  | 0.5  | 0.4  | 0.4   | 0.5   | 0.4   |