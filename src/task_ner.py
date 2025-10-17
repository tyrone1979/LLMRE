from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from task import Task, query
from relation import synonym, hypernyms
from data import revise_ner, revise_type, skip_ner_check, read_csv, get_include_ner
import re


def append_to_ner_data(type, sent_id, word, index, one, ner_data):
    same_index = index
    if type not in ner_data:
        ner_data[type] = {}
    word_lowcase = word.lower()
    if word_lowcase not in ner_data[type]:
        ner_data[type][word_lowcase] = []
    else:
        same_index = ner_data[type][word_lowcase][0]['index']
    ner_data[type][word_lowcase].append(
        {'entity': word, 'type': type, 'sent_id': sent_id, 'pos': one, 'index': same_index,
         'flag': -1})
    return ner_data


def ner_from_include(sentence_terms, **kwargs):
    ner_data = kwargs['ner_data']
    sent_id = kwargs['sent_id']
    index = kwargs['index']
    include_ner_pd = kwargs['include_ner_pd']
    for term in list(zip(include_ner_pd[0], include_ner_pd[1].str.lower())):
        word = term[1].strip()
        type = term[0]
        if word =='2-Amino-1-methyl-6-phenylimidazo [4, 5-b] pyridine'.lower():
            pass
        pos = compute_pos(word, sentence_terms)
        if len(pos) == 0:
            continue
        for one in pos:
            append_to_ner_data(type, sent_id, word, index, one, ner_data)
            index += 1
    return ner_data, index


def split_and_keep_delimiters(s):
    """
    使用一组分隔符分割字符串，并保留分隔符，同时去除空字符串

    :param s: 输入字符串
    :param delimiters: 分隔符列表
    :return: 分割后的列表
    """
    if s == 'as(2)o(3))' or s == 'as(2)o(3)':
        pass
    # 创建一个正则表达式模式，包含所有分隔符
    delimiters = [',', '.', '(', ')', ':', '-', '[', ']', '?', '/', '"', '+', '\\', '!', ';', '|', '\'']
    pattern = '|'.join(map(re.escape, delimiters))

    # 使用正则表达式分割字符串，并保留分隔符
    result = re.split(f'({pattern})', s)

    # 过滤掉空字符串
    result = [item.strip() for item in result if item != ' ' and item != '']

    return result


def compute_pos(phrase, sentence_terms):
    pos = set()
    phrase = split_and_keep_delimiters(phrase)

    search_terms = []
    for term in phrase:
        search_terms += term.split(' ')
    search_terms_lower = [term.lower() for term in search_terms]
    sentence_terms_lower = [term.lower() for term in sentence_terms]
    i = 0
    while i < len(sentence_terms_lower) - len(search_terms_lower) + 1:  # 确保有足够的空间来匹配整个search_terms
        # 检查当前位置的子列表是否与search_terms匹配
        if sentence_terms_lower[i:i + len(search_terms_lower)] == search_terms_lower:
            pos.add((i, i + len(search_terms_lower)))  # 添加匹配的索引对
        i += 1
    return pos


class ONENER:
    def __init__(self):
        pd = read_csv("../meta/skip.csv")
        self.skip_ner_list = list(zip(pd[0], pd[1].str.lower()))
        self.include_ner_pd = get_include_ner()

    def get_include_and_skip(self, document):
        include = {}
        skip = {}
        for sent_id, sentence in enumerate(document.doc):
            for term in list(zip(self.include_ner_pd[0], self.include_ner_pd[1].str.lower())):
                word = term[1].strip()
                type = term[0]
                pos = compute_pos(word, document.sents[sent_id])
                if len(pos) > 0:
                    if type not in include:
                        include[type] = set()
                    include[type].add(word)

            for (type, word) in self.skip_ner_list:
                pos = compute_pos(word, document.sents[sent_id])
                if len(pos) > 0:
                    if type not in skip:
                        skip[type] = set()
                    skip[type].add(word)
        return include, skip

    def get_entity_pos(self, name, document):
        result = []
        for sent_id, sentence in enumerate(document.doc):
            pos = compute_pos(name, document.sents[sent_id])
            for one in pos:
                result.append((sent_id, one))
        return result


class NER(Task):
    def __init__(self, model, data_handler):
        super().__init__(model, data_handler, task='NER')
        self.chain = ChatPromptTemplate.from_template(
            self.templates.get_template("NER")) | model.llm | StrOutputParser()
        self.alias = synonym(model, data_handler)
        self.hypernyms = hypernyms(model, data_handler)
        pd = read_csv(f"../meta/skip_{data_handler.datasource}.csv")
        self.skip_ner_list = list(zip(pd[0], pd[1].str.lower()))
        self.include_ner_pd = get_include_ner(data_handler.datasource)

    def process(self, **kwargs):
        result_dir = kwargs['result_dir']
        document = kwargs['document']
        descs = self.templates.get_ner_types()

        title = document.title
        ner_data = {}
        csv_data = []
        if title=='6293644':
            pass
        # NER
        for desc in descs:
            ner_queries = []
            index = 0
            for sentence in document.doc:
                desc = str(desc).replace('{', '').replace('}', '')
                ner_queries.append({"input": sentence, "type": desc})
            responses = query(self.chain, ner_queries)
            for sent_id, response in enumerate(responses):
                ner_data, index = ner_from_include(document.sents[sent_id], ner_data=ner_data, index=index,
                                                   include_ner_pd=self.include_ner_pd, sent_id=sent_id)
                for line in response.split('\n'):
                    if skip_ner_check(line):
                        continue
                    pair = line.split('|')
                    type = pair[0].strip()
                    word, _ = revise_ner(pair[1])
                    if (type, word.lower()) in self.skip_ner_list:
                        continue
                    if type in ner_data and word in ner_data[type]:
                        # exist in ner_data already
                        continue
                    pos = compute_pos(word, document.sents[sent_id])
                    if len(pos) == 0:
                        continue
                    for one in pos:
                        type = revise_type(word, type)
                        ner_data = append_to_ner_data(type, sent_id, word, index, one, ner_data)
                        index += 1
        ner_data = self.alias.process(entities=ner_data, document=document)
        ner_data = self.hypernyms.process(entities=ner_data, document=document)

        for type in ner_data:
            for word in ner_data[type]:
                for one in ner_data[type][word]:
                    csv_data.append(
                        f"{word}|{type}|{one['sent_id']}|[{one['pos'][0]}, {one['pos'][1]}]|{one['index']}|{one['flag']}|_|_|_|_|_|_|_|{title}\n")
        self.save(result_dir, csv_data)

    def save(self, output, csv_data, *args):
        """
        save result
        """
        with open(output, 'a', encoding='utf-8') as f:
            for row in csv_data:
                f.write(row)


if __name__ == '__main__':
    phrase = "it's a L-POCA/bize pain"
    ners = ner_from_include(phrase)
    print(ners)
