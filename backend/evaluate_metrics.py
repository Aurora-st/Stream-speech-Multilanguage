import argparse
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_curve,
)

matplotlib.use("Agg")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute classification metrics and save ROC/confusion matrix graphs."
    )
    parser.add_argument(
        "--input_csv",
        type=Path,
        required=True,
        help="Input CSV path. Required columns: true_label, pred_score. Optional: pred_label.",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("backend/metrics_output"),
        help="Directory where metrics JSON and plots are saved.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Threshold used to convert pred_score to pred_label if pred_label is missing.",
    )
    parser.add_argument(
        "--auto_tune_threshold",
        action="store_true",
        help="Search thresholds [0.00..1.00] and use the one with highest accuracy.",
    )
    parser.add_argument(
        "--target_accuracy",
        type=float,
        default=0.88,
        help="Target accuracy for reporting (default: 0.88).",
    )
    return parser.parse_args()


def find_best_threshold(y_true: pd.Series, y_score: pd.Series) -> tuple[float, float]:
    best_threshold = 0.5
    best_accuracy = -1.0
    for i in range(0, 101):
        threshold = i / 100.0
        y_pred = (y_score >= threshold).astype(int)
        acc = float(accuracy_score(y_true, y_pred))
        if acc > best_accuracy:
            best_accuracy = acc
            best_threshold = threshold
    return best_threshold, best_accuracy


def main() -> None:
    args = parse_args()
    if not args.input_csv.exists():
        raise FileNotFoundError(f"CSV not found: {args.input_csv}")

    df = pd.read_csv(args.input_csv)
    required_columns = {"true_label", "pred_score"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}. "
            "Expected: true_label, pred_score (and optional pred_label)."
        )

    y_true = df["true_label"].astype(int)
    y_score = df["pred_score"].astype(float)
    used_threshold = args.threshold
    tuned_accuracy = None
    if args.auto_tune_threshold:
        used_threshold, tuned_accuracy = find_best_threshold(y_true, y_score)

    if "pred_label" in df.columns and not args.auto_tune_threshold:
        y_pred = df["pred_label"].astype(int)
    else:
        y_pred = (y_score >= used_threshold).astype(int)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Core metrics
    accuracy = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True)

    # ROC + AUC
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    precision_vals, recall_vals, _ = precision_recall_curve(y_true, y_score)

    # Save ROC curve
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, label=f"ROC curve (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Random baseline")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend(loc="lower right")
    plt.tight_layout()
    roc_path = output_dir / "roc_curve.png"
    plt.savefig(roc_path, dpi=160)
    plt.close()

    # Save precision-recall graph
    plt.figure(figsize=(7, 5))
    plt.plot(recall_vals, precision_vals, label="Precision-Recall curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend(loc="lower left")
    plt.tight_layout()
    pr_path = output_dir / "precision_recall_curve.png"
    plt.savefig(pr_path, dpi=160)
    plt.close()

    # Save confusion matrix graph
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap="Blues", colorbar=False)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    cm_path = output_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=160)
    plt.close()

    metrics_payload = {
        "accuracy": round(float(accuracy), 6),
        "auc": round(float(roc_auc), 6),
        "threshold_used": used_threshold,
        "target_accuracy": args.target_accuracy,
        "target_accuracy_met": float(accuracy) >= args.target_accuracy,
        "tuned_accuracy": round(float(tuned_accuracy), 6) if tuned_accuracy is not None else None,
        "classification_report": report,
        "generated_files": {
            "roc_curve": str(roc_path),
            "confusion_matrix": str(cm_path),
            "precision_recall_curve": str(pr_path),
        },
    }
    metrics_path = output_dir / "classification_metrics.json"
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    print("Metrics generated successfully.")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"AUC      : {roc_auc:.4f}")
    print(f"Threshold: {used_threshold:.2f}")
    if accuracy >= args.target_accuracy:
        print(f"Target   : met (>= {args.target_accuracy:.2f})")
    else:
        print(f"Target   : NOT met (< {args.target_accuracy:.2f})")
    print(f"JSON     : {metrics_path}")
    print(f"ROC PNG  : {roc_path}")
    print(f"PR  PNG  : {pr_path}")
    print(f"CM PNG   : {cm_path}")


if __name__ == "__main__":
    main()
