from data import get_json_file, meta_rel_info_dir, Relation, Entity, DataHandler
import spacy
from spacy.lang.en import English
import sqlite3
nlp = spacy.load("en_core_web_sm")

remove_chars = [',', '.', '(', ')',':','-','[',']','?','/','"','+','\\','!',';','|','\'']
#remove_chars = [',', '.', '(', ')',':','[',']','?','"','+','\\','!',';','|','\'']
def compute_pos(pos_start, pos_end, sentence_term_positions):
    pos_start_index=-1
    pos_end_index=-1
    for idx, token_position in enumerate(sentence_term_positions):
        if pos_start==token_position[0]: #or pos_start==token_position[0]+1:
            pos_start_index=idx
            break
    for idx, token_position in enumerate(sentence_term_positions):
        if idx>=pos_start_index and pos_end<=token_position[1]:
            #if pos_end==token_position[1] or pos_end==token_position[1]+1 or pos_end==token_position[1]-1:
                pos_end_index=idx
                break
    if pos_start_index==-1 and pos_end_index!=-1:  #such as CI in 2CI
        pos_start_index=pos_end_index
    return [pos_start_index,pos_end_index+1]

def convert_to_tokens(sents):
    token_positions=[]
    sentences_tokens = [sent.split() for sent in sents]
    for i, sentence_tokens in enumerate(sentences_tokens):
        for idx, token in enumerate(sentence_tokens):
            if any(char in token for char in remove_chars):
                result = []
                for char in token:
                    if char in remove_chars:
                        result.append(char)  # 如果是短横线，直接添加到结果列表中
                    else:
                        # 如果不是短横线，检查列表是否为空
                        if len(result) == 0 or result[-1] in remove_chars:
                            # 如果列表为空或者最后一个元素是短横线，添加新的单词
                            result.append(char)
                        else:
                            # 如果列表不为空且最后一个元素不是短横线，将字符添加到列表的最后一个元素中
                            result[-1] += char
                sentence_tokens[idx] = result
                sentences_tokens[i] = [item for sublist in sentence_tokens for item in
                                       (sublist if isinstance(sublist, list) else [sublist])]
        positions = []
        start = 0
        for token in sentences_tokens[i]:
                # 找到token在sentence中的起始位置
                start = sents[i].find(token, start)
                if start==-1:
                    pass
                end = start + len(token)
                positions.append([start, end])
                start = end  # 更新下一次搜索的起始位置
        token_positions.append(positions)
    return sentences_tokens,token_positions


def convert_to_sentences(text):
    doc = nlp(text)
    # 获取分句结果
    sentences = [sent.text for sent in doc.sents]
    # 合并不符合规则的句子
    final_sentences = []
    i = 0
    while i < len(sentences):
        current_sentence = sentences[i]
        # 检查当前句子的最后一个字符是否为句号、问号或感叹号
        while not current_sentence.strip().endswith(('.', '?', '!')):
            # 如果不是，尝试将当前句子与下一个句子合并
            if i + 1 < len(sentences):
                if current_sentence.endswith(":"):
                    current_sentence += " "+sentences[i + 1]
                elif current_sentence.endswith(('/', '(', '[',' ')) or sentences[i + 1][0].startswith(('%','.',',')):
                    current_sentence += sentences[i + 1]
                else:
                    current_sentence += " " + sentences[i + 1]
                i += 1  # 跳过下一个句子
            else:
                break  # 如果没有下一个句子，退出循环
        final_sentences.append(current_sentence + " ")  # 在每个句子后面添加一个空格
        i += 1
    return final_sentences


class CDRData:
    def __init__(self):
        self.title = ""
        self.vertexSet = {}
        self.sents = []
        self.sents_token_positions=[]
        self.doc = []
        self.relations = []
        self.text = ''
        self.sentence_global_pos = {}
        self.relation_dict = get_json_file(meta_rel_info_dir)

    def get_relations(self):
        relations = []
        for relation in self.relations:
            if relation.h in self.vertexSet and relation.t in self.vertexSet:
                head_entities = self.vertexSet[relation.h]
                tail_entities = self.vertexSet[relation.t]
                for head_entity in head_entities:
                    for tail_entity in tail_entities:
                        relations.append([
                            head_entity.name, head_entity.type, head_entity.sent_id, head_entity.pos, head_entity.index, head_entity.flag,
                            self.relation_dict[relation.r],
                            tail_entity.name, tail_entity.type, tail_entity.sent_id, tail_entity.pos, tail_entity.index, tail_entity.flag
                        ])
        return relations

    def get_relation_schema(self):
        relation = []
        relation.append("impact,Chemical,Disease")
        return relation


class CDRHandler(DataHandler):
    """
    The data class for CDR dataset
    """

    def __init__(self, datasource):
        super().__init__(datasource)
        """
        self.conn=sqlite3.connect('disease_chemical.db')
        self.cursor=self.conn.cursor()
        # 创建表
        # 如果表已经存在，则不会创建新表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            id CHAR(7)  NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            alias_index INT
        )
        ''')
        """
        self.data = {}
    """
    def put_to_DB(self,entities):
        # 插入数据前检查是否存在
        for entity in entities:
            self.cursor.execute('SELECT * FROM entities WHERE id=? AND name=?', (entity[0], entity[1]))
            if self.cursor.fetchone():  # 如果查询结果不为空，表示记录已存在
                print(f"Entity with id {entity[0]} and name {entity[1]} already exists.")
            else:
                # 插入新的记录
                self.cursor.execute('INSERT INTO entities (id, name,type, alias_index) VALUES (?, ?, ?, ?)', entity)
        # 提交事务
        self.conn.commit()


    def close_db(self):
        # 关闭Cursor
        self.cursor.close()

        # 关闭Connection
        self.conn.close()
    """
    def parse_doc(self, lines):
        for line in lines:
            if '|t|' in line or '|a|' in line:
                parts = line.strip().split("|")
                record_id = parts[0]
                if not record_id in self.data.keys():
                    self.data[record_id] = CDRData()
                if parts[1] == 't':
                    self.data[record_id].title = record_id
                    self.data[record_id].text = parts[2]
                    self.data[record_id].doc = [parts[2]]
                    sentences_tokens,sentences_tokens_positions = convert_to_tokens([parts[2]])
                    self.data[record_id].sents = sentences_tokens
                    self.data[record_id].sents_token_positions=sentences_tokens_positions
                else:
                    self.data[record_id].text += parts[2]
                    sentences = convert_to_sentences(parts[2])
                    sentences_tokens,sentences_tokens_positions=convert_to_tokens(sentences)
                    self.data[record_id].doc += sentences
                    self.data[record_id].sents += sentences_tokens
                    self.data[record_id].sents_token_positions += sentences_tokens_positions

    def parse_relation(self, lines):
        for line in lines:
            if '\n' == line or '|t|' in line or '|a|' in line:
                continue
            parts = line.split("\t")
            record_id = parts[0]
            if parts[1] == 'CID':
                head_id = parts[2]
                tail_id = parts[3].replace("\n", "")
                self.data[record_id].relations.append(Relation('P3374', head_id, tail_id, ''))

    def find_sent(self, name, global_start, global_end, record_id):
        if self.data[record_id].text[global_start]!=name[0]:
            #ajust the position caused by space.
            global_start=global_start-1
            global_end=global_end-1
        sent_start = 0
        for idx, sentence in enumerate(self.data[record_id].doc):
            sent_end = sent_start + len(sentence) - 1
            if name in sentence:
                if global_start >= sent_start and global_end <= sent_end:
                    start_in_sent=global_start-sent_start
                    if sentence[start_in_sent]!=name[0]:
                        start_in_sent=start_in_sent-1
                    end_in_sent=global_end-sent_start
                    return idx, compute_pos(start_in_sent, end_in_sent,
                                            self.data[record_id].sents_token_positions[idx])
            sent_start = sent_end + 1
        return -1, []  #not found, alias name not appreared in the text

    def get_pos(self, name, sent_id, record_id):
        words = name.split()
        sentences = self.data[record_id].doc
        sents = self.data[record_id].sents
        pos = []
        for word in words:
            # 使用列表推导式找到单词在sents中的所有索引位置，并添加到pos列表中
            pos.extend([index for index, elem in enumerate(sents[sent_id]) if elem == word])

    def parse_entity(self, lines):
        index = 0
        for line in lines:
            if '\n' == line or '|t|' in line or '|a|' in line:
                continue
            parts = line.split("\t")
            record_id = parts[0]
            if parts[1] == 'CID':
                continue
            item_id = parts[5].replace("\n", "")
            item_ids = []
            item_names = []
            global_start = int(parts[1])
            global_end = int(parts[2])
            item_type = parts[4]
            if '|' in item_id:  #	D020225|D020227
                item_ids.append(item_id.split('|')[0])
            else:
                item_ids.append(item_id)
            item_names.append(parts[3])
            for item_name, item_id in zip(item_names, item_ids):
                sent_id, pos = self.find_sent(item_name, global_start, global_end, record_id)
                if sent_id==-1:
                    continue
                if item_id not in self.data[record_id].vertexSet:
                    self.data[record_id].vertexSet[item_id] = []
                    self.data[record_id].vertexSet[item_id].append(
                        Entity(item_name, pos, sent_id, item_type, [global_start, global_end],
                               str(index)))
                else:
                    i = self.data[record_id].vertexSet[item_id][0].index
                    self.data[record_id].vertexSet[item_id].append(
                        Entity(item_name, pos, sent_id, item_type, [global_start, global_end],
                               str(i)))
            index += 1

    def _read_from_file(self, file_path):
        self.data = {}
        with open(file_path, 'r', encoding='UTF-8') as file:
            lines = file.readlines()
            self.parse_doc(lines)
            self.parse_entity(lines)
            self.parse_relation(lines)

    def get_documents(self, dir):
        self._read_from_file(dir)
        documents = []
        for id in self.data.keys():
            documents.append(self.data[id])
        doc_dict = {}
        for document in documents:
            if document.title not in doc_dict:
                doc_dict[document.title] = []
            doc_dict[document.title] = document.text
        return documents, doc_dict


if __name__ == '__main__':
    # process("docred")
    doc = CDRHandler('cdr')
    doc.process('.txt')
