import json


class PromptTemplate:
    def __init__(self, datasource, file_path="../meta/prompt_templates.json"):
        self.file_path = file_path
        self.data = {}
        self.load_template()
        self.datasource=datasource
        self.template_names = {
            "NER": self.get_ner_template,
            "RE": self.get_re_template,
            "ALIAS": self.get_alias_templates,
            "ONE": self.get_one_template
        }

    def load_template(self):
        """Load and parse the JSON file."""
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)

    def get_template(self, name):
        return self.template_names[name]()

    def get_one_template(self):
        """Get the RE template from the JSON data."""
        return self.data.get(self.datasource, {}).get('ONE', {}).get('template', [])
    def get_ner_template(self):
        """Get the NER template from the JSON data."""
        return self.data.get(self.datasource, {}).get('NER', {}).get('template', '')

    def get_ner_types(self):
        """Get the NER entity types and descriptions from the JSON data."""
        return self.data.get(self.datasource, {}).get('NER', {}).get('type', [])

    def get_re_template(self):
        """Get the RE template from the JSON data."""
        return self.data.get(self.datasource, {}).get('RE', {}).get('template')

    def get_re_relation_answer_names(self):
        templates= self.data.get(self.datasource, {}).get('RE', {}).get('template')
        names=[]
        for one in templates:
            for answer in templates[one]["answers"]:
                value=templates[one]["answers"][answer]
                if isinstance(value,list):
                    names+=value
        return list(set(names))

    def get_alias_templates(self):
        """Get the RE entity types and descriptions from the JSON data."""
        return self.data.get(self.datasource, {}).get('ALIAS', {})


