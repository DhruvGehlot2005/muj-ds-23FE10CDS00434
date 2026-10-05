"""
@file train_section_classifier.py
@description Trains, evaluates, and exports the TF-IDF + Logistic Regression Resume Section Classifier
@module backend.app.ml.train_section_classifier
"""

import json
import os
import re
from typing import Dict, Any

import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def clean_text_for_ml(text: str) -> str:
    """
    Lightweight text normalization for TF-IDF feature extraction.

    @param text: Raw input text
    @return Cleaned, normalized string
    """
    if not isinstance(text, str):
        return ""
    # Lowercase and clean URLs/emails slightly to retain signal
    lowered = text.lower().strip()
    # Replace URLs with token
    lowered = re.sub(r"https?://\S+|www\.\S+", "url_token", lowered)
    # Normalize whitespaces
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def train_and_evaluate(
    train_csv_path: str = "data/training/resume_sections.csv",
    unseen_test_csv_path: str = "data/tests/resume_section_test_cases.csv",
    model_output_path: str = "data/models/resume_section_classifier.joblib",
    metrics_output_path: str = "data/models/section_classifier_metrics.json",
    confusion_matrix_path: str = "data/models/confusion_matrix.png",
) -> Dict[str, Any]:
    """
    Loads dataset, trains TF-IDF + Logistic Regression pipeline, evaluates on held-out
    validation split and unseen test cases, and persists model artifacts.

    @return Metrics dictionary
    """
    print(f"Loading training dataset from: {train_csv_path}")
    if not os.path.exists(train_csv_path):
        raise FileNotFoundError(f"Training dataset not found: {train_csv_path}")

    df = pd.read_csv(train_csv_path)
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'text' and 'label' columns.")

    # Drop nulls and strip
    df = df.dropna(subset=["text", "label"]).copy()
    df["clean_text"] = df["text"].apply(clean_text_for_ml)
    df["label"] = df["label"].str.strip()

    labels = sorted(df["label"].unique().tolist())
    print(f"Dataset loaded: {len(df)} samples across {len(labels)} classes: {labels}")

    # 1. Stratified split (80% train, 20% validation)
    X_train_raw, X_val_raw, y_train, y_val = train_test_split(
        df["clean_text"],
        df["label"],
        test_size=0.20,
        random_state=42,
        stratify=df["label"],
    )

    print(f"Training samples: {len(X_train_raw)}, Validation samples: {len(X_val_raw)}")

    # 2. Pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    C=8.0,
                    max_iter=1000,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    print("Fitting TF-IDF + Logistic Regression Pipeline...")
    pipeline.fit(X_train_raw, y_train)

    # 3. Evaluate on held-out validation set
    y_val_pred = pipeline.predict(X_val_raw)
    val_accuracy = float(accuracy_score(y_val, y_val_pred))
    val_precision_macro = float(precision_score(y_val, y_val_pred, average="macro", zero_division=0))
    val_recall_macro = float(recall_score(y_val, y_val_pred, average="macro", zero_division=0))
    val_f1_macro = float(f1_score(y_val, y_val_pred, average="macro", zero_division=0))
    val_report = classification_report(y_val, y_val_pred, output_dict=True, zero_division=0)
    val_cm = confusion_matrix(y_val, y_val_pred, labels=labels).tolist()

    print(f"\n--- HELD-OUT VALIDATION METRICS ---")
    print(f"Accuracy:  {val_accuracy * 100:.2f}%")
    print(f"Macro F1:  {val_f1_macro * 100:.2f}%")

    # 4. Evaluate on separate unseen test cases
    unseen_metrics: Dict[str, Any] = {}
    if os.path.exists(unseen_test_csv_path):
        test_df = pd.read_csv(unseen_test_csv_path)
        test_df["clean_text"] = test_df["text"].apply(clean_text_for_ml)
        y_test = test_df["expected_label"].str.strip()
        y_test_pred = pipeline.predict(test_df["clean_text"])

        test_acc = float(accuracy_score(y_test, y_test_pred))
        test_f1 = float(f1_score(y_test, y_test_pred, average="macro", zero_division=0))
        test_report = classification_report(y_test, y_test_pred, output_dict=True, zero_division=0)
        test_cm = confusion_matrix(y_test, y_test_pred, labels=labels).tolist()

        unseen_metrics = {
            "test_sample_count": len(test_df),
            "accuracy": test_acc,
            "f1_macro": test_f1,
            "precision_macro": float(precision_score(y_test, y_test_pred, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y_test, y_test_pred, average="macro", zero_division=0)),
            "classification_report": test_report,
            "confusion_matrix": test_cm,
        }
        print(f"\n--- SEPARATE UNSEEN TEST CASES METRICS ---")
        print(f"Accuracy:  {test_acc * 100:.2f}%")
        print(f"Macro F1:  {test_f1 * 100:.2f}%")

    # 5. Export model artifact
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(pipeline, model_output_path)
    print(f"\nModel pipeline saved to: {model_output_path}")

    # 6. Export metrics JSON
    metrics_data = {
        "model_architecture": "TF-IDF (1-2 ngrams) + Logistic Regression (C=1.5, balanced)",
        "classes": labels,
        "training_sample_count": len(X_train_raw),
        "validation_sample_count": len(X_val_raw),
        "validation_metrics": {
            "accuracy": val_accuracy,
            "precision_macro": val_precision_macro,
            "recall_macro": val_recall_macro,
            "f1_macro": val_f1_macro,
            "classification_report": val_report,
            "confusion_matrix": val_cm,
        },
        "unseen_test_cases_metrics": unseen_metrics,
    }

    with open(metrics_output_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Metrics saved to: {metrics_output_path}")

    # 7. Optionally generate confusion matrix plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 8))
        cm_array = np.array(val_cm)
        cax = ax.matshow(cm_array, cmap=plt.cm.Blues, alpha=0.8)

        for i in range(cm_array.shape[0]):
            for j in range(cm_array.shape[1]):
                ax.text(
                    x=j,
                    y=i,
                    s=str(cm_array[i, j]),
                    va="center",
                    ha="center",
                    size="medium",
                )

        fig.colorbar(cax)
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="left", fontsize=9)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel("Predicted Section Label", fontsize=11, fontweight="bold")
        ax.set_ylabel("True Section Label", fontsize=11, fontweight="bold")
        ax.set_title("Resume Section Classifier - Confusion Matrix", fontsize=13, fontweight="bold", pad=20)
        plt.tight_layout()
        plt.savefig(confusion_matrix_path, dpi=200)
        plt.close()
        print(f"Confusion matrix plot saved to: {confusion_matrix_path}")
    except Exception as e:
        print(f"Plot generation skipped: {e}")

    return metrics_data


if __name__ == "__main__":
    train_and_evaluate()
