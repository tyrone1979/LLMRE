from model import LLMModel
import argparse
from tqdm import tqdm
import os
import wandb
from task_re import RE,ONERE
from task_ner import NER
from data_cdr import CDRHandler
from data_docred import DocREDHandler, ReDocREDHandler
from data_chemdisgene import ChemDisGeneHandler


def process_ner_metrics(model, data_handler, **kwargs):
    """
    this is only NER metrices
    """
    ner_data_result = kwargs['ner_data_result']
    wandb_open = kwargs['wandb_open']
    task = NER(model, data_handler)
    documents, doc_dict = data_handler.get_documents(datasource)
    # NER metrics
    columns_to_group = [[[1], 'label']]
    task.evaluate(ner_data, ner_data_result, doc_dict, wandb_open=wandb_open,columns_to_compare=[1,2,3,-1],columns_to_group=columns_to_group)


def process_re_metrics(model, data_handler, **kwargs):
    """
    this is only RE metrices
    """
    re_data_result = kwargs['re_data_result']
    wandb_open = kwargs['wandb_open']
    task = RE(model, data_handler)
    print("reading data...")
    documents, doc_dict = data_handler.get_documents(datasource)
    # RE metrics
    columns_to_group=[[[6],'relation']]
    task.evaluate(re_data, re_data_result, doc_dict, wandb_open=wandb_open,columns_to_compare=[2,3,6,9,10,-1],columns_to_group=columns_to_group)



def process_ner(model, data_handler, **kwargs):
    """
    request LLM to do NER task
    """
    ner_data_result = kwargs['ner_data_result']

    task = NER(model, data_handler)
    # 检查文件是否存在
    if os.path.exists(ner_data_result):
        # 如果文件存在，删除文件
        os.remove(ner_data_result)
        print(f"File {ner_data_result} has been deleted.")
    else:
        # 如果文件不存在，打印消息
        print(f"File {ner_data_result} does not exist.")
    documents, doc_dict = data_handler.get_documents(datasource)
    for document in tqdm(documents, desc="Processing NER", leave=True):
        task.process(result_dir=ner_data_result, document=document)
    # generate alias relation after NER.
    process_ner_metrics(model,data_handler,ner_data_result=ner_data_result,wandb_open=wandb_open)



def process_re(model, data_handler, **kwargs):
    """
    request LLM to do RE task.
    """
    # RE function, make sure you have NER result file and Alias file
    re_data_result = kwargs['re_data_result']
    ner_data_result = kwargs['ner_data_result']
    wandb_open = kwargs['wandb_open']
    documents, doc_dict = data_handler.get_documents(datasource)
    task = RE(model, data_handler)
    if os.path.exists(re_data_result):
        os.remove(re_data_result)
        print(f"File {re_data_result} has been deleted.")
    else:
        print(f"File {re_data_result} does not exist.")

    for document in tqdm(documents, desc="Processing RE", leave=True):
        # iterate all documents.
        task.process(result_dir=re_data_result, document=document,
                     ner_data_result=ner_data_result)

    process_re_metrics(model,data_handler,wandb_open=wandb_open,re_data_result=re_data_result,)

def process_one(model, data_handler, **kwargs):
    re_data_result = kwargs['re_data_result']
    wandb_open = kwargs['wandb_open']
    documents, doc_dict = data_handler.get_documents(datasource)
    task = ONERE(model, data_handler)
    if os.path.exists(re_data_result):
        os.remove(re_data_result)
        print(f"File {re_data_result} has been deleted.")
    else:
        print(f"File {re_data_result} does not exist.")

    for document in tqdm(documents, desc="Processing RE", leave=True):
        # iterate all documents.
        task.process(result_dir=re_data_result, document=document)

    process_re_metrics(model,data_handler,wandb_open=wandb_open,re_data_result=re_data_result,)

def process_full(model, data_handler, **kwargs):
    ner_data_result = kwargs['ner_data_result']
    wandb_open = kwargs['wandb_open']
    ner_data = kwargs['ner_data']
    extension=kwargs['extension']
    data_handler_instance.process(extension)
    process_ner(model, data_handler, ner_data_result=ner_data_result, wandb_open=wandb_open)
    process_re(model, data_handler, ner_data_result=ner_data_result, ner_data=ner_data,
               wandb_open=wandb_open, re_data_result=re_data_result)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="NER and RE Model")
    parser.add_argument('--function', type=str, default="RM", help='FULL:NER->RE,Ner Metrics/Re Metrics, or ONE: one stages')
    parser.add_argument('--llm_url', type=str, default="http://172.17.19.238:11434", help='URL of the LLM service')
    parser.add_argument('--model', type=str, default="llama3.1:70b-instruct-q8_0", help='LLM model name,llama3.1:70b-instruct-q8_0 or gpt-oss:120b')
    parser.add_argument('--temperature', type=float, default=0, help='Temperature for the LLM')
    parser.add_argument('--datasource', type=str, default="cdr", help='data source : docred,redocred,cdr,chemdisgene')
    parser.add_argument('--input', type=str, default="dev.txt", help='input data dir')
    parser.add_argument('--wandb', type=str, default="OFF", help='ON or OFF wandb')
    parser.add_argument('--cache', type=str, default="postgresql://postgres:postgres@localhost:5432/postgres", help='cache url, such as sqlite:///.cache.db, no cache = nocache') #sqlite cache causes db lock.

    args = parser.parse_args()
    wandb_open = False
    if args.wandb == "ON":
        wandb_open = True
        wandb.init(project="llmre")
    # 使用os.path.splitext分割文件名和扩展名
    base_name, extension = os.path.splitext(args.input)
    datasource = f"../data/{args.datasource}/{args.input}"
    ner_data = f'../data/{args.datasource}/{base_name}_ner.csv'
    ner_data_result = f"../data/result/{args.datasource}/{base_name}_ner.csv"
    re_data = f"../data/{args.datasource}/{base_name}_re.csv"
    re_data_result = f"../data/result/{args.datasource}/{base_name}_re.csv"
    data_handler = {
        "docred": DocREDHandler,
        "redocred": ReDocREDHandler,
        "cdr": CDRHandler,
        "chemdisgene": ChemDisGeneHandler,
    }
    data_handler_instance = data_handler[args.datasource](args.datasource)
    model = LLMModel(args.llm_url, args.model, args.temperature, args.cache,args.datasource)
    process = {"NM": process_ner_metrics,
               "RM": process_re_metrics,
               "NER": process_ner,
               "RE": process_re,
               "FULL": process_full,
               "ONE": process_one}
    if args.function in process:
        process[args.function](model,
                               data_handler_instance,
                               ner_data=ner_data,
                               ner_data_result=ner_data_result,
                               re_data=re_data,
                               re_data_result=re_data_result,
                               wandb_open=wandb_open,
                               extension=extension)
