"""Train the local prompt-intent classifier and save data.pth."""

import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from config import BATCH_SIZE, DATA_FILE, HIDDEN_SIZE, INTENT_FILE, LEARNING_RATE, NUM_EPOCHS
from model import NeuralNet
from nltk_utils import bag_of_words, stem, tokenize


class PromptDataset(Dataset):
    def __init__(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data

    def __len__(self):
        return len(self.x_data)

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]


def main() -> None:
    with open(INTENT_FILE, "r", encoding="utf-8") as file:
        intents = json.load(file)

    all_words, tags, xy = [], [], []
    ignore_words = {"?", "!", ".", ","}
    for intent in intents["intents"]:
        tag = intent["tag"]
        tags.append(tag)
        for pattern in intent["patterns"]:
            tokens = tokenize(pattern)
            all_words.extend(tokens)
            xy.append((tokens, tag))

    all_words = sorted(set(stem(word) for word in all_words if word not in ignore_words))
    tags = sorted(set(tags))

    x_train, y_train = [], []
    for pattern_tokens, tag in xy:
        x_train.append(bag_of_words(pattern_tokens, all_words))
        y_train.append(tags.index(tag))

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    dataset = PromptDataset(x_train, y_train)
    train_loader = DataLoader(dataset=dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = NeuralNet(len(x_train[0]), HIDDEN_SIZE, len(tags)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(NUM_EPOCHS):
        for words, labels in train_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long).to(device)
            outputs = model(words)
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        if (epoch + 1) % 100 == 0:
            print(f"epoch {epoch + 1}/{NUM_EPOCHS}, loss={loss.item():.4f}")

    data = {
        "model_state": model.state_dict(),
        "input_size": len(x_train[0]),
        "hidden_size": HIDDEN_SIZE,
        "output_size": len(tags),
        "all_words": all_words,
        "tags": tags,
        "intents": intents,
    }
    torch.save(data, DATA_FILE)
    print(f"Training complete. Saved model and metadata to {Path(DATA_FILE).resolve()}")


if __name__ == "__main__":
    main()
