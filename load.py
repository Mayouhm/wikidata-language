import pandas as pd
import json
from pathlib import Path
from collections import OrderedDict

def load_to_dataframe(file_name):
    data = json.loads(Path(f"data/raw/{file_name}").read_text(encoding="utf-8"))
    langs = []
    for item in data['results']['bindings']:
        langs.append({var: cell["value"] for var, cell in item.items()})
    return pd.DataFrame(langs)


file_names = ["languages", "countries", "languages_countries", 
             "languages_parents", "languages_scripts", "languages_speakers"]
dfs = {}
for file_name in file_names:
    dfs[file_name] = load_to_dataframe(f"{file_name}.json")

def clean_languages(df):
    df["language"] = remove_link_qid(df["language"])
    df['links'] = pd.to_numeric(df['links']).astype("Int64")
    return df
def clean_countries(df):
    df["country"] = remove_link_qid(df["country"])
    return df
def clean_lang_countries(df):
    df["language"] = remove_link_qid(df["language"])
    df["country"] = remove_link_qid(df["country"])
    return df[["language", "country"]].drop_duplicates()
def clean_parents(df):
    df["language"] = remove_link_qid(df["language"])
    df["parent"] = remove_link_qid(df["parent"])
    return df[["language", "parent", "parentLabel"]].drop_duplicates()
def clean_scripts(df):
    df["language"] = remove_link_qid(df["language"])
    df["script"] = remove_link_qid(df["script"])
    return df[["language", "script", "scriptLabel"]].drop_duplicates()
def clean_speakers(df):
    df["language"] = remove_link_qid(df["language"])
    df['speakers'] = pd.to_numeric(df['speakers'], errors="coerce").round().astype("Int64")
    df["year"] = pd.to_numeric(df["year"].astype(str).
                               str.extract(r"^(\d{4})")[0],  errors="coerce").astype("Int64")
    df = df.dropna(subset=["speakers"])
    return df[["language", "speakers", "year"]].drop_duplicates()

def remove_link_qid(series):
    return series.str.extract(r"(Q\d+)$", expand=False)

dfs["languages"] = clean_languages(dfs["languages"])
print(dfs["languages"])
dfs["countries"] = clean_countries(dfs["countries"])
print(dfs["countries"])
dfs["languages_countries"] = clean_lang_countries(dfs["languages_countries"])
print(dfs["languages_countries"])
dfs["languages_parents"] = clean_parents(dfs["languages_parents"])
print(dfs["languages_parents"])
dfs["languages_scripts"] = clean_scripts(dfs["languages_scripts"])
print(dfs["languages_scripts"])
dfs["languages_speakers"] = clean_speakers(dfs["languages_speakers"])
print(dfs["languages_speakers"])