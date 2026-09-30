import requests


url = 'https://query.wikidata.org/sparql'

def get_sparql_query(filename, **kwargs):
    with open(f"queries/{filename}", 'r') as file:
        query = file.read()
    return query

r = requests.get(url, params = {'format': 'json', 'query': get_sparql_query("languages.rq")}, 
                 headers={"User-Agent": "InfoLabWikiDataLang/1.0 (contact: hamzamayou04@gmail.com)"})

print("Status:", r.status_code)
print("Content-Type:", r.headers.get("Content-Type"))
print("Response:", r.text[:1000])

r.raise_for_status()


data = r.json()
