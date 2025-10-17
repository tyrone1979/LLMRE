#!/bin/bash

# 设置参数
function=$1
llm_url="http://localhost:11434"
#model="llama3.1:70b-instruct-q8_0"
model="gpt-oss:120b"
temperature=0.0
input="dev.txt"
datasource="cdr"
wandb="ON"
cacheurl="postgresql://postgres:postgres@localhost:5432/postgres"
#cacheurl="nocache"
# 调用run.py脚本并传递参数
python run.py --function $function  \
              --llm_url $llm_url \
              --model $model \
              --temperature $temperature \
              --datasource $datasource \
	            --input $input \
              --wandb $wandb  \
              --cache $cacheurl
