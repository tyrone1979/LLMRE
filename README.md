# Zero-Shot Document-Level Biomedical Relation Extraction via Scenario-based Prompt Design in Two-Stage with LLM
- paper link: https://arxiv.org/abs/2505.01077
## abstract

With the advent of artificial intelligence (AI), many researchers are attempting to extract structured information from document-level biomedical literature by fine-tuning large language models (LLMs). However, they face significant challenges such as the need for expensive hardware, like high-performance GPUs and the high labor costs associated with annotating training datasets, especially in biomedical realm. Recent research on LLMs, such as GPT-4 and Llama3, has shown promising performance in zero-shot settings, inspiring us to explore a novel approach to achieve the same results from unannotated full documents using general LLMs with lower hardware and labor costs. Our approach combines two major stages: named entity recognition (NER) and relation extraction (RE). NER identifies chemical, disease and gene entities from the document with synonym and hypernym extraction using an LLM with a crafted prompt. RE extracts relations between entities based on predefined relation schemas and prompts. To enhance the effectiveness of prompt, we propose a five-part template structure and a scenario-based prompt design principles, along with evaluation method to systematically assess the prompts. Finally, we evaluated our approach against fine-tuning and pre-trained models on two biomedical datasets: ChemDisGene and CDR. The experimental results indicate that our proposed method can achieve comparable accuracy levels to fine-tuning and pre-trained models but with reduced human and hardware expenses.

## citation
```
@misc{zhao2025zeroshotdocumentlevelbiomedicalrelation,
      title={Zero-Shot Document-Level Biomedical Relation Extraction via Scenario-based Prompt Design in Two-Stage with LLM}, 
      author={Lei Zhao and Ling Kang and Quan Guo},
      year={2025},
      eprint={2505.01077},
      archivePrefix={arXiv},
      primaryClass={cs.NE},
      url={https://arxiv.org/abs/2505.01077}, 
}
```

## quick start
### Hardware requirement:
- GPU:Nvidia RTX A6000 48G x 2 
- CPU:Intel Xeon 2.3Hz x 2
- Memory: 128G DDR4

### Software
- OS:Ubuntu 24.04.6 LTS (GNU/Linux 5.4.0-205-generic x86_64) Tested
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
- cacheurl: DB url for LLM response cache. Program gets responses from cache if prompt and response exist in cache DB. Only PostgreSQL tested.

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

| type | TP | FP | FN | Precision |  Recall | F1 | Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
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