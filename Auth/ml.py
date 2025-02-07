# ml_model.py

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from Auth.models import Feedback

def train_transporter_model():
    """
    Train an ML model to predict the best transporter based on feedback.
    """
    # Load feedback data from database
    feedback_data = list(Feedback.objects.all().values("transporter", "rating", "delivery_time", "success","price"))
    if not feedback_data:
        return None  # No data to train on

    # Convert to Pandas DataFrame
    df = pd.DataFrame(feedback_data)

    # Features (X) and Target (y)
    X = df[["rating", "delivery_time","price"]]  # Features: Feedback data
    y = df["success"]  # Target: Whether the delivery was successful

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train RandomForest Model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    return model
