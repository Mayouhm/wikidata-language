import pandas as pd
import json
from pathlib import Path
import duckdb


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

    languages_codes = pd.concat([
        df[["language", "iso639_3"]]
          .rename(columns={"iso639_3": "code"}).assign(code_type="iso639_3"),
        df[["language", "glottolog"]]
          .rename(columns={"glottolog": "code"}).assign(code_type="glottolog"),
    ]).dropna(subset=["code"]).drop_duplicates()

    languages = df[["language", "languageLabel", "iso639_1", "links"]].drop_duplicates()
    return languages, languages_codes
def clean_countries(df):
    df["country"] = remove_link_qid(df["country"])
    return df
def clean_lang_countries(df, countries):
    df["language"] = remove_link_qid(df["language"])
    df["country"] = remove_link_qid(df["country"])
    df = df[df["country"].isin(countries["country"])]
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

dfs["languages"], dfs["languages_codes"] = clean_languages(dfs["languages"])
dfs["countries"] = clean_countries(dfs["countries"])
dfs["languages_countries"] = clean_lang_countries(dfs["languages_countries"], dfs["countries"])
dfs["languages_parents"] = clean_parents(dfs["languages_parents"])
dfs["languages_scripts"] = clean_scripts(dfs["languages_scripts"])
dfs["languages_speakers"] = clean_speakers(dfs["languages_speakers"])

# print(dfs["languages"])
# print(dfs["countries"])
# print(dfs["languages_countries"])
# print(dfs["languages_parents"])
# print(dfs["languages_scripts"])
# print(dfs["languages_speakers"])


con = duckdb.connect("data/languages.duckdb")
for name, df in dfs.items():
    con.register("temp", df)
    con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM temp")
    con.unregister("temp")

print("check")
assert dfs["languages"]["language"].is_unique
print("check")

# lc = dfs["languages_countries"]
# known = set(dfs["countries"]["country"])
# missing = lc[~lc["country"].isin(known)]
# print(missing.drop_duplicates("country"))
