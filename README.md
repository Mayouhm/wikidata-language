# Wikidata project for InfoLab
Welcome!
### What I built?
I built a dashboard that displays data from WikiData about languages. The audience I had in mind would be editors for WikiMedia projects, for example Wikipedia or Wikidata itself. The purpose I had in mind was to help these editors identify gaps in information in this space.

### The data
The data I used was from [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page). Wikidata is a free and open knowledge base. While this choice was suggested by Claude AI, I went with it due to me being a regular Wikipedia editor. I chose data on languages as I believed this would be reasonable to work with and would allow for a lot of information to be derived. It was also somewhat linked to my interest in history and world cultures.

### How it works?
To begin, I used a tutorial called "[Where do Mayors Come From: Querying Wikidata with Python and SPARQL](https://janakiev.com/blog/wikidata-mayors/)" by Nikolai Janakiev. This introduced me to using queries from WikiData and SparkQL. 


In order to get the data from Wikidata, I used their [query page](https://query.wikidata.org/) and I made SparkQL queries to get data for a number of things that I considered relevant. Using the above tutorial, I made JSON files for each of the queries I made. Part of the code written was assisted with a tutorial called "[How to use SQL files in Python code](https://mlquantdev.github.io/2023-05-03-use-sql-in-python/)".


In the next step, I cleaned the data using Pandas. I flattened the JSON files, removed null entries, removed links and converted things to the appropriate data type. I also wrote these to DuckDB and I used DuckDB to help verify the quality of the data. Some decisions were made here. For example, in the year column for the speakers table I removed timestamped data and only had the years. This was for consistency as some entries only had a year. Furthermore, this made logical sense as these timestamps were set to the first of January and only the year part was important.


Finally, I created the dashboard and there I presented the data in various formats. For the interactive map of official languages, I used a modified version of code I written for a past project to set things up. I also optimised that code and made it more appropriate for this project. I added things presenting statistics and tables of information I wanted to show and I added a search feature to allow a user to search any language they wanted.

### How to run it?
In terminal:
```
git clone https://github.com/Mayouhm/wikidata-language.git
python -m venv .venv
.venv\Scripts\activate      (Windows)   or   source .venv/bin/activate
pip install -r requirements.txt
python fetch.py
python load.py
python checks.py
streamlit run app.py
```
### What I would do next?
I would probably add more tools to the dashboard. Perhaps, for example, a way to see the "tree" of a language. However, I would have to modify the queries to include things like language groups. To make this more useful for users, I would add a way to go to Wikidata entries when people search up a language of their choosing. Furthermore, a language search randomiser to help users find more hidden languages. This randomiser could have filters so that languages with less information could be identified.
### Things I used to guide me
https://janakiev.com/blog/wikidata-mayors/
https://mlquantdev.github.io/2023-05-03-use-sql-in-python/
https://folium.streamlit.app/

#### AI use?
I used AI to help me in brainstorming for ideas for the entire project and for assisting me with errors as well as helping me write SQL queries when I found some trouble.