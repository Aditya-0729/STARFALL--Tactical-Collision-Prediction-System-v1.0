"""
LSTM-based trajectory prediction.
Architecture: sequence-to-sequence LSTM trained on historical state vectors.
"""
import numpy as np
import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import Optional


@dataclass
class PredictionResult:
    object_id:              int
    predicted_trajectory:   list[dict]
    anomaly_score:          float
    collision_probability:  float
    risk_level:             str


class OrbitalLSTM(nn.Module):
    """
    Sequence-to-sequence LSTM for orbital trajectory prediction.
    Input:  (batch, seq_len=48, features=6)
    Output: (batch, horizon=144, 3)
    """
    def __init__(
        self,
        input_size:   int   = 6,
        hidden_size:  int   = 128,
        num_layers:   int   = 2,
        output_steps: int   = 144,
        dropout:      float = 0.2,
    ):
        super().__init__()
        self.hidden_size  = hidden_size
        self.num_layers   = num_layers
        self.output_steps = output_steps

        self.encoder = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout,
        )
        self.decoder = nn.LSTM(
            3, hidden_size, num_layers,
            batch_first=True, dropout=dropout,
        )
        self.fc_out = nn.Linear(hidden_size, 3)

    def forward(
        self,
        src: torch.Tensor,
        tgt: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        _, (h, c) = self.encoder(src)

        batch     = src.size(0)
        dec_input = torch.zeros(batch, 1, 3, device=src.device)
        outputs   = []

        for _ in range(self.output_steps):
            out, (h, c) = self.decoder(dec_input, (h, c))
            pred        = self.fc_out(out)
            outputs.append(pred)
            dec_input   = pred

        return torch.cat(outputs, dim=1)


class TrajectoryPredictor:
    """
    Wraps OrbitalLSTM with normalization, inference, and scoring.
    """
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, model_path: Optional[str] = None, device: str = "cpu"):
        self.device = torch.device(device)
        self.model  = OrbitalLSTM().to(self.device)
        self.model.eval()

        if model_path:
            try:
                state = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(state)
                print(f"Model loaded from {model_path}")
            except Exception as e:
                print(f"Warning: Could not load model weights: {e}")

        # Normalization stats matching train.py
        self.pos_mean = 0.0
        self.pos_std  = 7000.0
        self.vel_mean = 0.0
        self.vel_std  = 8.0

    def _normalize(self, states: list[dict]) -> torch.Tensor:
        arr = np.array([[
            (s["x_km"]    - self.pos_mean) / self.pos_std,
            (s["y_km"]    - self.pos_mean) / self.pos_std,
            (s["z_km"]    - self.pos_mean) / self.pos_std,
            (s["vx_km_s"] - self.vel_mean) / self.vel_std,
            (s["vy_km_s"] - self.vel_mean) / self.vel_std,
            (s["vz_km_s"] - self.vel_mean) / self.vel_std,
        ] for s in states], dtype=np.float32)

        return torch.from_numpy(arr).unsqueeze(0).to(self.device)

    def _denormalize(self, tensor: torch.Tensor) -> np.ndarray:
        arr = tensor.squeeze(0).cpu().detach().numpy()
        return arr * self.pos_std + self.pos_mean

    def _compute_anomaly(
        self,
        predicted: np.ndarray,
        history:   list[dict],
    ) -> float:
        """
        Compare predicted first positions against extrapolated history.
        Score 0.0 = normal, 1.0 = highly anomalous.
        """
        if len(history) < 2:
            return 0.0

        # Expected position: linear extrapolation from last history point
        last = history[-1]
        vx, vy, vz = last["vx_km_s"], last["vy_km_s"], last["vz_km_s"]
        dt = 300  # 5 minutes in seconds

        expected_positions = np.array([
            [
                last["x_km"] + vx * dt * (i + 1),
                last["y_km"] + vy * dt * (i + 1),
                last["z_km"] + vz * dt * (i + 1),
            ]
            for i in range(min(12, len(predicted)))
        ])

        actual = predicted[:len(expected_positions)]
        residuals = np.linalg.norm(actual - expected_positions, axis=1)

        # Normalize: typical short-term deviation is ~50-200 km
        mean_residual = float(np.mean(residuals))
        score = min(mean_residual / 2000.0, 1.0)
        return round(score, 4)

    def _compute_pc(
        self,
        predicted: np.ndarray,
        object_id: int,
    ) -> float:
        """
        Compute simplified Probability of Collision based on
        minimum predicted altitude above Earth surface.
        """
        radii = np.linalg.norm(predicted, axis=1)
        altitudes = radii - self.EARTH_RADIUS_KM

        min_alt = float(np.min(altitudes))

        # Objects below 200km are decaying — higher Pc
        if min_alt < 0:
            return 1e-2
        elif min_alt < 100:
            return 1e-3
        elif min_alt < 200:
            return 1e-4
        elif min_alt < 300:
            return 1e-5
        else:
            # Normal orbit — very low Pc
            return 1e-7

    @torch.no_grad()
    def predict(
        self,
        history:   list[dict],
        object_id: int,
    ) -> PredictionResult:
        """
        Run inference on history, return 12-hour prediction.
        """
        if len(history) < 5:
            return self._fallback(history, object_id)

        # Pad or trim to 48 steps
        seq = history[-48:] if len(history) >= 48 else history
        if len(seq) < 48:
            padding = [seq[0]] * (48 - len(seq))
            seq     = padding + seq

        src       = self._normalize(seq)
        output    = self.model(src)              # (1, 144, 3)
        positions = self._denormalize(output)    # (144, 3)

        trajectory = [
            {
                "x_km": float(p[0]),
                "y_km": float(p[1]),
                "z_km": float(p[2]),
            }
            for p in positions
        ]

        anomaly = self._compute_anomaly(positions, history)
        pc      = self._compute_pc(positions, object_id)

        if pc >= 1e-3:
            risk = "CRITICAL"
        elif pc >= 1e-4:
            risk = "WARNING"
        else:
            risk = "SAFE"

        return PredictionResult(
            object_id=object_id,
            predicted_trajectory=trajectory,
            anomaly_score=anomaly,
            collision_probability=pc,
            risk_level=risk,
        )

    def _fallback(
        self,
        history:   list[dict],
        object_id: int,
    ) -> PredictionResult:
        last = history[-1] if history else {"x_km": 0, "y_km": 0, "z_km": 0}
        trajectory = [
            {"x_km": last["x_km"], "y_km": last["y_km"], "z_km": last["z_km"]}
            for _ in range(144)
        ]
        return PredictionResult(
            object_id=object_id,
            predicted_trajectory=trajectory,
            anomaly_score=0.0,
            collision_probability=1e-7,
            risk_level="SAFE",
        )