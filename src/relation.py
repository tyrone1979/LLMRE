from data_prompt_templates import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from data import RESchema, NERData, global_delimiter
import csv
from io import StringIO


class RelationHandler:
    def __init__(self, model, datasource, name):
        self.model = model
        self.name = name
        if name in PromptTemplate(datasource).get_template("RE"):
            self.template = PromptTemplate(datasource).get_template("RE")[name]
            self.chain = ChatPromptTemplate.from_template(
                    self.template["question"]) | self.model.llm | StrOutputParser()
            self.answers=self.template["answers"]
            self.schemas = RESchema()
        else:
            self.template = ''
            self.schemas = None

    def query(self, queries):
        """
        feed batch to LLM. seems to better performance by one record.
        """
        return self.chain.batch(queries, {"max_concurrency": 16})

    def process(self, **kwargs):
        ner_data = kwargs["ner_data"]
        document = kwargs['document']
        title = document.title
        full_text = ''
        for sentence in document.doc:
            full_text += sentence
        _, pairs = self.schemas.query(self.name)
        queries = []
        heads = []
        tails = []
        #labels = []
        fulls = []
        for pair in pairs:
            head_type = pair[0]
            tail_type = pair[1]
            head_entities_reduce_alias = reduce_synonym(ner_data.query(head_type, title))
            tail_entities_reduce_alias = reduce_synonym(ner_data.query(tail_type, title))
            for head_entity in head_entities_reduce_alias:
                for tail_entity in tail_entities_reduce_alias:
                    if tail_entity[0] == head_entity[0]:
                        continue
                    queries.append(
                        {"input": full_text, "head": head_entity[0], "tail": tail_entity[0]})
                    heads.append(head_entity)
                    tails.append(tail_entity)
                    #labels.append(self.name)
                    fulls.append(full_text)
        if len(queries) > 0:
            responses = self.query(queries)
            return responses, heads, tails, fulls
        return [], _, _, _


# 去重函数
def reduce_synonym(entities):
    # 创建一个空字典来存储第4列值相同的第一个元组
    unique_entities = {}
    for entity in entities:
        first_column_value = entity[4]
        # 如果这个值还没有被记录过，就添加到字典中
        if first_column_value not in unique_entities:
            unique_entities[first_column_value] = entity
    return list(unique_entities.values())


class OneRelationHandler:
    def __init__(self, model, datasource, name):
        self.model = model
        self.name = name
        if name in PromptTemplate(datasource).get_template("ONE"):
            self.template = PromptTemplate(datasource).get_template("ONE")[name]
            self.chain = ChatPromptTemplate.from_template(
                self.template[0]) | self.model.llm | StrOutputParser()
        else:
            self.template = ''

    def query(self, queries):
        """
        feed batch to LLM. seems to better performance by one record.
        """
        return self.chain.batch(queries, {"max_concurrency": 16})

    def process(self, **kwargs):
        document = kwargs['document']
        includes=kwargs['includes']
        skips=kwargs['skips']
        types=kwargs['types']

        full_text = ''
        for sentence in document.doc:
            full_text += sentence
        query={"input": full_text}
        for type in types:
            query[type + "_include"]=[]
            query[type + "_skip"]=[]

        for key, items in includes.items():
            query[key + "_include"]=items
        for key, items in skips.items():
            query[key + "_skip"]=items
        queries = [query]
        responses = self.query(queries)
        return responses


class hypernyms(RelationHandler):
    def __init__(self, model, data_handler):
        self.name = 'hypernyms'
        super().__init__(model, data_handler.datasource, self.name)

    def process(self, **kwargs):
        """
        generate alias relation.
        """
        entities = kwargs['entities']
        document = kwargs['document']
        if self.schemas is None:
            return entities
        full_text = ' '.join(document.doc)
        for type in entities:
            if type != 'Disease' and type != 'Chemical':
                continue
            queries = []
            hypernyms_list = []
            items = list(entities[type].items())
            n = len(items)  # word count
            for i in range(n):
                head = items[i][0]
                for j in range(i + 1, n):  # 从i+1开始，避免重复比较和自身比较
                    tail = items[j][0]
                    if items[i][1][0]['index'] == items[j][1][0]['index']:  # synonym
                        continue
                    else:
                        hypernyms_list.append((i, j))
                        queries.append({"input": full_text, "head": head,
                                        "tail": tail, "type": type})
                        hypernyms_list.append((j, i))
                        queries.append({"input": full_text, "head": tail,
                                        "tail": head, "type": type})
            if len(hypernyms_list) > 0:
                hypernym_response_list = []
                responses = self.query(queries)
                for response, (head_entity_index, tail_entity_index) in zip(responses, hypernyms_list):
                    if response in self.answers:
                        for one in items[head_entity_index][1]:
                            one['flag'] = 'H'
                        hypernym_response_list.append((head_entity_index, tail_entity_index))
                for (head_entity_index, tail_entity_index) in hypernym_response_list:
                    if (tail_entity_index, head_entity_index) in hypernym_response_list:
                        for one in items[head_entity_index][1]:
                            one['flag'] = '-1'
                        for one in items[tail_entity_index][1]:
                            one['flag'] = '-1'
        return entities

    @staticmethod
    def filter(data):
        csv_data = [item.split('\n\n')[1] if '\n\n' in item else item for item in data]
        filted_re = []
        head_by_flag_dict = {}

        head_tail_dict = {}
        entity_by_index_dict = {}

        for one in csv_data:
            row = one.split(global_delimiter)
            if (row[4], row[11]) not in head_tail_dict:
                head_tail_dict[(row[4], row[11])] = []
            head_tail_dict[(row[4], row[11])].append(row)

        remove_index = []
        for one in csv_data:
            row = one.split(global_delimiter)
            if row[5] == 'H':
                # chemcial is a super class
                remove_index.append(row[4])
            if row[12] == 'H':
                # handle tail [disease] hypernym case
                remove_index.append(row[11])

        for one in csv_data:
            row = one.split(global_delimiter)
            if row[4] in remove_index or row[11] in remove_index:
                continue
            else:
                filted_re.append(one)
        return filted_re


class synonym(RelationHandler):
    def __init__(self, model, data_handler):
        self.name = 'synonym'
        super().__init__(model, data_handler.datasource, self.name)

    def process(self, **kwargs):
        """
        generate alias relation.
        """
        entities = kwargs['entities']
        document = kwargs['document']
        if self.schemas is None:
            return entities
        compute_alias_type = self.schemas.query(self.name)
        index = 500
        full_text = ' '.join(document.doc)
        for type in entities:
            if type not in compute_alias_type[0]:
                continue

            queries = []
            name_list = {}
            items = list(entities[type].items())
            n = len(items)  # word count
            for i in range(n):
                name1 = items[i][0]
                for j in range(i + 1, n):  # 从i+1开始，避免重复比较和自身比较
                    name2 = items[j][0]
                    if (name1, name2) not in name_list:
                        name_list[(name1, name2)] = []
                    name_list[(name1, name2)].append(i)
                    name_list[(name1, name2)].append(j)

            if len(name_list) > 0:
                for (name1, name2) in name_list.keys():
                    queries.append({"input": full_text, "head": name1,
                                    "tail": name2, "type": type})
                responses = self.query(queries)
                for response, (name1, name2) in zip(responses, name_list.keys()):
                    if response in self.answers:
                        name1_word_index=name_list[(name1, name2)][0]
                        name2_word_index=name_list[(name1, name2)][1]
                        name1_current_index=items[name1_word_index][1][0]['index']
                        name2_current_index=items[name2_word_index][1][0]['index']
                        if name1_current_index>=500:
                            #be a alias already
                            for one in items[name2_word_index][1]:
                                one['index']=name1_current_index
                        elif name2_current_index>=500:
                            for one in items[name1_word_index][1]:
                                one['index']=name2_current_index
                        else:
                            for one in items[name1_word_index][1]:
                                one['index'] = index
                            for one in items[name2_word_index][1]:
                                one['index']=index
                            index += 1
            index += 1
        return entities
