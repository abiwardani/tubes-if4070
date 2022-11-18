import json
from urllib.parse import unquote

f = open("../data/train.json", "r")
train_data = json.load(f)
f.close()

f = open("../data/dev.json", "r")
dev_data = json.load(f)
f.close()

new_data = {"data": []}
new_data_arr = []

all_data = train_data["data"] + dev_data["data"]
title_list = []

for topic_dict in all_data:
    title = unquote(topic_dict["title"]).replace("_", " ")
    print(title)
    
    if title not in title_list:
        title_list.append(title)

        new_topic_dict = {"title": title, "qas": []}
        qas = []

        for paragraph_dict in topic_dict["paragraphs"]:
            for qa in paragraph_dict["qas"]:
                question = qa["question"]
                answer = qa["answers"]

                if len(answer) == 0:
                    if "plausible_answers" in qa:
                        answer = qa["plausible_answers"]
                        if len(answer) != 0:
                            answer = answer[0]["text"]
                else:
                    answer = answer[0]["text"]
                
                if len(answer) != 0:
                    qas.append({"question": question, "answer": answer.replace("_", " ").replace("%27", "")})

        new_topic_dict["qas"] = qas
        new_data_arr.append(new_topic_dict)

new_data["data"] = new_data_arr

with open("../data/qa_data.json", "w") as outfile:
    json.dump(new_data, outfile)

title_dict = {"titles": title_list}

with open("../data/title_list.json", "w") as outfile:
    json.dump(title_dict, outfile)