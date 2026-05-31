import os
# Hide unnecessary TensorFlow initialization logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
import numpy as np
from datasets import load_dataset
from sklearn.model_selection import train_test_split

print(" Waking up Upgraded General Topic Engine...")

# =====================================================================
#   1. INGEST & PRE-PROCESS FULL DATASET
# =====================================================================
print("Loading data from Hugging Face...")
raw_dataset = load_dataset("abzzer/Social-Media-Post-Relevance", split="train")

categories = ['politics', 'gaming', 'movies', 'sports', 'food', 'music', 'technology', 'books', 'science', 'art']
category_to_id = {cat: idx for idx, cat in enumerate(categories)}

print("Extracting text and converting labels...")
# Force inputs to strings to ensure the vectorizer processes them smoothly
texts = [str(example["content"]) for example in raw_dataset]
labels = [category_to_id[example["search"]] for example in raw_dataset]

X_train_raw, X_test_raw, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

print(f"Dataset ready! Training samples: {len(X_train_raw)}, Validation samples: {len(X_test_raw)}")

# =====================================================================
#   2. NATIVE TENSORFLOW TOKENIZATION
# =====================================================================
print("Building TensorFlow Text Vectorizer...")
# Tighten vocabulary slightly to 12,000 to eliminate rare noisy words (reduces overfitting)
vocab_size = 12000
max_length = 128

vectorize_layer = tf.keras.layers.TextVectorization(
    max_tokens=vocab_size, 
    output_sequence_length=max_length
)

print("Adapting vectorizer to training data text...")
vectorize_layer.adapt(tf.constant(X_train_raw))

# =====================================================================
#   3. BUILD THE ARCHITECTURE
# =====================================================================
print("Building native Keras Neural Network...")

model = tf.keras.Sequential([
    tf.keras.Input(shape=(1,), dtype=tf.string),  # Accept raw strings directly!
    vectorize_layer,                              # Text processing happens INSIDE the model
    tf.keras.layers.Embedding(
        input_dim=vocab_size, 
        output_dim=128,                           # Increased dimensions to capture deep context
        mask_zero=True  
    ),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),                 # Increased dropout to fight memorization
    tf.keras.layers.Dense(len(categories), activation='softmax') # Softmax gives clean probabilities!
])

# =====================================================================
#   4. COMPILE AND TRAIN
# =====================================================================
print("\nCompiling model...")
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(), # No longer from_logits=True
    metrics=['accuracy']
)

print("\nStarting Training Loop...")
history = model.fit(
    tf.constant(X_train_raw), 
    np.array(y_train), 
    validation_data=(tf.constant(X_test_raw), np.array(y_test)),
    epochs=15,                                    # 15 epochs is plenty with a 128-dim embedding
    batch_size=64,
    verbose=1
)

print("\nTraining Complete!")

# Save this general brain safely to its own file
model_save_path = "./saved_general_topic_model.keras"
model.save(model_save_path)
print(f" Saved general model to '{model_save_path}'")

# =====================================================================
#   5. LIVE INFERENCE EXAMPLES
# =====================================================================
print("\n=== Testing Live Predictions with Upgraded Model ===")
sample_new_posts = [
    "I can't wait for the new RPG to drop next week, the graphics look incredible.",
    "The central bank announced a new interest rate policy this morning.",
    "This homemade spicy chicken pizza recipe turned out amazing!"
]

for post in sample_new_posts:
    input_tensor = tf.constant([post])
    raw_predictions = model.predict(input_tensor, verbose=0)
    
    predicted_class_id = np.argmax(raw_predictions[0])
    confidence_score = raw_predictions[0][predicted_class_id] * 100
    predicted_category = categories[predicted_class_id]
    
    print(f"\n[PREDICTION: {predicted_category.upper()} ({confidence_score:.1f}% Confidence)]")
    print(f"Post: {post}") 