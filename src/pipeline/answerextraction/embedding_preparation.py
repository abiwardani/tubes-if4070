import pickle
import json
from clean_filename import clean_filename

with open('models/sim-model.pkl', 'rb') as filehandler:
    model = pickle.load(filehandler)

f = open("../../../data/qa_data.json", "r")
qa_data = json.load(f)
f.close()

for topics in qa_data["data"]:
    for qa in topics["qas"]:
        qa["embed"] = model.encode(qa["question"]).tolist()
    print(".", end="")

    with open("../../../data/embedded_qa/"+clean_filename(topics["title"])+".json", "w") as outfile:
        json.dump(topics, outfile)