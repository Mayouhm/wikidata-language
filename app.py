import streamlit as st
import pandas as pd
import duckdb
import folium
from streamlit_folium import st_folium


@st.cache_resource
def get_database_connection():
    return duckdb.connect("data/languages.duckdb", read_only=True)

@st.cache_data
def query(sql):
    return get_database_connection().execute(sql).df()


# languages = query("SELECT * FROM languages")
# st.write(f"{len(languages):,} languages")
# st.dataframe(languages)

# countries = query("SELECT * FROM countries")
# st.write(f"{len(countries):,} countries")
# st.dataframe(countries)

table_names = ["languages", "languages_codes", "countries", "languages_countries", 
             "languages_parents", "languages_scripts", "languages_speakers"]
dfs = {}
for table_name in table_names:
    dfs[table_name] = query(f"SELECT * FROM {table_name}")
    st.write(f"{len(dfs[table_name]):,} {table_name}")
    st.dataframe(dfs[table_name])


m = folium.Map(location=(30, 10), zoom_start=2)
folium.Marker(
    [39.949610, -75.150282], popup="Liberty Bell", tooltip="Liberty Bell"
).add_to(m)
st_data = st_folium(m, width=725)
