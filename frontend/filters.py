from h2o_wave import main, app, Q, ui
import pandas as pd

# filter for table
# assume a pd df is obtained
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})

headings = df.columns.tolist()

# load df to table rows
def df_to_rows(df:pd.DataFrame):
    return [ui.table_row(row[name] for name in headings) for id, row in df.iterrows()]

# filter df based on choice
def filter_df (df:pd.DataFrame, term:str):
    str_cols = df.select_dtypes(include=[object])
    return df[str_cols.apply(lambda column: column.str.contains(
        term, case=False, na=False)).any(axis=1)]