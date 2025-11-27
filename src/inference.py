import os
import pandas as pd
from pathlib import Path

def dummy_predict(path):
    return "NoFinding"

def main(input_dir="test_images", output_csv="submission.csv"):
    input_dir = Path(input_dir)
    rows = []

    for f in input_dir.iterdir():
        if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".dcm"]:
            pred = dummy_predict(f)
            rows.append({"id": f.stem, "prediction": pred})

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print("Saved:", output_csv)

if __name__ == "__main__":
    main()
