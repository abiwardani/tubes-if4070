import pickle
import json
from clean_filename import clean_filename

with open('models/sim-model.pkl', 'rb') as filehandler:
    model = pickle.load(filehandler)

f = open("../../../data/title_list.json", "r")
title_data = json.load(f)
f.close()

new_dict = []

for title in title_data["titles"]:
    new_dict.append({"title": title, "embed": model.encode(title).tolist()})
    print(".", end="")

    with open("../../../data/embedded_titles/title_list.json", "w") as outfile:
        json.dump(new_dict, outfile)