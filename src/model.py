from langchain_ollama import ChatOllama
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLAlchemyCache
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.orm import declarative_base


class LLMModel:
    """
    识别所有Entity
    """

    def __init__(self, llm_url, model_name, temperature, cache, datasource):
        self.llm = ChatOllama(base_url=llm_url,
                              model=model_name,
                              temperature=temperature,
                              num_predict=-1)
        if cache != 'nocache':
            engine = create_engine(cache)
            Base = declarative_base()

            class LLMCache(Base):
                __tablename__ = datasource
                id = Column(Integer, Sequence("cache_id"), primary_key=True)
                prompt = Column(String, nullable=False)
                llm = Column(String, nullable=False)
                idx = Column(Integer)
                response = Column(String)
                message = Column(String)
            #set_llm_cache(SQLiteCache(cache))
            set_llm_cache(SQLAlchemyCache(engine, LLMCache))


if __name__ == '__main__':
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from data_prompt_templates import PromptTemplate

    cache = "sqlite:///.cache.db"
    datasource = 'chemdisgene'
    model = LLMModel("http://172.17.19.238:11434", "llama3.1:70b-instruct-q8_0", 0, cache, datasource)
    name = 'chem_disease:therapeutic'
    template = PromptTemplate(datasource).get_template("RE")[name]
    print(template[0])
    chain = ChatPromptTemplate.from_template(template[0]) | model.llm | StrOutputParser()
    # template=PromptTemplate(datasource).get_template("NER")
    # chain = ChatPromptTemplate.from_template(template) | model.llm | StrOutputParser()
    descs = PromptTemplate(datasource).get_ner_types()
    queries = []
    # full_text="Ketanserin pretreatment reverses alfentanil-induced muscle rigidity.Systemic pretreatment with ketanserin, a relatively specific type-2 serotonin receptor antagonist, significantly attenuated the muscle rigidity produced in rats by the potent short-acting opiate agonist alfentanil. Following placement of subcutaneous electrodes in each animal's left gastrocnemius muscle, rigidity was assessed by analyzing root-mean-square electromyographic activity. Intraperitoneal ketanserin administration at doses of 0.63 and 2.5 mg/kg prevented the alfentanil-induced increase in electromyographic activity compared with animals pretreated with saline. Chlordiazepoxide at doses up to 10 mg/kg failed to significantly influence the rigidity produced by alfentanil. Despite the absence of rigidity, animals that received ketanserin (greater than 0.31 mg/kg i.p.) followed by alfentanil were motionless, flaccid, and less responsive to external stimuli than were animals receiving alfentanil alone. Rats that received ketanserin and alfentanil exhibited less rearing and exploratory behavior at the end of the 60-min recording period than did animals that received ketanserin alone. These results, in combination with previous work, suggest that muscle rigidity, a clinically relevant side-effect of parenteral narcotic administration, may be partly mediated via serotonergic pathways. Pretreatment with type-2 serotonin antagonists may be clinically useful in attenuating opiate-induced rigidity, although further studies will be necessary to assess the interaction of possibly enhanced CNS, cardiovascular, and respiratory depression."
    full_text = """
    Endometriotic inflammatory microenvironment induced by macrophages can be targeted by niclosamide . Endometriosis causes severe chronic pelvic pain and infertility. We have recently reported that niclosamide treatment reduces growth and progression of endometriosis-like lesions and inflammatory signaling (NF${\rm \small K}$B and STAT3) in a mouse model. In the present study, we examined further inhibitory mechanisms by which niclosamide affects endometriotic lesions using an endometriotic epithelial cell line, 12Z, and macrophages differentiated from a monocytic THP-1 cell line. Niclosamide dose dependently reduced 12Z viability, reduced STAT3 and NF${\rm \small K}$B activity, and increased both cleaved caspase-3 and cleaved PARP. To model the inflammatory microenvironment in endometriotic lesions, we exposed 12Z cells to macrophage conditioned media (CM). Macrophages were differentiated from THP-1 cells using 12-O-tetradecanoylphorbol-13-acetate as M0, and then M0 macrophages were polarized into M1 or M2 using LPS/IFNgamma or IL4/IL13, respectively. Conditioned media from M0, M1, or M2 cultures increased 12Z viability. This effect was blocked by niclosamide, and cell viability returned to that of CM from cells treated with niclosamide alone. To assess proteins targeted by niclosamide in 12Z cells, CM from 12Z cells cultured with M0, M1, or M2 with/without niclosamide were analyzed by cytokine/chemokine protein array kits. Conditioned media from M0, M1, and/or M2 stimulated the secretion of cytokines/chemokines from 12Z cells. Production of most of these secreted cytokines/chemokines in 12Z cells was inhibited by niclosamide. Knockdown of each gene in 12Z cells using siRNA resulted in reduced cell viability. These results indicate that niclosamide can inhibit the inflammatory factors in endometriotic epithelial cells stimulated by macrophages by targeting STAT3 and/or NF${\rm \small K}$B signaling.
    """
    head = 'niclosamide'
    tail = 'pain'
    type = 'Chemical'
    # queries.append({"input": full_text, "head": head, "tail": tail})
    desc = str(descs[0]).replace('{', '').replace('}', '')
    queries.append({"input": full_text, "type": type, "head": head, "tail": tail})
    responses = chain.batch(queries, {"max_concurrency": 16})
    print(responses)
    for response in responses:
        if response in template[1]:
            print(response)


