import pandas as pd

df = pd.read_csv("Pesticides.csv")

selected_classes = [
    "rice leaf roller",
    "rice leaf caterpillar",
    "asiatic rice borer",
    "yellow rice borer",
    "rice gall midge",
    "brown plant hopper",
    "white backed plant hopper",
    "rice water weevil",
    "english grain aphid",
    "bird cherry-oataphid",
    "wheat blossom midge",
    "wheat sawfly",
    "aphids",
    "army worm",
    "black cutworm",
    "flea beetle",
    "Thrips",
    "red spider",
    "corn borer",
    "grub"
]

df = df[df["Pest"].isin(selected_classes)]

def find_pesticides(pest_name):
    return df.loc[df["Pest"] == pest_name, 'Pesticides'].to_string(index=False).split(', ')

def get_pest_names():
    return selected_classes
