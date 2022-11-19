import json
import pandas as pd
from os import getcwd, listdir
from topicclassifier.utils import create_train_loader
from topicclassifier.model import DistilBERTCustomModel
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical


def load_train_data():
    dataset_path = "data/embedded_qa/"

    # load dataset
    data_list = []
    for data_path in listdir(dataset_path):
        if data_path.endswith(".json"):
            title_path = dataset_path + data_path
            f = open(title_path, "r")
            qa_data = json.load(f)
            f.close()

            title = qa_data["title"]
            for qa in qa_data["qas"]:
                data_list.append([title, qa["question"]])

    df = pd.DataFrame(data=data_list, columns=["title", "question"])

    # transform title to oneshot encoding
    titles = df["title"].unique()
    n_titles = len(titles)
    le = LabelEncoder()
    le.fit(titles)
    df["title"] = le.transform(df["title"])
    df["title"] = df["title"].apply(lambda x: to_categorical(x, n_titles))

    print(df.head(20))
    return df, le, n_titles


class pipeline():
    def __init__(self):
        self.models = []

    def train(self):
        # load train data
        df, le, n_titles = load_train_data()
        self.le = le
        training_loader, validation_loader = create_train_loader(df)

        # train topicclassifier model
        model = DistilBERTCustomModel(n_titles)
        model.fit(training_loader, validation_loader)
        self.models.append(model)

    def run(self, input_text):
        y_pred = self.models[0].predict(input_text)
        print(y_pred)


pipe = pipeline()
pipe.train()
pipe.run("What is Nintendo first console?")
