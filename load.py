import pandas as pd
import json
from pathlib import Path
from collections import OrderedDict
# from load import lang_data, countries_data, lang_countries_data, lang_parents_data, lang_scripts_data, lang_speakers_data

def load_to_dataframe(file_name):
    data = json.loads(Path(f"data/raw/{file_name}").read_text(encoding="utf-8"))
    langs = []
    for item in data['results']['bindings']:
        langs.append({var: cell["value"] for var, cell in item.items()})
    return pd.DataFrame(langs)


for file_name in ["languages.json", "countries.json", "languages_countries.json", 
             "languages_parents.json", "languages_scripts.json", "languages_speakers.json"]:
    df = load_to_dataframe(file_name)
    print(df)

