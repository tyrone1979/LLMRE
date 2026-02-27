# Zero-shot document-level biomedical relation extraction via scenario-based prompt design in two-stage with LLM
- paper link: [https://arxiv.org/abs/2505.01077](https://doi.org/10.1016/j.compbiolchem.2026.108978)
## abstract

Document-level biomedical relation extraction is a crucial task due to the complex interactions among multiple entities distributed across lengthy scientific texts. Traditional supervised methods are constrained by their dependency on large, expensively annotated datasets. Such datasets are particularly scarce in specialized biomedical domains. In addition, these methods require substantial computational resources for model fine-tuning. To address these limitations, we propose a novel zero-shot framework that leverages the intrinsic knowledge of large language models through structured prompting. Our method adopts a two-stage framework. First, named entity recognition and normalization identify chemical, disease, and gene entities while extracting synonym and hypernym relations. Second, relation extraction determines inter-entity relationships based on predefined schemas, along with the evaluation methods to assess the quality of these prompts. The framework’s effectiveness is driven by scenario-based prompt design principles, instantiated in a reusable five-part template. Experimental results on the ChemDisGene and CDR benchmarks demonstrate that our approach achieves competitive performance with state-of-the-art supervised methods. It eliminates the need for task-specific training data and reduces computational demands. This work indicates that well-structured zero-shot prompting is a viable and resource-efficient approach for extracting biomedical knowledge.

## citation
```
@article{ZHAO2026108978,
title = {Zero-shot document-level biomedical relation extraction via scenario-based prompt design in two-stage with LLM},
journal = {Computational Biology and Chemistry},
volume = {123},
pages = {108978},
year = {2026},
issn = {1476-9271},
doi = {https://doi.org/10.1016/j.compbiolchem.2026.108978},
url = {https://www.sciencedirect.com/science/article/pii/S1476927126001039},
author = {Lei Zhao and Ling Kang and Quan Guo},
}
```

## quick start
### Code Structure
For a detailed description of the project code structure, see [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

### Hardware requirement:
- GPU: Nvidia RTX A6000 48 GB x 2 
- CPU: Intel Xeon 2.3Hz x 2
- Memory: 128GB DDR4

### Software
- OS: Ubuntu 24.04.6 LTS (GNU/Linux 5.4.0-205-generic x86_64) Tested
- Python version: 3.11.10 tested
- PostgreSQL(optional) version: (Ubuntu 16.10-0ubuntu0.24.04.1) for LLM response cache only.

### Setup
- cd src/
- pip -r requirements.txt
- config run.sh
```shell
#!/bin/bash

# 设置参数
function=$1
llm_url="http://localhost:11434"
model="gpt-oss:120b"
temperature=0.0
input="dev.txt"
#input="test.txt"
datasource="cdr"
#datasource="chemdisgene"
wandb="OFF"
cacheurl="postgresql://postgres:postgres@localhost:5432/postgres"
#cacheurl="nocache"
python run.py --function $function  \
              --llm_url $llm_url \
              --model $model \
              --temperature $temperature \
              --datasource $datasource \
	            --input $input \
              --wandb $wandb  \
              --cache $cacheurl
```
- function: NER, RE, NM for NER metrics output, RM for RE metrics output, ONE for ONE stage model, just for metrics comparison.
- SOTA model: gpt-oss:120b by Oct 17th, 2025.
- input: dev.txt for CDR, test.txt for ChemDisGene
- wandb: ON for wandb.ai usage.
- cacheurl: DB url for LLM response cache. The program gets responses from cache if the prompt and response exist in the cache DB. Only PostgreSQL is tested.

- Run both NER and RE
```shell
run.sh FULL
```
- Run NER or RE separately.
```shell
run.sh NER #for NER only
run.sh RE #for RE only
```
- Run NER or RE metrics only
```shell
run.sh NM #for NER metrics only
run.sh RM #for RE metrics only
```

## RE results
## CDR
- run RE by GPT-OSS 120b, updated on Oct 17th,2025. 

| type | TP | FP | FN | Precision |  Recall | F1  |
| --- | --- | --- | --- | --- | --- | --- |
| ['induce'] | 826 | 246 | 168 |  0.770522 | 0.830986 | 0.799613 |

## ChemDisGene
- run RE by Llama 3.1 70b, same with paper.

| Type                                      | TP  | FP  | FN  | Precision | Recall  | F1 Score |
|-------------------------------------------|-----|-----|-----|-----------|---------|----------|
| chem_disease:marker/mechanism             | 421 | 218 | 227 | 0.658842  | 0.649691| 0.654235 |
| chem_disease:therapeutic                  | 321 | 196 | 106 | 0.620890  | 0.751756| 0.680085 |
| chem_gene:affects^binding                 | 78  | 32  | 116 | 0.709091  | 0.402062| 0.513158 |
| chem_gene:affects^expression              | 54  | 86  | 28  | 0.385714  | 0.658537| 0.486486 |
| chem_gene:affects^localization            | 21  | 22  | 20  | 0.488372  | 0.512195| 0.500000 |
| chem_gene:decreases^activity              | 177 | 208 | 134 | 0.459740  | 0.569132| 0.508621 |
| chem_gene:decreases^expression            | 355 | 369 | 81  | 0.490331  | 0.814220| 0.612069 |
| chem_gene:decreases^metabolic_processing  | 28  | 48  | 30  | 0.368421  | 0.482759| 0.417910 |
| chem_gene:increases^activity              | 139 | 227 | 174 | 0.379781  | 0.444089| 0.409426 |
| chem_gene:increases^expression            | 315 | 166 | 221 | 0.654886  | 0.587687| 0.619469 |
| chem_gene:increases^metabolic_processing  | 51  | 60  | 77  | 0.459459  | 0.398438| 0.426778 |
| chem_gene:increases^transport             | 21  | 19  | 20  | 0.525000  | 0.512195| 0.518519 |
| gene_disease:marker/mechanism             | 341 | 371 | 143 | 0.478933  | 0.704545| 0.570234 |
| gene_disease:therapeutic                  | 31  | 49  | 51  | 0.387500  | 0.378049| 0.382716 |


- running RE by GPT-OSS 120b.
- micro metrics
  
|  TP  | FP |  FN | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- | 
|2406 | 2028 | 1375 | 0.542625 | 0.63634 | 0.585758 |

- group metrics
  
| Type                                      | TP  | FP  | FN  | Precision | Recall  | F1 Score |
|-------------------------------------------|-----|-----|-----|-----------|---------|----------|
|           ['chem_disease:marker/mechanism'] | 538 | 251 | 110 |  0.681876 | 0.830247 | 0.748782 |
|                ['chem_disease:therapeutic'] | 320 | 180|  107 |   0.640000 | 0.749415 | 0.690399 |
|               ['chem_gene:affects^binding'] | 133 | 199 |  61 |   0.400602 | 0.685567 | 0.505703 |
|            ['chem_gene:affects^expression'] |  48 |  84 |  34 |   0.363636 | 0.585366 | 0.448598 |
|          ['chem_gene:affects^localization'] |  24 |  28 |  17 |   0.461538 | 0.585366 | 0.516129 |
|            ['chem_gene:decreases^activity'] | 204 | 284 | 107 |   0.418033 | 0.655949 | 0.510638 |
|          ['chem_gene:decreases^expression'] | 279 | 162 | 157 |   0.632653 | 0.639908 | 0.636260 |
|['chem_gene:decreases^metabolic_processing'] |  38 |  15 |  20 |   0.716981 | 0.655172 | 0.684685 |
|            ['chem_gene:increases^activity'] | 212 | 386 | 101 |   0.354515 | 0.677316 | 0.465423 |
|          ['chem_gene:increases^expression'] | 303 | 171 | 233 |   0.639241 | 0.565299 | 0.600000 |
|['chem_gene:increases^metabolic_processing'] |  72 |  64 |  56 |   0.529412 | 0.562500 | 0.545455 |
|           ['chem_gene:increases^transport'] |  22 |  43 |  19 |   0.338462 | 0.536585 | 0.415094 |
|           ['gene_disease:marker/mechanism'] | 185 | 114 | 299 |   0.618729 | 0.382231 | 0.472542 |
|                ['gene_disease:therapeutic'] |  28 |  47 |  54 |   0.373333 | 0.341463 | 0.356688 |
				




