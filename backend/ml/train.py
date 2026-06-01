"""
Train the OrbitalLSTM model.

Usage (from backend/ folder with venv active):
    python -m ml.train
"""
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.lstm_predictor import OrbitalLSTM

DATA_DIR   = "ml/training_data"
SAVE_DIR   = "ml/checkpoints"
EPOCHS     = 30    # 40 epochs is best for orbit prediction, but takes too long to train
BATCH_SIZE = 128   # 32 is best for orbit prediction, but takes too long to train
HORIZON    = 144   # 144 steps = 12 hours instead of 72
LR         = 1e-3
VAL_SPLIT  = 0.1
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

POS_MEAN, POS_STD = 0.0, 7000.0
VEL_MEAN, VEL_STD = 0.0, 8.0


def normalize_X(X):
    X = X.copy()
    X[:, :, :3] = (X[:, :, :3] - POS_MEAN) / POS_STD
    X[:, :, 3:] = (X[:, :, 3:] - VEL_MEAN) / VEL_STD
    return X


def normalize_Y(Y):
    return (Y - POS_MEAN) / POS_STD


def train():
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Device: {DEVICE}")

    # Check data exists
    if not os.path.exists(f"{DATA_DIR}/X_train.npy"):
        print("ERROR: Training data not found.")
        print("Run: python -m ml.collect_training_data first")
        return

    print("Loading training data...")
    X_raw = np.load(f"{DATA_DIR}/X_train.npy")
    Y_raw = np.load(f"{DATA_DIR}/Y_train.npy")
    print(f"  X: {X_raw.shape}")
    print(f"  Y: {Y_raw.shape}")

    if len(X_raw) < 10:
        print("ERROR: Not enough training samples.")
        print("Need at least 10 sequences. Collect more data first.")
        return

    X = normalize_X(X_raw)
    Y = normalize_Y(Y_raw)

    X_t = torch.from_numpy(X).float()
    Y_t = torch.from_numpy(Y).float()

    dataset  = TensorDataset(X_t, Y_t)
    val_size = max(1, int(len(dataset) * VAL_SPLIT))
    trn_size = len(dataset) - val_size
    trn_ds, val_ds = random_split(dataset, [trn_size, val_size])

    trn_loader = DataLoader(trn_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)
    print(f"  Train: {trn_size} | Val: {val_size}")

    model = OrbitalLSTM(
        input_size=6,
        hidden_size=128,
        num_layers=2,
        output_steps=144,
        dropout=0.2,
    ).to(DEVICE)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"  Model parameters: {total_params:,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, patience=4, factor=0.5, verbose=True
    )
    criterion = nn.MSELoss()
    best_val  = float("inf")

    print("\nStarting training...\n")

    for epoch in range(1, EPOCHS + 1):
        model.train()
        trn_loss = 0.0
        t0 = time.time()

        for X_batch, Y_batch in trn_loader:
            X_batch = X_batch.to(DEVICE)
            Y_batch = Y_batch.to(DEVICE)
            optimizer.zero_grad()
            pred = model(X_batch)
            loss = criterion(pred, Y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            trn_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_batch, Y_batch in val_loader:
                X_batch = X_batch.to(DEVICE)
                Y_batch = Y_batch.to(DEVICE)
                pred     = model(X_batch)
                val_loss += criterion(pred, Y_batch).item()

        trn_loss /= len(trn_loader)
        val_loss /= len(val_loader)
        trn_km    = (trn_loss ** 0.5) * POS_STD
        val_km    = (val_loss ** 0.5) * POS_STD
        elapsed   = time.time() - t0

        print(
            f"Epoch {epoch:03d}/{EPOCHS} | "
            f"Train: {trn_km:7.1f} km | "
            f"Val: {val_km:7.1f} km | "
            f"{elapsed:.1f}s"
        )

        scheduler.step(val_loss)

        if val_loss < best_val:
            best_val = val_loss
            torch.save(
                model.state_dict(),
                f"{SAVE_DIR}/orbital_lstm_best.pt"
            )
            print(f"  ✓ Best model saved → {SAVE_DIR}/orbital_lstm_best.pt")

        if epoch % 10 == 0:
            torch.save(
                model.state_dict(),
                f"{SAVE_DIR}/orbital_lstm_epoch{epoch:03d}.pt"
            )

    best_km = (best_val ** 0.5) * POS_STD
    print(f"\nTraining complete.")
    print(f"Best validation error: {best_km:.1f} km")
    print(f"Model saved to: {SAVE_DIR}/orbital_lstm_best.pt")
    print(f"\nNext step: python -m ml.evaluate")


if __name__ == "__main__":
    train()