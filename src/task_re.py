from data import RESchema, global_delimiter
from task import Task
from task_ner import ONENER
import csv
import importlib
from relation import RelationHandler, OneRelationHandler
from data_prompt_templates import PromptTemplate
from data import NERData
import datetime

def instantiate_class(module_name, class_name):
    # 动态导入模块
    module = importlib.import_module(module_name)
    return hasattr(module, class_name)


def append_alias(entity, title, ner_data):
    return ner_data.query_by_index(entity[1], title, entity[4])

def response_extract(response):
    if '\n' in response:
        response = response.split('\n')[-1]
    if '|' in response:
        responses=response.split('|')
    else:
        responses=[response,' ','1.0']
    return responses[0].strip(), responses[1].strip(),responses[2].strip()




class RE(Task):
    def __init__(self, model, data_handler):
        super().__init__(model, data_handler, task='RE')
        self.schemas = RESchema()
        self.re_chain = {}
        self.templates = PromptTemplate(data_handler.datasource).get_template("RE")
        self.relation_instances = []
        for class_name in self.templates.keys():
            if not instantiate_class("relation", class_name):
                self.relation_instances.append(RelationHandler(model, data_handler.datasource, class_name))

    def save(self, output, csv_data, *args):
        """
        save result
        """
        csv_reader = super().save(output, csv_data)
        result_file = open(output, 'a', newline='', encoding='utf-8')
        csv_writer = csv.writer(result_file, delimiter=global_delimiter)
        for row in csv_reader:
            #if row[0].strip().lower() == row[2].strip().lower():
            #    continue
            row.append(args[0])
            csv_writer.writerow(row)

    def process(self, **kwargs):
        result_dir = kwargs['result_dir']
        document = kwargs['document']
        ner_data_result = kwargs["ner_data_result"]
        ner_data = NERData(ner_data_result)
        # RE funciton.
        title = document.title
        record = []
        log=[]
        for relation in self.relation_instances:
            responses, heads, tails,  fulls = relation.process(document=document,
                                                                      ner_data=ner_data)
            if len(responses) > 0:
                for response, head, tail, full_text in zip(responses, heads, tails, fulls):
                    if head[0]=='telmisartan' and tail[0]=='headache':
                        pass
                    response, reason, confidence=response_extract(response)
                    if response in relation.answers and head[0].strip() != '' and tail[0].strip() != '':
                        head_alias = append_alias(head, title, ner_data)
                        tail_alias = append_alias(tail, title, ner_data)
                        for one_head in head_alias:
                            for one_tail in tail_alias:
                                if one_head[0] == one_tail[0]:
                                    continue
                                for label in relation.answers[response]:
                                    record.append(
                                        f"{one_head[0]}|{one_head[1]}|{one_head[2]}|{one_head[3]}|{one_head[4]}|{one_head[5]}|{label}|{one_tail[0]}|{one_tail[1]}|{one_tail[2]}|{one_tail[3]}|{one_tail[4]}|{one_tail[5]}|{response}")
                    else:
                        log.append(f"{relation.name}|{head[0]}|{tail[0]}|{response}")
            #self.save(f"../data/result/re_out_log.csv",log,title)
            if len(record) > 0:
                #record = hypernyms.filter(record)
                self.save(result_dir, record, title)


class ONERE(Task):
    def __init__(self, model, data_handler):
        super().__init__(model, data_handler, task='ONE')
        self.schemas = RESchema()
        self.re_chain = {}
        self.templates = PromptTemplate(data_handler.datasource).get_template("ONE")
        self.relation_instances = []
        for class_name in self.templates.keys():
            if not instantiate_class("relation", class_name):
                self.relation_instances.append(OneRelationHandler(model, data_handler.datasource, class_name))
        self.ner=ONENER()
    def save(self, output, csv_data, *args):
        """
        save result
        """
        csv_reader = super().save(output, csv_data)
        result_file = open(output, 'a', newline='', encoding='utf-8')
        csv_writer = csv.writer(result_file, delimiter=global_delimiter)
        for row in csv_reader:
            if row[0].strip().lower() == row[2].strip().lower():
                continue
            row.append(args[0])
            csv_writer.writerow(row)


    def process(self, **kwargs):
        result_dir = kwargs['result_dir']
        document = kwargs['document']
        # RE funciton.
        title = document.title
        record = []
        includes, skips = self.ner.get_include_and_skip(document)

        for relation in self.relation_instances:
            types,_ = self.schemas.query(relation.name)
            responses= relation.process(document=document,includes=includes,skips=skips,types=list(types))
            if len(responses) > 0:
                for response in responses:
                    lines=response.split('\n')
                    for line in lines:
                        split_data= line.split('|')
                        if len(split_data)==9:
                            if split_data[1].lower().strip()!='chemical entity name' and split_data[1].strip()!='---':
                                chemical_name=split_data[1].strip()
                                chemical_index=split_data[2].strip()
                                chemical_sent_id_and_pos=self.ner.get_entity_pos(chemical_name,document)
                                chemical_flag=split_data[3].strip()
                                disease_name=split_data[5].strip()
                                disease_sent_id_and_pos=self.ner.get_entity_pos(disease_name,document)
                                disease_index=split_data[6].strip()
                                disease_flag=split_data[7].strip()
                                for chemical_one in chemical_sent_id_and_pos:
                                    for disease_one in disease_sent_id_and_pos:
                                        record.append( f"{chemical_name}|Chemical|{chemical_one[0]}|\"[{chemical_one[1][0]}, {chemical_one[1][1]}]\"|{chemical_index}|{chemical_flag}|"
                                                       f"{relation.name}|{disease_name}|Disease|{disease_one[0]}|\"[{disease_one[1][0]}, {disease_one[1][1]}]\"|{disease_index}|{disease_flag}")
            if len(record) > 0:
                self.save(result_dir, record, title)
