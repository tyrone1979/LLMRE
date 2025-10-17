from data import get_json_file, meta_rel_info_dir, Relation, Entity, DataHandler,revise_ner,PromptTemplate


class DocRED:
    """
    The data class for DocRED dataset
    """

    def __init__(self, vertexSet, labels, title, sents):
        self.vertexSet = [self._create_entities(vertices) for vertices in vertexSet]
        self.relations = [Relation(**label) for label in labels]
        self.title = title.lower()
        self.sents = sents
        self.doc = []
        self.relation_dict = get_json_file(meta_rel_info_dir)
        for sent in self.sents:
            self.doc.append(' '.join(sent))

    def _create_entities(self, vertices):
        # 假设每个顶点都是一个包含字典的列表，我们将创建一个Entity对象列表
        return [Entity(**vertex) for vertex in vertices if isinstance(vertex, dict)]

    def get_relations(self):
        relations = []
        for relation in self.relations:
            h, r, t, e = relation.getTripleWithEvidence()
            for head in self.vertexSet[h]:
                for tail in self.vertexSet[t]:
                    head_index=head.index.split('_')[0]
                    tail_index=tail.index.split('_')[0]

                    head.name,head.pos=revise_ner(head.name,head.pos)
                    tail.name,tail.pos=revise_ner(tail.name,tail.pos)
                    relations.append(
                        [head.name, head.type, head.sent_id,head.pos,head_index,head.flag,self.relation_dict[r], tail.name,tail.type,tail.sent_id,tail.pos,tail_index, tail.flag])

        return list(relations)

    def print_relation(self):
        for relation in self.relations:
            h, r, t = relation.getTriple()
            print(','.join([self.relation_dict[r], self.vertexSet[h][0].name, self.vertexSet[t][0].name]))

    def print_entity(self):
        for vertex in self.vertexSet:
            for entity in vertex:
                print(entity.name, entity.pos, entity.sent_id, entity.type)

    def get_entity_type(self):
        entityType = []
        for vertex in self.vertexSet:
            for entity in vertex:
                entityType.append(entity.type)
        return entityType

    def get_relation_schema(self):
        relations = []
        for relation in self.relations:
            h, r, t = relation.getTriple()
            relations.append(self.relation_dict[r] + ',' + self.vertexSet[h][0].type + ',' + self.vertexSet[t][0].type)
        return relations


class ReDocRED(DocRED):
    """
    The data class for Redocred dataset
    """

    def __init__(self, title, vertexSet, labels, sents):
        super().__init__(vertexSet, labels, title, sents)


class ReDocREDHandler(DataHandler):
    def __init__(self, datasource):
        super().__init__(datasource)


    def get_documents(self, dir):
        documents = []
        data_list = get_json_file(dir)
        # 创建Document对象
        for data in data_list:
            documents.append(ReDocRED(**data))
        doc_dict = {}
        for document in documents:
            if document.title not in doc_dict:
                doc_dict[document.title] = []
            doc_dict[document.title] = "".join(document.doc)
        return documents, doc_dict


class DocREDHandler(DataHandler):
    def __init__(self, datasource):
        super().__init__(datasource)
    def get_documents(self, dir):
        documents = []
        data_list = get_json_file(dir)
        # 创建Document对象
        for data in data_list:
            documents.append(DocRED(**data))
        doc_dict = {}
        for document in documents:
            if document.title not in doc_dict:
                doc_dict[document.title] = []
            doc_dict[document.title] = "".join(document.doc)
        return documents, doc_dict


if __name__ == '__main__':
    # process("docred")
    #doc = DocREDHandler("docred")
    doc=ReDocREDHandler("redocred")
    doc.process()
    #doc.process()

