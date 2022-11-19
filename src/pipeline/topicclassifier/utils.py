import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer


class MultiClassDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_len):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.text = dataframe.question
        self.targets = self.data.title
        self.max_len = max_len

    def __len__(self):
        return len(self.text)

    def __getitem__(self, index):
        text = str(self.text[index])
        text = " ".join(text.split())

        inputs = self.tokenizer.encode_plus(
            text,
            None,
            add_special_tokens=True,
            max_length=self.max_len,
            pad_to_max_length=True,
            return_token_type_ids=True
        )
        ids = inputs['input_ids']
        mask = inputs['attention_mask']
        token_type_ids = inputs["token_type_ids"]

        return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
            'targets': torch.tensor(self.targets[index], dtype=torch.float)
        }


def create_train_dataset(df, tokenizer, train_size=0.7):
    train_data = df.sample(frac=train_size, random_state=200)
    validation_data = df.drop(train_data.index).reset_index(drop=True)
    train_data = train_data.reset_index(drop=True)

    print("FULL Dataset: {}".format(df.shape))
    print("TRAIN Dataset: {}".format(train_data.shape))
    print("VALIDATION Dataset: {}".format(validation_data.shape))

    training_set = MultiClassDataset(train_data, tokenizer, 128)
    validation_set = MultiClassDataset(validation_data, tokenizer, 128)
    return training_set, validation_set


def create_train_loader(train_df, train_size=0.7):
    tokenizer = DistilBertTokenizer.from_pretrained(
        'distilbert-base-uncased', truncation=True, do_lower_case=True)
    training_set, validation_set = create_train_dataset(
        train_df, tokenizer, train_size)

    train_params = {'batch_size': 4,
                    'shuffle': True,
                    'num_workers': 0
                    }

    validation_params = {'batch_size': 4,
                         'shuffle': True,
                         'num_workers': 0
                         }

    training_loader = DataLoader(training_set, **train_params)
    validation_loader = DataLoader(validation_set, **validation_params)

    return training_loader, validation_loader
