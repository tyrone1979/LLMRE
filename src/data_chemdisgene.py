"""
Reading and Writing PubTator format files.
"""

from collections import defaultdict
import gzip
import os
import re
import sys
from typing import List, Optional, Set, TextIO, Tuple
from data_cdr import CDRHandler
from data import get_json_file, meta_rel_info_dir

# -----------------------------------------------------------------------------
#   Globals
# -----------------------------------------------------------------------------

# Includes support for non-numeric Document IDs, e.g. "Manoj_Ramachandran_1|t|Fully Automating Graf’s Method for ..."
TITLE_ABSTR_PATT = re.compile(r'([^|]+)\|([ta])\|')


# -----------------------------------------------------------------------------
#   Classes
# -----------------------------------------------------------------------------

class Relation:
    STDD_ARG_TYPES = {"chem": "Chemical",
                      "disease": "Disease",
                      "gene": "Gene"}

    def __init__(self, subj_eid: str, obj_eid: str, relation_label: str, from_ctd: bool = True):

        self.h = subj_eid
        self.t = obj_eid
        self.r = relation_label
        self.from_ctd = from_ctd

        # Derived Fields:

        # Relation label contains the arg entity types
        # Examples: "chem_gene:increases^expression", "chem_disease:marker/mechanism"
        subj_type, obj_type = relation_label.split(":")[0].split("_")
        self.subj_type = self.STDD_ARG_TYPES[subj_type]
        self.obj_type = self.STDD_ARG_TYPES[obj_type]

        return

    def get_subj_entity(self) -> Tuple[str, str]:
        return self.subj_type, self.h

    def get_obj_entity(self) -> Tuple[str, str]:
        return self.obj_type, self.t

    def get_pretty_relation_label(self):
        r_flds = self.r.split(":")[1].split("^")
        if len(r_flds) == 1:
            r_action, r_type = None, r_flds[0]
        else:
            r_action, r_type = r_flds[0], r_flds[1]

        if r_action:
            r_type += f" - {r_action}"

        return f"{self.subj_type}-{self.obj_type} : {r_type}"

    def write(self, docid, file: TextIO = sys.stdout):
        print(docid, self.r, self.h, self.t,
              sep="\t", file=file)

    def __str__(self):
        return "Relation(" + ", ".join([f"{fld} = {getattr(self, fld)}" for fld in self.__dict__]) + ")"

    def getTriple(self):
        return self.h, self.r, self.t

    def getTripleWithEvidence(self):
        return self.h, self.r, self.t, ''


# /


class Entity:
    """
    Each mention here is a contiguous substring of the document text:
        mention-text = doc.get_text()[ch_start : ch_end]
    Typically, each mention is for one Entity, uniquely specified by (Entity-Type, Entity-ID).
    Some mentions may be composite -- mention more than one entity -- as in "ovarian and peritoneal cancer".

    Some entity recognition models (e.g. Pubtator Central) will on occasion recognize the type of a mention
    without resolving it to a particular entity ID. In such cases, the Entity-ID will be null (empty) or "-".

    NOTE: Does not handle multiple values in `entity_type`
    """

    def __init__(self, ch_start: int, ch_end: int, mention: str, entity_type: str, entity_ids: Optional[str],
                 mention_id: str = None, composite_mentions: Optional[str] = None):
        self.ch_start = ch_start
        self.ch_end = ch_end
        self.name = mention
        self.type = entity_type
        self.pos = []
        self.sent_id = -1
        self.global_pos = [ch_start, ch_end]
        self.index = -1
        self.flag = -1

        if not entity_ids or entity_ids == "-":
            self.entity_ids = None
        else:
            self.entity_ids = re.split(r"[;|]", entity_ids)

        # When more than one ConceptID is assigned to mention
        # e.g.  mention = "ovarian and peritoneal cancer"
        #       concept_id = D010051|D010534
        #       Additional field composite_mentions = "ovarian cancer|peritoneal cancer"
        # where: D010051 = Ovarian Neoplasms, D010534 = Peritoneal Neoplasms
        self.is_composite = self.entity_ids is not None and len(self.entity_ids) > 1

        self.composite_mentions = composite_mentions.split("|") if composite_mentions else None

        self._from_title = False
        return

    @property
    def is_from_title(self):
        return self._from_title

    @is_from_title.setter
    def is_from_title(self, from_title: bool):
        self._from_title = from_title
        return

    def is_unresolved_mention(self):
        """
        Whether this mention is not resolved (not linked to any Entity IDs)
        """
        return self.entity_ids is None

    def get_entity_ids(self):
        if not self.entity_ids:
            return ["-"]
        else:
            return self.entity_ids

    def get_entities(self) -> List[Tuple[str, str]]:
        return [(self.type, eid) for eid in self.get_entity_ids()]

    def write(self, docid, file: TextIO = sys.stdout, composite_sep: str = "|"):
        """
        Output in PubTator format.
        Ignores `mention_id`.
        """
        print(docid, self.ch_start, self.ch_end, self.name, self.type,
              composite_sep.join(self.get_entity_ids()),
              sep="\t", end="", file=file)
        if self.composite_mentions:
            print("", "|".join(self.composite_mentions), sep="\t", end="", file=file)
        print(file=file)
        return

    def __str__(self):
        return "Entity(" + ", ".join([f"{fld} = {getattr(self, fld)}" for fld in self.__dict__]) + ")"

    @classmethod
    def from_pubtator_line(cls, flds: List[str]):
        """
        Relationship Fields in PubTator format:
            DocID, Char-Start-Index, Char-End-Index, Mention-text, Entity-Type, Entity-IDs [, Composite-Mentions ]
        where
            Entity-IDs = empty  ||  "-"  ||  Entity-ID [ SEP Entity-ID ]*
            Entity-ID = str
            SEP = "|"  ||  ";"
            Composite-Mentions = Mention [ "|" Mention ]*
            Mention = str

        Example of composite mentions:
            11752998	213	235	acute and chronic pain	Disease	D059787|D059350     acute pain|chronic pain

            Mention-text = acute and chronic pain
            Entity-IDs = D059787|D059350
            Composite-Mentions = acute pain|chronic pain
        """

        assert len(flds) in [5, 6, 7], \
            f"Incorrect number of fields for EntityMention (expected 5-7, got {len(flds)})"

        flds = [fld.strip() for fld in flds]

        docid, ch_start, ch_end, mention, ent_type = flds[:5]
        ent_id = None
        composite_mentions = None

        if len(flds) > 5:
            ent_id = flds[5]

        if len(flds) > 6 and flds[6]:
            composite_mentions = flds[6]

        ch_start = int(ch_start)
        ch_end = int(ch_end)

        ann = Entity(ch_start, ch_end, mention, ent_type, ent_id, composite_mentions)

        return ann, docid


# /


class ChemDisGeneData:
    def __init__(self, docid: str, title: Optional[str] = None, abstract: Optional[str] = None):
        super().__init__()
        self.docid = docid
        self.title: Optional[str] = title
        self.abstract: Optional[str] = abstract
        self.text = ''
        self.vertexSet = defaultdict(list)
        self.doc = []
        self.title_len = None
        self.relations: List[Relation] = []
        self.sents = []  # sentence
        self.sents_token_positions = []
        self.relation_dict = get_json_file(meta_rel_info_dir)

        # Dict: (entity_type: str, entity_id: str) => List[EntityMention]
        self._entity_mentions_dict = defaultdict(list)

        self._is_sorted = True
        return

    def get_title_length(self):
        if self.title is None:
            return 0
        elif self.title_len is None:
            self.title_len = len(self.title)

        return self.title_len

    def get_text(self, sep="\n"):
        if self.title and self.abstract:
            return self.title + sep + self.abstract
        elif self.title:
            return self.title
        else:
            return self.abstract

    def get_relation_schema(self):
        relations = []
        for relation in self.relations:
            h, r, t = relation.getTriple()
            relations.append(r + ',' + self.vertexSet[h][0].type + ',' + self.vertexSet[t][0].type)
        return relations

    def get_relations(self):
        relations = []
        for relation in self.relations:
            if relation.h in self.vertexSet and relation.t in self.vertexSet:
                head_entities = self.vertexSet[relation.h]
                tail_entities = self.vertexSet[relation.t]
                for head_entity in head_entities:
                    for tail_entity in tail_entities:
                        relations.append([
                            head_entity.name, head_entity.type, head_entity.sent_id, head_entity.pos, head_entity.index,
                            head_entity.flag,
                            relation.r,
                            tail_entity.name, tail_entity.type, tail_entity.sent_id, tail_entity.pos, tail_entity.index,
                            tail_entity.flag
                        ])
        return relations


# /

from data_cdr import convert_to_tokens, convert_to_sentences


class ChemDisGeneHandler(CDRHandler):
    def __init__(self, datasource):
        super().__init__(datasource)

    def read_docs_relns(self, pbtr_file: str, ctd_relns_file: str, new_relns_file: str = None):
        docs_dict = self.parse_pubtator(pbtr_file, ctd_relns_file)
        if new_relns_file:
            if new_relns_file.endswith(".gz"):
                with gzip.open(new_relns_file) as f:
                    self.parse_relationships_opened_file(f, from_ctd=False)
            else:
                with open(new_relns_file) as f:
                    self.parse_relationships_opened_file(f, from_ctd=False)
        return docs_dict

    def is_integral(self, txt: str):
        return all(c in "1234567890" for c in txt)

    def parse_pubtator(self, pbtr_file: str, relns_file: str = None, encoding: str = 'UTF-8'):
        """
        Parse a PubTator file and extract AnnotatedDocument's.
        Restrict to docids if `docids_file` provided, which contains one DOCID per file.
        Annotations are sorted on position in text.
        """
        if pbtr_file.endswith(".gz"):
            with gzip.open(os.path.expanduser(pbtr_file)) as f:
                docs = self.parse_pubtator_opened_file(f, encoding=encoding)
        else:
            with open(os.path.expanduser(pbtr_file), encoding=encoding) as f:
                docs = self.parse_pubtator_opened_file(f)

        if relns_file:
            if relns_file.endswith(".gz"):
                with gzip.open(os.path.expanduser(relns_file)) as f:
                    self.parse_relationships_opened_file(f, encoding=encoding)
            else:
                with open(os.path.expanduser(relns_file), encoding=encoding) as f:
                    self.parse_relationships_opened_file(f)
        return docs

    def parse_pubtator_opened_file(self, f, encoding: str = 'UTF-8'):
        curdoc = None
        lc = 0
        index = 0
        for line in f:
            lc += 1
            if isinstance(line, bytes):
                line = line.decode(encoding)

            line = line.strip()
            if line == '':
                continue

            m = TITLE_ABSTR_PATT.match(line)
            if m:
                docid = m.group(1)
                if docid not in self.data:
                    curdoc = ChemDisGeneData(docid)
                    self.data[docid] = curdoc
                    index = 0
                text = line[m.end(0):]
                if m.group(2) == 't':
                    curdoc = self.data[docid]
                    curdoc.title = docid
                    curdoc.doc = [text + ' ']
                    curdoc.text = text + ' '
                    sentences_tokens, sentences_tokens_positions = convert_to_tokens([text])
                    curdoc.sents = sentences_tokens
                    curdoc.sents_token_positions = sentences_tokens_positions
                else:
                    curdoc.abstract = text
                    curdoc.text += text
                    sentences = convert_to_sentences(text)
                    sentences_tokens, sentences_tokens_positions = convert_to_tokens(sentences)
                    curdoc.doc += sentences
                    curdoc.sents += sentences_tokens
                    curdoc.sents_token_positions += sentences_tokens_positions
            else:
                try:
                    self.add_annotation_pubtator(line, index)
                    index += 1
                except AssertionError as e:
                    print("Error while processing PubTator file")
                    print(e)
                    print(f"Line {lc}:", line)
                    print("Skipping entry ...\n")

        return self.data

    def parse_relationships_opened_file(self, f, encoding: str = 'UTF-8', from_ctd: bool = True):
        lc = 0
        for line in f:
            lc += 1
            if isinstance(line, bytes):
                line = line.decode(encoding)
            flds = line.strip().split("\t")
            try:
                self.add_relationship(flds, from_ctd=from_ctd)

            except Exception as e:
                print(f"Error at line {lc}: [{line.strip()}]")
                raise e

    def add_relationship(self, flds: List[str], from_ctd: bool = True):
        """
        Relationship Fields in ChemDisGen PubTator format:
            DocID, Relation-Label, Subj-Entity-ID, Obj-Entity-ID
        """
        assert len(flds) == 4, \
            f"Incorrect number of fields for BinaryRelationship (expected 4, got {len(flds)}), flds = {flds}"

        docid, reln, s_id, o_id = flds
        r = Relation(s_id, o_id, reln, from_ctd=from_ctd)
        self.data[docid].relations.append(r)

    def add_annotation_pubtator(self, pbtr_line: str,index: int):
        flds = pbtr_line.strip().split("\t")
        if len(flds) > 2:
            if self.is_integral(flds[1]):
                mention, docid = Entity.from_pubtator_line(flds)
                if mention.entity_ids is None:
                    return
                if docid == '30469162' and mention.entity_ids[0] == '1040':
                    pass
                sent_id, pos = self.find_sent(mention.name,
                                              mention.ch_start,
                                              mention.ch_end, docid)
                if sent_id == -1:
                    return
                mention.sent_id = sent_id
                mention.pos = pos

                for id in mention.entity_ids:
                    if id in self.data[docid].vertexSet:
                        mention.index=self.data[docid].vertexSet[id][0].index
                    else:
                        mention.index=index
                    self.data[docid].vertexSet[id].append(mention)
            else:
                self.add_relationship(flds)
        return

    def get_documents(self, dir):
        self.data = defaultdict(list)
        pbtr_file = dir
        name = dir.split('.txt')
        ctd_relns_file = f"{name[0]}_relns.tsv"
        ctd_relns_new_file = f"{name[0]}_relns_new.tsv"
        self.data = self.read_docs_relns(pbtr_file, ctd_relns_file, ctd_relns_new_file)
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
    # 首先，确保你已经下载了nltk的句子分割模型

    doc = ChemDisGeneHandler('chemdisgene')
    doc.process('.txt')
