# Hide unnecessary TensorFlow initialization logs
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

print(" Waking up Pure TensorFlow Marketing Engine...")

# =====================================================================
#   1. INGEST & PRE-PROCESS LOCAL STRATEGY DATASET
# =====================================================================
print("Loading data from local CSV...")

# Automatically detect the folder where market_trainer.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Build the absolute path to the CSV file
csv_path = os.path.join(current_dir, "marketing_strategy_dataset.csv")

# Load the dataset
df = pd.read_csv(csv_path)

# Extract your unique categories dynamically from the CSV file
categories = df["category_label"].unique().tolist()
category_to_id = {cat: idx for idx, cat in enumerate(categories)}

print("Extracting text and converting labels...")
# ---> FIX 1: We check if the column is 'problem_description' or 'text_input' and use the right one
text_col = "problem_description" if "problem_description" in df.columns else "text_input"
texts = df[text_col].astype(str).tolist()

labels = [category_to_id[cat] for cat in df["category_label"]]

X_train_raw, X_test_raw, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

print(f"Dataset ready! Training samples: {len(X_train_raw)}, Validation samples: {len(X_test_raw)}")

# =====================================================================
#   2. NATIVE TENSORFLOW TOKENIZATION
# =====================================================================
print("Building TensorFlow Text Vectorizer...")
vocab_size = 5000
max_length = 64

vectorize_layer = tf.keras.layers.TextVectorization(
    max_tokens=vocab_size, 
    output_sequence_length=max_length
)

print("Adapting vectorizer to training data text...")
vectorize_layer.adapt(X_train_raw)

# =====================================================================
#   3. BUILD THE ARCHITECTURE
# =====================================================================
print(" Building native Keras Neural Network...")

model = tf.keras.Sequential([
    tf.keras.Input(shape=(1,), dtype=tf.string),  
    vectorize_layer,                              
    tf.keras.layers.Embedding(
        input_dim=vocab_size, 
        output_dim=32, 
        mask_zero=True
    ),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(len(categories))  
])

# =====================================================================
#   4. COMPILE AND TRAIN
# =====================================================================
print("\n Compiling model...")
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
    metrics=['accuracy']
)

print("\n Starting Training Loop...")
history = model.fit(
    tf.constant(X_train_raw), 
    np.array(y_train), 
    validation_data=(tf.constant(X_test_raw), np.array(y_test)),
    epochs=40,
    batch_size=4,
    verbose=1 # Added verbose=1 so you can see the progress bar!
)

print("\n Training Complete!")

# =====================================================================
#   5. SAVE THE CHOSEN BRAIN FOR THE PRODUCTION PIPELINE
# =====================================================================
# ---> FIX 2: Save the model inside the current directory alongside the CSV!
model_save_path = os.path.join(current_dir, "saved_routing_model.keras")

print(f"\n Saving trained router to '{model_save_path}'...")
model.save(model_save_path)
print("Router saved! Ready to load into your live pipeline script.")

# =====================================================================
#   6. LIVE INFERENCE EXAMPLES
# =====================================================================
print("\n=== Testing Live Predictions with Your New Router ===")

sample_marketing_inputs = [
    "How can I get more followers naturally without spending money on social ads?",
    "Our Google Ads campaign has a horrible conversion rate, how do we fix the ROAS?",
    "What's the best approach to pitch micro-influencers on TikTok for a product launch?"
]

print("Processing sample queries through the trained network...")

for post in sample_marketing_inputs:
    input_tensor = tf.constant([post])
    raw_predictions = model.predict(input_tensor, verbose=0)
    
    predicted_class_id = np.argmax(raw_predictions[0])
    predicted_category = categories[predicted_class_id]
    
    print(f"\n[ROUTE TO: {predicted_category.upper()}]")
    print(f"Query: \"{post}\"")

print("\n All pipeline tests complete!")