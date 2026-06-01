import os
import warnings
import tensorflow as tf
import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification

# Clean up terminal output
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("🚀 Waking up Hugging Face (TensorFlow Engine)...")

def prepare_tf_dataset(hf_dataset, tokenizer, batch_size=8, shuffle=False):
    """Converts a Hugging Face Dataset into a high-performance tf.data.Dataset"""
    def tokenize_function(examples):
        return tokenizer(examples["content"], padding="max_length", truncation=True, max_length=128)
    
    tokenized_dataset = hf_dataset.map(tokenize_function, batched=True)
    
    tf_dataset = tokenized_dataset.to_tf_dataset(
        columns=["input_ids", "attention_mask"],
        label_cols=["label"],
        shuffle=shuffle,
        batch_size=batch_size,
    )
    return tf_dataset

def run_elite_training():
    model_id = "distilbert-base-uncased"
    print(f"Loading Tokenizer & Base Model ({model_id})...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    print("Fetching 'abzzer/Social-Media-Post-Relevance' dataset...")
    raw_dataset = load_dataset("abzzer/Social-Media-Post-Relevance", split="train")

    categories = ['politics', 'gaming', 'movies', 'sports', 'food', 'music', 'technology', 'books', 'science', 'art']
    category_to_id = {cat: idx for idx, cat in enumerate(categories)}

    def add_labels(example):
        example["label"] = category_to_id[example["search"]]
        return example
        
    labeled_dataset = raw_dataset.map(add_labels)

    # Split dataset
    split_dataset = labeled_dataset.train_test_split(test_size=0.2, seed=42)
    
    print("Converting to TensorFlow Dataset format...")
    # NOTE: Slicing here for quick testing (100 examples). 
    train_subset = split_dataset["train"].select(range(100))
    eval_subset = split_dataset["test"].select(range(20))

    tf_train_dataset = prepare_tf_dataset(train_subset, tokenizer, batch_size=8, shuffle=True)
    tf_eval_dataset = prepare_tf_dataset(eval_subset, tokenizer, batch_size=8, shuffle=False)

    print("Building Hugging Face TF Model...")
    model = TFAutoModelForSequenceClassification.from_pretrained(
        model_id, 
        num_labels=len(categories),
        id2label={idx: cat for cat, idx in category_to_id.items()},
        label2id=category_to_id
    )

    print("Compiling model mechanics...")
    # WE BYPASS HUGGING FACE HERE AND USE PURE TENSORFLOW TO PREVENT CRASHES
    optimizer = tf.keras.optimizers.Adam(learning_rate=2e-5)
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    metrics = [tf.keras.metrics.SparseCategoricalAccuracy("accuracy")]
    
    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    print("\n🔥 Launching Elite Training Loop...")
    model.fit(tf_train_dataset, validation_data=tf_eval_dataset, epochs=3)

    print("\n✅ Training Complete!")
    
    print("\n=== Testing Optimized Predictions ===")
    sample_posts = [
        "The new graphics card benchmarks are insane, hitting 240fps on ultra settings.",
        "Senators are debating the new tax policy proposal today.",
        "Just made the most incredible slow-cooked brisket."
    ]

    inputs = tokenizer(sample_posts, padding=True, truncation=True, return_tensors="tf")
    outputs = model(**inputs)
    predictions = tf.math.argmax(outputs.logits, axis=-1)

    for i, post in enumerate(sample_posts):
        predicted_category = model.config.id2label[int(predictions[i])]
        print(f"\n[PREDICTION: {predicted_category.upper()}]")
        print(f"Post: {post}")

if __name__ == "__main__":
    run_elite_training()