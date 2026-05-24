# ========================================================================
#   SALES + MARKETING FORECAST - PYTORCH MODEL TRAINING (train_model.py)
# ========================================================================

import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

# =====================================================================
#   1. DEFINE THE NEURAL NETWORK ARCHITECTURE
# =====================================================================
#   INPUTS (4 Numbers):
#     - Column 0 (Ad Spend): Normalized budget (0.1 = low, 1.0 = high).
#     - Column 1 (Market Sentiment): Broad consumer eagerness index (0.1 = very cautious/slow economy, 1.0 = high spending eagerness).
#     - Column 2 (Trend Score): Popularity/viral interest index (0.1 to 1.0).
#     - Column 3 (Quality Score): Rating of the user's content/drafts (0.1 to 1.0).
#
#   OUTPUTS (2 Numbers):
#     - Column 0 (Reach Multiplier): Expected viewer growth (e.g. 2.5x reach).
#     - Column 1 (Conversion Rate): Expected purchase rate (e.g. 4% conversion).
# =====================================================================
class SalesPredictor(nn.Module):
    def __init__(self):
        super(SalesPredictor, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 8),
            nn.ReLU(),
            nn.Linear(8, 2)
        )
        
    def forward(self, x):
        return self.network(x)

# =====================================================================
#   2. FEEDING YOUR CUSTOM DATASET (HOW & WHERE TO INSERT)
# =====================================================================
def get_training_dataset():
    
    # -----------------------------------------------------------------
    #   >>> UNCOMMENT AND CUSTOMIZE THIS BLOCK TO LOAD YOUR DATA <<<
    # -----------------------------------------------------------------
    #   Step 1: Save your CSV sheet in the same folder as this script.
    #   Step 2: Install pandas if needed (pip install pandas).
    #   Step 3: Remove the "#" signs from the lines below:
    #
    #   import pandas as pd
    #   
    #   # Read CSV file
    #   df = pd.read_csv("my_historical_sales.csv")
    #
    #   # Group features (the factors the model looks at)
    #   input_features = df[['ad_spend', 'market_sentiment', 'trend_score', 'quality_score']].values
    #
    #   # Group targets (what the model is trying to predict)
    #   output_targets = df[['reach_multiplier', 'conversion_rate']].values
    #
    #   # Convert datasets to PyTorch Float Tensors
    #   X = torch.tensor(input_features, dtype=torch.float32)
    #   y = torch.tensor(output_targets, dtype=torch.float32)
    #   return X, y
    # -----------------------------------------------------------------
    
    print("No custom CSV file loaded. Generating synthetic training data instead...")
    
    # --- BROAD SYNTHETIC DATASET GENERATOR ---
    num_samples = 1200
    np.random.seed(42)
    
    ad_spend = np.random.uniform(0.1, 1.0, num_samples)
    market_sentiment = np.random.uniform(0.2, 1.0, num_samples) # 0.2 = Cautious, 1.0 = Eager
    trend_index = np.random.uniform(0.1, 1.0, num_samples)
    quality_score = np.random.uniform(0.2, 1.0, num_samples)
    
    inputs = np.stack([ad_spend, market_sentiment, trend_index, quality_score], axis=1)
    
    # Projections based on broad sentiment weights (instead of narrow inflation numbers)
    reach_multiplier = (ad_spend * 3.0) + (quality_score * 1.5) + (trend_index * 2.0) + (market_sentiment * 0.5)
    reach_multiplier = np.clip(reach_multiplier, 0.1, 8.0)
    
    conversion_rate = (quality_score * 0.04) + (trend_index * 0.02) + (market_sentiment * 0.06) + 0.01
    conversion_rate = np.clip(conversion_rate, 0.005, 0.15)
    
    outputs = np.stack([reach_multiplier, conversion_rate], axis=1)
    
    X = torch.tensor(inputs, dtype=torch.float32)
    y = torch.tensor(outputs, dtype=torch.float32)
    return X, y

# =====================================================================
#   3. TRAINING ROUTINE
# =====================================================================
def train_model():
    print("Initializing PyTorch pipeline...")
    
    # Load dataset
    X, y = get_training_dataset()
    
    split_idx = int(0.8 * len(X))
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    model = SalesPredictor()
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    epochs = 100
    batch_size = 32
    
    print("Training SalesPredictor neural network...")
    
    for epoch in range(epochs):
        model.train()
        permutation = torch.randperm(X_train.size()[0])
        epoch_loss = 0
        
        for i in range(0, X_train.size()[0], batch_size):
            indices = permutation[i:i+batch_size]
            batch_x, batch_y = X_train[indices], y_train[indices]
            
            predictions = model(batch_x)
            loss = criterion(predictions, batch_y)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item() * len(indices)
            
        if (epoch + 1) % 10 == 0 or epoch == 0:
            model.eval()
            with torch.no_grad():
                val_preds = model(X_val)
                val_loss = criterion(val_preds, y_val).item()
            print(f"Epoch {epoch+1:03d}/{epochs} | Train Loss: {epoch_loss/len(X_train):.6f} | Val Loss: {val_loss:.6f}")
            
    model_filename = "sales_model.pth"
    torch.save(model.state_dict(), model_filename)
    print(f"\nTraining completed! Saved PyTorch model weights to: {os.path.abspath(model_filename)}")

if __name__ == "__main__":
    train_model()
