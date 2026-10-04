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
def query(sql):
    return get_database_connection().execute(sql).df()

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

# the interactive map
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

st.write("Below is a map showing official languages by country.")

language_map = build_map(country_sql)
st_folium(language_map , height=500, use_container_width=True, returned_objects=[])
html = language_map.get_root().render()

# Below shows the tables we got through WikiData which were cleaned in part via Pandas with the help of DuckDB
table_names = ["languages", "languages_codes", "countries", "languages_countries", 
             "languages_parents", "languages_scripts", "languages_speakers"]
dfs = {}
with st.expander("Browse the database tables"):
    for table_name in table_names:
        dfs[table_name] = query(f"SELECT * FROM {table_name}")
        st.write(f"{len(dfs[table_name]):,} {table_name}")
        st.dataframe(dfs[table_name])
    
script_count_query = query("""
    SELECT
        (SELECT COUNT(*) FROM languages)                      AS total,
        (SELECT COUNT(DISTINCT language) FROM languages_scripts) AS with_script
""")

total = int(script_count_query.loc[0, "total"])
with_script = int(script_count_query.loc[0, "with_script"])
pct = 100 * with_script / total

st.metric("Languages with a recorded writing system", f"{pct:.1f}%")
st.caption(f"{with_script:,} of {total:,} languages have at least one script in Wikidata")