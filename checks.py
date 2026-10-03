import duckdb

con = duckdb.connect("data/languages.duckdb", read_only=True)


# checks for duplicates
def duplicates(con, table, key_cols):
    key = ", ".join(key_cols)
    sql = f"""
        SELECT COUNT(*) FROM (
            SELECT {key} FROM {table}
            GROUP BY {key}
            HAVING COUNT(*) > 1
        )
    """
    return con.execute(sql).fetchone()[0]
dupe_keys = {
    "languages": ["language"],
    "countries": ["country"],
    "languages_countries": ["language", "country"],
    "languages_scripts": ["language", "script"],
    "languages_parents": ["language", "parent"],
    "languages_codes": ["language", "code_type", "code"],
    "languages_speakers": ["language", "speakers", "year"],
}
for table, cols in dupe_keys.items():
    print(f"{table}: {duplicates(con, table, cols)} duplicated keys")

print("")
# checks for orphans
def orphans(con, child, child_col, parent, parent_col):
    sql = f"""
        SELECT COUNT(*) FROM {child} c
        LEFT JOIN {parent} p ON p.{parent_col} = c.{child_col}
        WHERE p.{parent_col} IS NULL
    """
    return con.execute(sql).fetchone()[0]
orphan_links = [
    # (child table,          child column, parent table, parent column)
    ("languages_countries",  "language",   "languages",  "language"),
    ("languages_countries",  "country",    "countries",  "country"),
    ("languages_scripts",    "language",   "languages",  "language"),
    ("languages_speakers",   "language",   "languages",  "language"),
    ("languages_codes",      "language",   "languages",  "language"),
    ("languages_parents",    "language",   "languages",  "language"),
]
for child, child_col, parent, parent_col in orphan_links:
    n = orphans(con, child, child_col, parent, parent_col)
    print(f"{child}.{child_col} -> {parent}.{parent_col}: {n} orphans")