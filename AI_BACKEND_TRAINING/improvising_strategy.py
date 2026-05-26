from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import TrainingArguments, Trainer
import numpy as np
from sklearn.metrics import accuracy_score
import pandas as pd

model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

from datasets import load_dataset

# Dataset 1
dataset_1 = load_dataset("abzzer/Social-Media-Post-Relevance")

train_1 = dataset_1["train"].shuffle(seed=42).select(range(1000))
test_1 = dataset_1["test"].shuffle(seed=42).select(range(200))

# Dataset 2
dataset_2 = load_dataset("lingbow/tiktok-trending-hashtags-music")

train_2 = dataset_2["train"].shuffle(seed=42).select(range(1000))

def tokenize(batch):
    return tokenizer(batch["text"], padding=True, truncation=True)
train_dataset = train_dataset.map(tokenize, batched=True, batch_size = 16)
test_dataset = test_dataset.map(tokenize, batched=True, batch_size = 16)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
results = trainer.evaluate()
print(f"Test Accuracy: {results['eval_accuracy']:.4f}")




