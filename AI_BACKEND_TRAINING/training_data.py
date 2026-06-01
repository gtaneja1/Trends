import os
import warnings
warnings.filterwarnings("ignore")

print(" 🚀 Script is running! Loading massive AI libraries (this might take 30 seconds)...")
# Hide the annoying warnings to keep your terminal clean
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  

# FORCE the system to ONLY use TensorFlow and ignore everything else
os.environ["KERAS_BACKEND"] = "tensorflow"

import tensorflow as tf
import numpy as np
from datasets import load_dataset
from sklearn.model_selection import train_test_split

print("Waking up Pure TensorFlow Engine...")


print("Loading data...")
raw_dataset = load_dataset("abzzer/Social-Media-Post-Relevance", split="train")

categories = ['politics', 'gaming', 'movies', 'sports', 'food', 'music', 'technology', 'books', 'science', 'art']
category_to_id = {cat: idx for idx, cat in enumerate(categories)}

print("Extracting raw text and labels...")
texts = [example["content"] for example in raw_dataset]
labels = [category_to_id[example["search"]] for example in raw_dataset]

texts = np.array(texts)
labels = np.array(labels)

# Split into train and test
X_train_raw, X_test_raw, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Select a small subset for fast testing (remove this for real training!)
X_train_raw, y_train = X_train_raw[:100], y_train[:100]
X_test_raw, y_test = X_test_raw[:20], y_test[:20]

# =====================================================================
#   2. NATIVE TENSORFLOW TOKENIZATION (UPFRONT)
# =====================================================================
print("Building TensorFlow Text Vectorizer...")
vectorize_layer = tf.keras.layers.TextVectorization(
    max_tokens=10000, 
    output_sequence_length=128
)

# Learn the vocabulary from the training strings
vectorize_layer.adapt(X_train_raw)

print("Vectorizing text data into integer sequences...")
# We transform the strings to integers here so model.fit doesn't see raw strings
X_train = vectorize_layer(X_train_raw)
X_test = vectorize_layer(X_test_raw)

# =====================================================================
#   3. BUILD THE PURE TENSORFLOW MODEL
# =====================================================================
print("Building native Keras Neural Network...")

model = tf.keras.Sequential([
    # The model now receives integer sequences directly, matching the input dimension of 10000 tokens
    tf.keras.layers.Embedding(
        input_dim=10000, 
        output_dim=64, 
        mask_zero=True
    ),
    
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10) 
])

print("\nCompiling model...")
model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
    metrics=['accuracy']
)

print("\nStarting Training Loop...")
history = model.fit(
    X_train, 
    y_train, 
    validation_data=(X_test, y_test),
    epochs=5,
    batch_size=16
)

print("\nTraining Complete!")

# =====================================================================
#   5. LIVE INFERENCE EXAMPLES
# =====================================================================
print("\n=== Testing Live Predictions ===")
sample_new_posts = [
    "I can't wait for the new RPG to drop next week, the graphics look incredible.",
    "The central bank announced a new interest rate policy this morning.",
    "This homemade spicy chicken pizza recipe turned out amazing!"
]

# Transform the raw text strings through our vectorizer before predicting
tokenized_samples = vectorize_layer(np.array(sample_new_posts))
raw_predictions = model.predict(tokenized_samples)

# Apply softmax to see probabilities or take the highest index
for i, post in enumerate(sample_new_posts):
    predicted_class_id = np.argmax(raw_predictions[i])
    predicted_category = categories[predicted_class_id]
    print(f"\n[PREDICTION: {predicted_category.upper()}]")
    print(f"Post: {post}")
import os
# Hide the annoying warnings to keep your terminal clean
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  

import tensorflow as tf
import numpy as np
from datasets import load_dataset
from sklearn.model_selection import train_test_split

print("Waking up Pure TensorFlow Engine...")


print("Loading data...")
raw_dataset = load_dataset("abzzer/Social-Media-Post-Relevance", split="train")

categories = ['politics', 'gaming', 'movies', 'sports', 'food', 'music', 'technology', 'books', 'science', 'art']
category_to_id = {cat: idx for idx, cat in enumerate(categories)}

print("Extracting raw text and labels...")
texts = [example["content"] for example in raw_dataset]
labels = [category_to_id[example["search"]] for example in raw_dataset]

texts = np.array(texts)
labels = np.array(labels)

# Split into train and test
X_train_raw, X_test_raw, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Select a small subset for fast testing (remove this for real training!)
X_train_raw, y_train = X_train_raw[:100], y_train[:100]
X_test_raw, y_test = X_test_raw[:20], y_test[:20]

# =====================================================================
#   2. NATIVE TENSORFLOW TOKENIZATION (UPFRONT)
# =====================================================================
print("Building TensorFlow Text Vectorizer...")
vectorize_layer = tf.keras.layers.TextVectorization(
    max_tokens=10000, 
    output_sequence_length=128
)

# Learn the vocabulary from the training strings
vectorize_layer.adapt(X_train_raw)

print("Vectorizing text data into integer sequences...")
# We transform the strings to integers here so model.fit doesn't see raw strings
X_train = vectorize_layer(X_train_raw)
X_test = vectorize_layer(X_test_raw)

# =====================================================================
#   3. BUILD THE PURE TENSORFLOW MODEL
# =====================================================================
print("Building native Keras Neural Network...")

model = tf.keras.Sequential([
    # The model now receives integer sequences directly, matching the input dimension of 10000 tokens
    tf.keras.layers.Embedding(
        input_dim=10000, 
        output_dim=64, 
        mask_zero=True
    ),
    
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10) 
])

print("\nCompiling model...")
model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
    metrics=['accuracy']
)

print("\nStarting Training Loop...")
history = model.fit(
    X_train, 
    y_train, 
    validation_data=(X_test, y_test),
    epochs=5,
    batch_size=16
)

print("\nTraining Complete!")

# =====================================================================
#   5. LIVE INFERENCE EXAMPLES
# =====================================================================
print("\n=== Testing Live Predictions ===")
sample_new_posts = [
    "I can't wait for the new RPG to drop next week, the graphics look incredible.",
    "The central bank announced a new interest rate policy this morning.",
    "This homemade spicy chicken pizza recipe turned out amazing!"
]

# Transform the raw text strings through our vectorizer before predicting
tokenized_samples = vectorize_layer(np.array(sample_new_posts))
raw_predictions = model.predict(tokenized_samples)

# Apply softmax to see probabilities or take the highest index
for i, post in enumerate(sample_new_posts):
    predicted_class_id = np.argmax(raw_predictions[i])
    predicted_category = categories[predicted_class_id]
    print(f"\n[PREDICTION: {predicted_category.upper()}]")
    print(f"Post: {post}")