import json
import csv
from abc import abstractmethod
import pandas as pd
import os

from data_prompt_templates import PromptTemplate

meta_rel_info_dir = "../meta/rel_info.json"
meta_ignore_txt_dir = "../meta/ignore.txt"
global_delimiter = '|'

def get_include_ner(datasource):
    return read_csv(f'../meta/include_{datasource}.csv')

def get_ignore_title():
    if not os.path.exists(meta_ignore_txt_dir):
        return []
    with open(meta_ignore_txt_dir, 'r', encoding='utf-8') as csvfile:
        lines = csvfile.readlines()
        return [line.rstrip('\n') for line in lines]


COUNTRY_LIST = ['United States', 'Japan', 'China', 'U.S.', 'USA', 'Japanese', 'Chinese', 'Australia', 'Canada', 'Italy']
ORG_LIST = [' School', ' Elementary', ' League']
MISC_LIST = [' Plan']
PLACE_LIST = ['Museum', 'Gallery', 'Park', 'Nationale']


def convert_set_to_list(o):
    if isinstance(o, set):
        return list(o)
    else:
        return o


def revise_type(word, type):
    if type == "PLACE":
        if word in COUNTRY_LIST:
            type = 'CTRY'
        if word.endswith(tuple(ORG_LIST)):
            type = 'ORG'
        if word.endswith(tuple(MISC_LIST)):
            type = 'MISC'
    if type == 'ORG':
        if any(item in word for item in PLACE_LIST):
            type = 'PLACE'
    return type


def revise_ner(word, pos=[]):
    """
    delete 'the
    """
    word = word.strip()
    word = word.replace('\n', '')
    remove_first_words = ['the ', 'The ', 'Province of ', 'City of ', 'Pope ', 'Parks in ', 'morbid ', 'rat ',
                          'superior ', 'acute ' ,'low-grade ','serum ','liposomal ','severe ','high-grade histopathological ',
                          'non-immune ','easy ','complete ','chloroquine '
                         ]
    for remove_word in remove_first_words:
        if word.startswith(remove_word):
            end = len(remove_word)
            word = word[:0] + word[end:]
            if len(pos) > 0:
                pos[0] += len(remove_word.split())

    remove_end_words = [' region', ' range', ' ranges', ' forest', ' grassland', ' deserts', ' feet', ' County',
                        ' neighbourhood', ' neighbourhoods', ' Neighbourhood', ' metropolitan area', ' mainland',
                        ' Street', ' state', ' nations', ' pills', ' changes']

    for remove_word in remove_end_words:
        if word.endswith(remove_word):
            end = len(word) - len(remove_word)
            word = word[:end]
            if len(pos) > 0:
                pos[1] -= len(remove_word.split())
    # 使用any()函数检查word中是否包含mid_words列表中的任意元素
    mid_word = 'induced '
    if len(pos) == 0 and mid_word in word:
        word = word.split(mid_word)[1]

    return word, pos


class NERData:
    def __init__(self, filename):
        # 初始化一个字典来存储数据
        self.data = {}
        self.read_data_from_csv(filename)

    def add_data(self, title, type, entity, sent_id, pos, index, flag):
        title = title.lower()
        if (type, title) not in self.data:
            self.data[(type, title)] = set()
        if entity not in self.data[(type, title)]:
            self.data[(type, title)].add((entity, type, sent_id, pos, index, flag))

    def query(self, type, title):
        # 根据key查询数据
        # 根据col2和col3查询数据
        if (type, title) in self.data:
            return self.data[(type, title)]
        else:
            return set()

    def query_by_index(self, type, title, index):
        alias = []
        if (type, title) in self.data:
            target_list = self.data[(type, title)]
            for each in target_list:
                if each[4] == index:
                    alias.append(each)
        return alias

    # 从CSV文件中读取数据
    def read_data_from_csv(self, filename):
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=global_delimiter)
            for row in reader:
                if len(row) >= 3:
                    self.add_data(row[-1], row[1], row[0], row[2], row[3], row[4], row[5])


class RESchema:
    def __init__(self, filename="../meta/schemas.csv"):
        # 初始化一个字典来存储数据
        self.data = {}
        self.read_data_from_csv(filename)

    def add_data(self, key, col2, col3):
        # 添加数据到字典
        if key not in self.data:
            self.data[key] = []
        self.data[key].append((col2, col3))

    def query(self, key):
        # 根据key查询数据,返回一个set
        types = set()
        pairs = set()
        if key in self.data:
            for pair in self.data[key]:
                types.add(pair[0])
                types.add(pair[1])
                pairs.add(pair)
            return types, pairs
        else:
            return None, pairs

    # 从CSV文件中读取数据
    def read_data_from_csv(self, filename="../meta/schemas.csv"):
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.add_data(row[0], row[1], row[2])


class Entity:
    def __init__(self, name, pos, sent_id, type, global_pos=None, index=''):
        self.name = name
        self.pos = pos
        self.sent_id = sent_id
        self.type = type
        self.global_pos = global_pos
        self.index = index
        self.flag= -1


class Relation:
    def __init__(self, r, h, t, evidence):
        self.r = r
        self.h = h
        self.t = t
        self.evidence = evidence

    def getTriple(self):
        return self.h, self.r, self.t

    def getTripleWithEvidence(self):
        return self.h, self.r, self.t, self.evidence


def get_json_file(dir):
    with open(dir, 'r', encoding="UTF-8") as f:
        info = json.load(f)
        # 获取所有的键和值
    return info


def get_relation_info(dir):
    relations_json = get_json_file(dir)
    relations_value = []
    for one in relations_json:
        relations_value.append(relations_json[one])
    return relations_value


def getAllRelationSchema(documents):
    relation_schema = []
    for document in documents:
        relation_schema += document.get_relation_schema()
    return set(relation_schema)


def getUniqueEntityTypeList(documents):
    entityTypeList = []
    for document in documents:
        # 获取每个文档的实体类型，并将其转换为元组
        # 将元组添加到集合中去重
        entityTypeList += document.get_entity_type()
    return set(entityTypeList)


def convert_ner_to_csv(documents, csv_file_name):
    with open(csv_file_name, 'w', newline='', encoding='UTF-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=global_delimiter)
        for document in documents:
            # 打印所有实体
            for vertex in document.vertexSet:
                if isinstance(vertex, list):
                    for entity in vertex:
                        index = entity.index
                        if '_' in index:
                            index = entity.index.split('_')[0]
                        entity.name, entity.pos = revise_ner(entity.name, entity.pos)
                        row = [entity.name, entity.type, entity.sent_id, entity.pos, index, '_', '_', '_', '_', '_', '_', '_',
                               '_', document.title]
                        csv_writer.writerow(row)
                else:
                    for entity in document.vertexSet[vertex]:
                        index = entity.index
                        entity.name, entity.pos = revise_ner(entity.name, entity.pos)
                        row = [entity.name, entity.type, entity.sent_id, entity.pos, index, '_', '_', '_', '_', '_', '_', '_',
                               '_', document.title]
                        csv_writer.writerow(row)


def convert_re_to_csv(documents, csv_file_name, target_relations_fitler):
    with open(csv_file_name, 'w', newline='', encoding='UTF-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=global_delimiter)
        for document in documents:
            # 打印所有关系
            for relation in document.get_relations():
                if relation[6] in target_relations_fitler:
                    relation.append(document.title)
                    csv_writer.writerow(relation)



def get_label_map():
    filename = "../meta/label_map.csv"
    map = {}
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            map[row[0]] = row[1]
    return map


def read_csv(file_path):
    return pd.read_csv(file_path, delimiter=global_delimiter, header=None)


def skip_ner_check(item):
    if '|' not in item:
        return True
    if any(word in item.lower() for word in
               ['note', 'since', 'exclude', 'none', 'excluding', 'zip', 'please ', 'about ']):
        return True
    return False


class DataHandler:
    def __init__(self, datasource):
        self.datasource = datasource
        templates = PromptTemplate(datasource)
        self.target_relations = templates.get_re_relation_answer_names()
        self.relation_dict = get_json_file(meta_rel_info_dir)

    @abstractmethod
    def get_documents(self, dir):
        pass

    def summary(self, dir, summary_dir):
        """
        统计
        """
        with open(summary_dir, 'w', encoding="UTF-8") as f:
            documents, _ = self.get_documents(dir)
            f.write(f"document:{len(documents)}\n")
            relation_dict = {}
            for doc in documents:
                for relation in doc.relations:
                    h, r, t, e = relation.getTripleWithEvidence()
                    if r not in relation_dict:
                        relation_dict[r] = [0, 0]
                    relation_dict[r][0] += 1
                    if relation_dict[r][1] < len(e):
                        relation_dict[r][1] = len(e)

            f.write(f"relations:{len(relation_dict)}\n")
            f.write(f"relation,count,max evidence count\n")
            for key in relation_dict.keys():
                f.write(f"{key},{relation_dict[key][0]},{relation_dict[key][1]}\n")

    def process(self, extension=".json"):
        """
        convert from json to csv
        """
        dev_data_dir = f"../data/{self.datasource}/dev{extension}"
        sample_dev_data_dir = f"../data/{self.datasource}/sample_dev{extension}"
        test_data_dir = f"../data/{self.datasource}/test{extension}"
        summary_dev_dir = f"../data/{self.datasource}/summary_dev.txt"
        summary_test_dir = f"../data/{self.datasource}/summary_test.txt"

        patterns = set()
        if os.path.exists(sample_dev_data_dir):
            documents, _ = self.get_documents(sample_dev_data_dir)
            convert_ner_to_csv(documents, f"../data/{self.datasource}/sample_dev_ner.csv")
            convert_re_to_csv(documents, f"../data/{self.datasource}/sample_dev_re.csv", self.target_relations)
            patterns = getAllRelationSchema(documents)
        if os.path.exists(dev_data_dir):
            documents, _ = self.get_documents(dev_data_dir)
            convert_ner_to_csv(documents, f"../data/{self.datasource}/dev_ner.csv")
            convert_re_to_csv(documents, f"../data/{self.datasource}/dev_re.csv", self.target_relations)
            patterns = getAllRelationSchema(documents)
            self.summary(dev_data_dir, summary_dev_dir)
        if os.path.exists(test_data_dir):
            documents, _ = self.get_documents(test_data_dir)
            convert_ner_to_csv(documents, f"../data/{self.datasource}/test_ner.csv")
            convert_re_to_csv(documents, f"../data/{self.datasource}/test_re.csv", self.target_relations)
            patterns.update(getAllRelationSchema(documents))
            self.summary(test_data_dir, summary_test_dir)

        # 从documents中抽取schema
        sorted_patterns = sorted(list(patterns))
        schema_file_dir = f"../meta/schemas_{self.datasource}.csv"
        with open(schema_file_dir, 'w', newline='', encoding='utf-8') as file:
            # 将排序后的list写入CSV文件，每个元素作为一列
            for item in sorted_patterns:
                file.write(f"{item}\n")  # 注意这里使用[item]来创建一个单元素的list
