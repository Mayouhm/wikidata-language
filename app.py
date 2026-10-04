import streamlit as st
import pandas as pd
import duckdb
import json
import folium
from streamlit_folium import st_folium

@st.cache_resource
def get_database_connection():
    return duckdb.connect("data/languages.duckdb", read_only=True)

@st.cache_data
def query(sql, params=None):
    return get_database_connection().execute(sql,params).df()

@st.cache_data
def load_geojson():
    with open("data/world_countries.json", encoding="utf-8") as f:
        return json.load(f)


# THe structure was based off code from a past project
def round_coords(coords, nd=2):
    if isinstance(coords[0], (int, float)):
        return [round(c, nd) for c in coords]
    return [round_coords(c, nd) for c in coords]

@st.cache_data
def prepare_data(sql_query):
    stats = query(sql_query)
    lookup = stats.set_index("iso3")
    features = []
    for f in load_geojson()["features"]:
        iso = f["properties"]["ADM0_A3"]
        #South Sudan and Palestine ISO Code mismatch. Update the GeoJSON ISO-Code
        if iso == "SDS":
            iso = "SSD"
            f["properties"]["ADM0_A3"] = "SSD"
        elif iso == "PSX":
            iso = "PSE"
            f["properties"]["ADM0_A3"] = "PSE"
        if iso in lookup.index:
            n, langs = int(lookup.loc[iso, "n_languages"]), lookup.loc[iso, "languages"]
        else:
            n, langs = "No data", "No data"
        
        features.append({
            "type": "Feature",
            "geometry": {"type": f["geometry"]["type"],
                         "coordinates": round_coords(f["geometry"]["coordinates"])},
            "properties": {"NAME": f["properties"]["NAME"],
                           "ADM0_A3": iso,
                           "n_languages": n, "languages": langs},
        })
    return stats, {"type": "FeatureCollection", "features": features}

def build_map(sql_query):
    stats, geo = prepare_data(sql_query)

    m = folium.Map(location=(30, 10), zoom_start=2)

    choropleth = folium.Choropleth(
        geo_data=geo,
        data=stats,
        columns=["iso3", "n_languages"],
        key_on="feature.properties.ADM0_A3",
        fill_color="Blues",
        nan_fill_color="lightgrey",
        bins=[0, 1, 2, 4, int(stats["n_languages"].max()) + 1],
        legend_name="Official languages by country via Wikidata",
    ).add_to(m)
    choropleth.geojson.add_child(
       folium.GeoJsonTooltip(fields=["NAME", "n_languages"],
                             aliases=["Country:", "Official languages:"]))
    choropleth.geojson.add_child(
       folium.GeoJsonPopup(fields=["NAME", "n_languages", "languages"],
                           aliases=["Country:", "Count:", "Languages:"], 
                           max_height=250))
    return m

st.write("Hello to all who read this! This is the result of the work I was assigned to do. I used data about languages from WikiData.")
every_language_query = query("SELECT language, languageLabel FROM languages ORDER BY languageLabel")


# Below shows the tables we got through WikiData which were cleaned in part via Pandas with the help of DuckDB
table_names = ["languages", "languages_codes", "countries", "languages_countries", 
             "languages_parents", "languages_scripts", "languages_speakers"]
dfs = {}
with st.expander("Browse the database tables"):
    for table_name in table_names:
        dfs[table_name] = query(f"SELECT * FROM {table_name}")
        st.write(f"{len(dfs[table_name]):,} {table_name}")
        st.dataframe(dfs[table_name])

def generate_percentage(choice):
    count_query = query(f"""
        SELECT
            (SELECT COUNT(*) FROM languages)                      AS total,
            (SELECT COUNT(DISTINCT language) FROM languages_{choice}s) AS with_{choice}
    """)
    total = int(count_query.loc[0, "total"])
    with_choice = int(count_query.loc[0, f"with_{choice}"])
    percent = 100 * with_choice / total
    st.metric(f"Languages with a {choice}", f"{percent:.1f}%")
    st.caption(f"{with_choice:,} of {total:,} languages have at least one {choice} in Wikidata")
def generate_percentage_speakers():
    choice = "speaker"
    count_query = query(f"""
        SELECT
            (SELECT COUNT(*) FROM languages)                      AS total,
            (SELECT COUNT(DISTINCT language) FROM languages_{choice}s) AS with_{choice}
    """)
    total = int(count_query.loc[0, "total"])
    with_choice = int(count_query.loc[0, f"with_{choice}"])
    percent = 100 * with_choice / total
    st.metric(f"Languages with a speakers count", f"{percent:.1f}%")
    st.caption(f"{with_choice:,} of {total:,} languages have at least one speakers count in Wikidata")
def generate_percentage_country():
    choice = "countrie"
    count_query = query(f"""
        SELECT
            (SELECT COUNT(*) FROM languages)                      AS total,
            (SELECT COUNT(DISTINCT language) FROM languages_countries) AS with_{choice}
    """)
    total = int(count_query.loc[0, "total"])
    with_choice = int(count_query.loc[0, f"with_{choice}"])
    percent = 100 * with_choice / total
    st.metric(f"Languages with a speakers count", f"{percent:.1f}%")
    st.caption(f"{with_choice:,} of {total:,} languages have at least one speakers count in Wikidata")

st.write("The below percentages can tell us two things: the quality of data on wikidata and how many languages actually lack the features mentioned.")
generate_percentage("script")
generate_percentage("parent")
generate_percentage_speakers()


labels = dict(zip(every_language_query["language"], every_language_query["languageLabel"]))

choice = st.selectbox(
    "Search for a language",
    options=every_language_query["language"].tolist(),
    format_func=lambda qid: f"{labels[qid]} ({qid})",
    index=None,
    placeholder="Start typing, e.g. French, Arabic, Tapirapé ",
)

if choice:
    names = ["parent", "script"]
    for name in names:
        choice_query = query(
            f"""
            SELECT {name}Label AS {name}, {name} AS wikidata_id
            FROM languages_{name}s
            WHERE language = ?
            ORDER BY {name}Label
            """,
            (choice,),
        )
        st.write(f"**{labels[choice]}** has {len(choice_query)} recorded {name} group(s) in Wikidata.")
        if choice_query.empty:
            st.info(f"No {name}s are recorded for this language in Wikidata.")
        else:
            st.dataframe(choice_query, hide_index=True)


# Offical languages

st.header("Official Languages in Countries")
generate_percentage_country()

st.write("The table shows the most common official languages.")
top_languages = query("""
    SELECT
        l.languageLabel AS language,
        COUNT(*)        AS countries
    FROM languages_countries lc
    JOIN languages l ON l.language = lc.language
    GROUP BY l.language, l.languageLabel
    ORDER BY countries DESC, language
    LIMIT 10
""")
st.dataframe(top_languages, hide_index=True)

st.write("The below table shows the proportion of the number of languages by country.")
language_count_country = query("""
    WITH per_country AS (
        SELECT c.country, COUNT(lc.language) AS n
        FROM countries c
        LEFT JOIN languages_countries lc ON lc.country = c.country
        GROUP BY c.country
    )
    SELECT n AS languages_per_country, COUNT(*) AS countries
    FROM per_country
    GROUP BY n
    ORDER BY n
""")
st.dataframe(language_count_country, hide_index=True)
st.write("Below is a map showing official languages by country.")

country_sql = """
    SELECT
        c.iso3,
        c.countryLabel AS name,
        COUNT(lc.language) AS n_languages,
        COALESCE(string_agg(l.languageLabel, ', ' ORDER BY l.languageLabel), 'None recorded') AS languages
    FROM countries c
    LEFT JOIN languages_countries lc ON lc.country  = c.country
    LEFT JOIN languages l            ON l.language = lc.language
    WHERE c.iso3 IS NOT NULL
    GROUP BY c.iso3, c.countryLabel
"""

language_map = build_map(country_sql)
st_folium(language_map , height=500, use_container_width=True, returned_objects=[])
html = language_map.get_root().render()
st.caption("Note: For the GeoJSON, I used Natural Earth. I specifically used the British country perspective. Unfortunately, it is imperfect. For example, despite British recognition of Kosovo, it does not show up here on the map. This only affects the map.")
