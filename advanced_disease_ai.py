"""
Advanced Disease AI (Educational Prototype)

This module builds a synthetic bloodstream disease-analysis pipeline that:
1) simulates bloodstream biomarker time-series data,
2) trains a neural model to classify disease states, and
3) explains prediction drivers via feature attributions.

IMPORTANT:
- For research/education only.
- Not for diagnosis, triage, or treatment decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical


FEATURES = [
    "wbc_count",
    "crp",
    "procalcitonin",
    "lactate",
    "interleukin6",
    "platelet_count",
    "neutrophil_ratio",
    "d_dimer",
    "body_temp",
    "heart_rate",
]

DISEASE_LABELS = {
    0: "healthy",
    1: "viral_infection",
    2: "bacterial_sepsis",
    3: "autoimmune_flare",
}


@dataclass
class TrainingArtifacts:
    model: Sequential
    scaler: StandardScaler
    x_test: np.ndarray
    y_test: np.ndarray
    feature_names: List[str]


def _class_profile(label: int, size: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng()

    # baseline physiological ranges (synthetic)
    base = {
        "wbc_count": rng.normal(7.0, 1.3, size),
        "crp": rng.normal(1.2, 0.7, size),
        "procalcitonin": rng.normal(0.05, 0.03, size),
        "lactate": rng.normal(1.3, 0.4, size),
        "interleukin6": rng.normal(3.0, 1.2, size),
        "platelet_count": rng.normal(260, 40, size),
        "neutrophil_ratio": rng.normal(0.56, 0.1, size),
        "d_dimer": rng.normal(280, 120, size),
        "body_temp": rng.normal(36.9, 0.3, size),
        "heart_rate": rng.normal(74, 10, size),
    }

    # disease-specific signatures (synthetic)
    if label == 1:  # viral
        base["crp"] += rng.normal(2.5, 1.2, size)
        base["interleukin6"] += rng.normal(6, 2.5, size)
        base["body_temp"] += rng.normal(0.8, 0.3, size)
        base["neutrophil_ratio"] -= rng.normal(0.08, 0.04, size)
    elif label == 2:  # sepsis
        base["wbc_count"] += rng.normal(7.5, 2.2, size)
        base["crp"] += rng.normal(10.5, 3.8, size)
        base["procalcitonin"] += rng.normal(5.5, 1.8, size)
        base["lactate"] += rng.normal(3.8, 1.5, size)
        base["interleukin6"] += rng.normal(22, 7.0, size)
        base["platelet_count"] -= rng.normal(85, 30, size)
        base["d_dimer"] += rng.normal(1400, 500, size)
        base["body_temp"] += rng.normal(1.6, 0.5, size)
        base["heart_rate"] += rng.normal(26, 9, size)
    elif label == 3:  # autoimmune
        base["crp"] += rng.normal(6.3, 2.4, size)
        base["interleukin6"] += rng.normal(16, 5.4, size)
        base["d_dimer"] += rng.normal(700, 350, size)
        base["body_temp"] += rng.normal(0.5, 0.25, size)

    return base


def make_synthetic_dataset(samples_per_class: int = 600) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    for label in DISEASE_LABELS:
        profile = _class_profile(label, samples_per_class)
        df = pd.DataFrame(profile)
        df["label"] = label
        frames.append(df)

    dataset = pd.concat(frames, ignore_index=True)
    dataset[FEATURES] = dataset[FEATURES].clip(lower=0)
    return dataset.sample(frac=1.0, random_state=42).reset_index(drop=True)


def train_disease_ai(dataset: pd.DataFrame) -> TrainingArtifacts:
    x = dataset[FEATURES].values
    y = dataset["label"].values

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    num_classes = len(DISEASE_LABELS)
    y_train_cat = to_categorical(y_train, num_classes)

    model = Sequential(
        [
            Dense(128, activation="relu", input_shape=(len(FEATURES),)),
            Dropout(0.3),
            Dense(64, activation="relu"),
            Dropout(0.2),
            Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(optimizer=Adam(learning_rate=0.001), loss="categorical_crossentropy", metrics=["accuracy"])

    stopper = EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True)
    model.fit(
        x_train_scaled,
        y_train_cat,
        validation_split=0.2,
        epochs=60,
        batch_size=32,
        verbose=0,
        callbacks=[stopper],
    )

    return TrainingArtifacts(
        model=model,
        scaler=scaler,
        x_test=x_test_scaled,
        y_test=y_test,
        feature_names=FEATURES,
    )


def evaluate(artifacts: TrainingArtifacts) -> str:
    probs = artifacts.model.predict(artifacts.x_test, verbose=0)
    preds = np.argmax(probs, axis=1)
    names = [DISEASE_LABELS[idx] for idx in sorted(DISEASE_LABELS)]
    return classification_report(artifacts.y_test, preds, target_names=names)


def explain_single_prediction(artifacts: TrainingArtifacts, index: int = 0) -> List[Tuple[str, float]]:
    """Simple gradient-free attribution using local perturbation impact."""
    sample = artifacts.x_test[index : index + 1].copy()
    baseline_prob = artifacts.model.predict(sample, verbose=0)[0]
    baseline_class = int(np.argmax(baseline_prob))

    impacts = []
    for i, name in enumerate(artifacts.feature_names):
        perturbed = sample.copy()
        perturbed[0, i] = 0.0
        perturbed_prob = artifacts.model.predict(perturbed, verbose=0)[0]
        delta = float(baseline_prob[baseline_class] - perturbed_prob[baseline_class])
        impacts.append((name, delta))

    impacts.sort(key=lambda item: abs(item[1]), reverse=True)
    return impacts


def main() -> None:
    dataset = make_synthetic_dataset(samples_per_class=600)
    artifacts = train_disease_ai(dataset)

    print("=== Disease AI Evaluation (Synthetic Bloodstream Data) ===")
    print(evaluate(artifacts))

    top = explain_single_prediction(artifacts, index=5)[:5]
    print("Top feature impacts for one prediction:")
    for feature, score in top:
        print(f"  - {feature:18s} impact={score:+.4f}")

    print("\nSafety note: This prototype is educational and not a medical device.")


if __name__ == "__main__":
    main()
