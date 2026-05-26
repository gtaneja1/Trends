# ========================================================================
#   SALES + MARKETING FORECAST - MODEL IMPROVISER (improvising_strategy.py)
# ========================================================================

# FORCE PYTORCH BACKEND DETECTION (PREVENT KERAS/TENSORFLOW IMPORT ERRORS)
import os
os.environ["USE_TORCH"] = "1"
os.environ["USE_TF"] = "0"
os.environ["USE_JAX"] = "0"

import torch
import numpy as np
from datasets import load_dataset
from sklearn.metrics import accuracy_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding
from transformers import TrainingArguments, Trainer

# =====================================================================
#   1. DEFINE & PRE-CONFIGURE THE MODELS
# =====================================================================
model_name = "bert-base-uncased"
print(f"Loading pre-trained tokenizer & model for {model_name}...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=10)

# =====================================================================
#   2. INGEST & PRE-PROCESS DATASETS
# =====================================================================
print("\nLoading 'abzzer/Social-Media-Post-Relevance' from Hugging Face...")
raw_dataset = load_dataset("abzzer/Social-Media-Post-Relevance")
train_split = raw_dataset["train"]

# Map string categories to numeric class labels (0 to 9)
categories = ['politics', 'gaming', 'movies', 'sports', 'food', 'music', 'technology', 'books', 'science', 'art']
category_to_id = {cat: idx for idx, cat in enumerate(categories)}

def add_numeric_labels(example):
    example["label"] = category_to_id[example["search"]]
    return example

print("Mapping string search categories to numeric target labels...")
labeled_dataset = train_split.map(add_numeric_labels)

# Split dataset manually into train (80%) and validation (20%) segments
print("Splitting dataset into train and validation sets...")
split_dataset = labeled_dataset.train_test_split(test_size=0.2, seed=42)

# Select a small subset for fast CPU testing (adjust these numbers for real training)
print("Selecting subset for fast validation run...")
train_data_subset = split_dataset["train"].shuffle(seed=42).select(range(40))
test_data_subset = split_dataset["test"].shuffle(seed=42).select(range(10))

# =====================================================================
#   3. TOKENIZATION
# =====================================================================
def tokenize(batch):
    return tokenizer(batch["content"], truncation=True)

print("Tokenizing content text columns...")
train_dataset = train_data_subset.map(tokenize, batched=True, batch_size=8)
test_dataset = test_data_subset.map(tokenize, batched=True, batch_size=8)

# =====================================================================
#   4. TRAINING CONFIGURATIONS
# =====================================================================
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=2,
    report_to="none"
)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc}

# Initialize data collator for dynamic padding
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
    data_collator=data_collator,
)

# =====================================================================
#   5. RUN TRAINING & EVALUATION
# =====================================================================
print("\nStarting model training...")
trainer.train()

print("\nEvaluating trained model performance...")
evaluation_results = trainer.evaluate()
print(f"\nEvaluation completed successfully!")
print(f"Test Accuracy achieved: {evaluation_results['eval_accuracy']:.4f}")
