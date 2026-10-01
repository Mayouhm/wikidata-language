import requests
from pathlib import Path


url = 'https://query.wikidata.org/sparql'
def make_query(queryName):
    query = queryName + ".rq"
    def get_sparql_query(filename, **kwargs):
        with open(f"queries/{filename}", 'r') as file:
            query = file.read()
        return query
    r = requests.get(url, params = {'format': 'json', 'query': get_sparql_query(query)}, 
                    headers={"User-Agent": "InfoLabWikiDataLang/1.0 (contact: hamzamayou04@gmail.com)"})
    print("Status:", r.status_code)
    print("Content-Type:", r.headers.get("Content-Type"))
    print("Response:", r.text[:1000])

    r.raise_for_status()
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    with open(f"data/raw/{queryName}.json", "w", encoding="utf-8") as f:
        f.write(r.text)
    return r.json()


lang_data = make_query("languages")
countries_data = make_query("countries")
lang_countries_data = make_query("languages_countries")
lang_parents_data = make_query("languages_parents")
lang_scripts_data = make_query("languages_scripts")
lang_speakers_data = make_query("languages_speakers")

