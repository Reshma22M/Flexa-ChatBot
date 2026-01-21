# train.py
# Flexa: Train & save a KNN model bundle (pipeline + dataset) from gymdataset.xlsx

import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier


# ✅ Update these if your folder names differ
DATA_PATH = os.path.join("data", "gymdataset.xlsx")
MODEL_PATH = os.path.join("models", "flexa_plan_model.joblib")


def load_dataset(path: str) -> pd.DataFrame:
    """
    Loads the Excel dataset and performs minimal cleaning:
    - strips column names
    - normalizes Yes/No fields
    - checks required columns exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at '{path}'.\n"
            f"Make sure your file is located at: {os.path.abspath(path)}"
        )

    df = pd.read_excel(path)

    # Stronger column cleanup (handles hidden spaces/newlines)
    df.columns = df.columns.astype(str).str.replace("\n", " ").str.strip()

    required = [
        "ID", "Sex", "Age", "Height", "Weight",
        "Hypertension", "Diabetes", "BMI", "Level",
        "Fitness Goal", "Fitness Type", "Exercises", "Equipment", "Diet", "Recommendation"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing columns in dataset:\n"
            f"{missing}\n\n"
            f"Available columns are:\n{list(df.columns)}"
        )

    # Normalize Yes/No fields
    for col in ["Hypertension", "Diabetes"]:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].map(lambda x: "Yes" if x in ["yes", "y", "true", "1"] else "No")

    # Normalize Sex
    df["Sex"] = df["Sex"].astype(str).str.strip().str.capitalize()

    # Ensure numeric columns are numeric (convert errors to NaN)
    for col in ["Age", "Height", "Weight", "BMI"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clean Level text
    df["Level"] = df["Level"].astype(str).str.strip().str.capitalize()

    return df


def train_and_save():
    """
    Trains a KNN classifier to map (Sex, Age, Height, Weight, Hypertension, Diabetes, BMI, Level)
    -> nearest plan ID from your dataset, then saves a joblib bundle:
      {
        "pipeline": trained_pipeline,
        "dataset": original_dataframe
      }
    """
    os.makedirs("models", exist_ok=True)

    df = load_dataset(DATA_PATH)

    feature_cols = ["Sex", "Age", "Height", "Weight", "Hypertension", "Diabetes", "BMI", "Level"]
    X = df[feature_cols].copy()
    y = df["ID"]  # Target is plan ID

    categorical = ["Sex", "Hypertension", "Diabetes", "Level"]
    numeric = ["Age", "Height", "Weight", "BMI"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]), numeric),
            ("cat", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ]), categorical),
        ]
    )

    model = KNeighborsClassifier(
        n_neighbors=5,
        weights="distance"
    )

    pipeline = Pipeline(steps=[
        ("prep", preprocessor),
        ("knn", model)
    ])

    # ✅ IMPORTANT: Do NOT use stratify=y because IDs are usually unique per row
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)

    bundle = {
        "pipeline": pipeline,
        "dataset": df
    }

    joblib.dump(bundle, MODEL_PATH)

    print("✅ Training complete!")
    print("✅ Model saved to:", os.path.abspath(MODEL_PATH))
    print("ℹ️ Dataset rows:", len(df))
    print("ℹ️ Features used:", feature_cols)


if __name__ == "__main__":
    train_and_save()
