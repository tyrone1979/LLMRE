# 📁 Project Code Structure
## 🔝 Root Directory

```
.
├── cdr/                     # CDR dataset files
├── chemdisgene/             # ChemDisGene dataset files
├── meta/                    # Metadata and configuration files
├── result/                  # Model inference and evaluation results
├── src/                     # Source code
├── README.md                # Project description
├── CODE_STRUCTURE.md        # Code structure description
├── README.txt               # Original README
└── LICENSE                  # License file
```

## 📊 Dataset Files

| File / Folder                 | Description                          |
| ----------------------------- | ------------------------------------ |
| `dev.txt`, `test.txt`         | Raw text data                        |
| `dev_ner.csv`, `test_ner.csv` | Named entity recognition annotations |
| `dev_re.csv`, `test_re.csv`   | Relation extraction annotations      |
| `summary_*.txt` / `.csv`      | Dataset statistics and summaries     |
| `*_relns.tsv`                 | Relation triples                     |

## 🗂 `meta/` — Metadata & Configuration

```
meta/
├── prompt_templates.json         # Prompt templates configuration
├── rel_info.json                 # Relation type definitions
├── schemas_cdr.csv               # CDR-specific schema definition
└── schemas_chemdisgene.csv       # ChemDisGene-specific schema definition
```

## 🧠 `src/` — Source Code Structure

```
src/
├── __init__.py

├── data.py                   # General data loading and preprocessing
├── data_cdr.py               # CDR dataset processing
├── data_chemdisgene.py       # ChemDisGene dataset processing
├── data_docred.py            # DocRED dataset support

├── data_prompt_templates.py  # Prompt building logic

├── datastats.py              # Dataset statistics

├── regex.py                  # Regex rules and text cleaning

├── relation.py               # Relation labels and triple definitions

├── model.py                  # Model wrapper (LLM / classifier interfaces)

├── task.py                   # Generic task framework
├── task_ner.py               # NER task implementation
├── task_re.py                # Relation extraction task implementation

├── en_core_web_sm-3.7.0.tar.gz  # Offline spaCy English model
├── requirements.txt         # Python dependencies
├── run.py                   # Main Python entry point
├── run.sh                   # Shell script to run experiments
```

