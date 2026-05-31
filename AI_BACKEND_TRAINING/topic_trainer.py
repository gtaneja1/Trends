import os
import tensorflow as tf
import numpy as np
from datasets import load_dataset
from sklearn.model_selection import train_test_split

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

print("Waking up Upgraded General Topic Engine...")

# Automatically resolve paths so it saves in the correct folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_save_path = os.path.join(BASE_DIR, "saved_general_topic_model.keras")

# =====================================================================
#   1. INGEST & SANITIZE DATASET
# =====================================================================
print("Loading data from Hugging Face...")
raw_dataset = load_dataset("abzzer/Social-Media-Post-Relevance", split="train")

categories = ['politics', 'gaming', 'movies', 'sports', 'food', 'music', 'technology', 'books', 'science', 'art']
category_to_id = {cat: idx for idx, cat in enumerate(categories)}

print("Sanitizing social media text (removing emojis to prevent Windows encoding bugs)...")
texts = []
for example in raw_dataset:
    text_str = str(example["content"])
    # Force encode to cp1252 and ignore any emojis or unmappable characters
    clean_text = text_str.encode('cp1252', errors='ignore').decode('cp1252')
    texts.append(clean_text)

labels = [category_to_id[example["search"]] for example in raw_dataset]

X_train_raw, X_test_raw, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# =====================================================================
#   2. TOKENIZATION & ARCHITECTURE
# =====================================================================
print("Building TensorFlow Text Vectorizer & Network...")
vocab_size = 12000
max_length = 128

vectorize_layer = tf.keras.layers.TextVectorization(
    max_tokens=vocab_size, 
    output_sequence_length=max_length
)
vectorize_layer.adapt(tf.constant(X_train_raw))

model = tf.keras.Sequential([
    tf.keras.Input(shape=(1,), dtype=tf.string),  
    vectorize_layer,                              
    tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=128, mask_zero=True),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),                 
    tf.keras.layers.Dense(len(categories), activation='softmax') 
])

# =====================================================================
#   3. TRAIN & SAVE
# =====================================================================
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=['accuracy']
)

print("\n Starting Fast Training Loop (15 Epochs)...")
model.fit(
    tf.constant(X_train_raw), 
    np.array(y_train), 
    epochs=15,                                    
    batch_size=64,
    verbose=1
)

print(f"\n Saving fresh, uncorrupted model to '{model_save_path}'")
model.save(model_save_path)
print(" General Topic model successfully rebuilt and saved!")