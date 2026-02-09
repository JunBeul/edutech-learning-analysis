"""
Smoke Test — Preprocessing Pipeline

Purpose:
- Verify preprocessing handles midterm snapshot correctly
- Ensure all-NaN columns (e.g., final_score) are filled
- Confirm label generation works

Run:
python scripts/smoke_test_preprocessing.py
"""

import sys
from pathlib import Path

# --- Path setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("PROJECT_ROOT:", PROJECT_ROOT)

# --- Imports ---
from src.preprocessing import load_csv, preprocess_pipeline


def main():

    print("\n[1] Load dummy midterm snapshot data")
    df_raw = load_csv("data/dummy/dummy_midterm_like.csv")
    print("shape:", df_raw.shape)

    print("\n[2] Run preprocessing pipeline")
    df = preprocess_pipeline(df_raw, add_labels=True)

    print("\n[3] Check missing values")
    missing_final = df["final_score"].isna().sum()
    print("final_score missing:", missing_final)

    assert missing_final == 0, (
        "final_score still has NaN values — "
        "all-NaN fallback fill is not working."
    )

    print("\n[4] Check label distribution")
    risk_rate = df["at_risk"].mean()
    print("at_risk rate:", round(risk_rate, 3))

    assert 0 <= risk_rate <= 1, "Invalid risk rate."

    print("\n✅ Smoke test passed — preprocessing is production-ready.")


if __name__ == "__main__":
    main()
