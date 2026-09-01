import pandas as pd
df = pd.read_csv('pests_pesticides.csv')
def get_pest_info(pest_name):
    pest_name = str(pest_name).lower().strip()

    result = df.loc[
        df['Pest Name'].astype(str).str.lower().str.strip() == pest_name,
        'Crop':'Source'
    ]

    if result.empty:
        return None

    return result.iloc[0].to_dict()
