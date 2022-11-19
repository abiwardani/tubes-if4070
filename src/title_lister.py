from os import listdir
import json

dataset_path = "../data/embedded_qa/"

data_list = []
title_list = []
for data_path in listdir(dataset_path):
    if data_path.endswith(".json"):
        title_path = dataset_path + data_path
        f = open(title_path, "r")
        qa_data = json.load(f)
        f.close()

        title = qa_data["title"]
        title_list.append(title)

title_dict = {"titles": title_list}

with open("../data/title_list.json", "w") as outfile:
    json.dump(title_dict, outfile)