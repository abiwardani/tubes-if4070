import pickle
import json

def clean_filename(text):
    res = text.lower()

    val_chars = "abcdefghijklmnopqrstuvwxyz0123456789_- "
    for char in text:
        if char not in val_chars:
            res = res.replace(char, "")
    
    return res.replace(" ", "_")

with open('models/sim-model.pkl', 'rb') as filehandler:
    model = pickle.load(filehandler)

f = open("../../data/qa_data.json", "r")
qa_data = json.load(f)
f.close()

for topics in qa_data["data"]:
    for qa in topics["qas"]:
        qa["embed"] = model.encode(qa["question"]).tolist()
    print(".", end="")

    with open("../../data/embedded_qa/"+clean_filename(topics["title"])+".json", "w") as outfile:
        json.dump(topics, outfile)