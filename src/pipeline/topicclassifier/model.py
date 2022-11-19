import tensorflow as tf
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertModel
from torch import cuda
from sklearn import metrics


class DistilBERTClass(torch.nn.Module):
    def __init__(self, n_titles):
        super(DistilBERTClass, self).__init__()
        self.l1 = DistilBertModel.from_pretrained("distilbert-base-uncased")
        self.pre_classifier = torch.nn.Linear(768, 768)
        self.dropout = torch.nn.Dropout(0.3)
        self.classifier = torch.nn.Linear(768, n_titles)

    def forward(self, input_ids, attention_mask):
        output_1 = self.l1(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = output_1[0]
        pooler = hidden_state[:, 0]
        pooler = self.pre_classifier(pooler)
        pooler = torch.nn.ReLU()(pooler)
        pooler = self.dropout(pooler)
        output = self.classifier(pooler)
        return output


class DistilBERTCustomModel():
    def __init__(self):
        self.device = 'cuda' if cuda.is_available() else 'cpu'
        self.model = DistilBERTClass()
        self.learning_rate = 1e-05
        self.optimizer = torch.optim.Adam(
            params=self.model.parameters(), lr=self.learning_rate)

        self.model.to(self.device)

    def train(self, epoch, training_loader):
        self.model.train()
        for _, data in enumerate(training_loader, 0):
            ids = data['ids'].to(self.device, dtype=torch.long)
            mask = data['mask'].to(self.device, dtype=torch.long)
            token_type_ids = data['token_type_ids'].to(
                self.device, dtype=torch.long)
            targets = data['targets'].to(self.device, dtype=torch.float)

            outputs = self.model(ids, mask)

            self.optimizer.zero_grad()
            loss = loss_fn(outputs, targets)
            if _ % 5000 == 0:
                print(f'Epoch: {epoch}, Loss:  {loss.item()}')

            loss.backward()
            self.optimizer.step()

    def validation(self, validation_loader):
        self.model.eval()
        fin_targets = []
        fin_outputs = []
        with torch.no_grad():
            for _, data in enumerate(validation_loader, 0):
                ids = data['ids'].to(self.device, dtype=torch.long)
                mask = data['mask'].to(self.device, dtype=torch.long)
                token_type_ids = data['token_type_ids'].to(
                    self.device, dtype=torch.long)
                targets = data['targets'].to(self.device, dtype=torch.float)
                outputs = self.model(ids, mask)
                fin_targets.extend(targets.cpu().detach().numpy().tolist())
                fin_outputs.extend(torch.sigmoid(
                    outputs).cpu().detach().numpy().tolist())
        return fin_outputs, fin_targets

    def fit(self, training_loader, validation_loader):
        for epoch in range(1):
            self.train(epoch, training_loader)

        outputs, targets = self.validation(validation_loader)

        final_outputs = np.array(outputs) >= 0.5

        val_hamming_loss = metrics.hamming_loss(targets, final_outputs)
        val_hamming_score = hamming_score(
            np.array(targets), np.array(final_outputs))

        print(f"Hamming Score = {val_hamming_score}")
        print(f"Hamming Loss = {val_hamming_loss}")


def loss_fn(outputs, targets):
    return torch.nn.BCEWithLogitsLoss()(outputs, targets)


def hamming_score(y_true, y_pred, normalize=True, sample_weight=None):
    acc_list = []
    for i in range(y_true.shape[0]):
        set_true = set(np.where(y_true[i])[0])
        set_pred = set(np.where(y_pred[i])[0])
        tmp_a = None
        if len(set_true) == 0 and len(set_pred) == 0:
            tmp_a = 1
        else:
            tmp_a = len(set_true.intersection(set_pred)) /\
                float(len(set_true.union(set_pred)))
        acc_list.append(tmp_a)
    return np.mean(acc_list)
