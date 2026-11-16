"""
Machine Learning Training & Model Comparison Pipeline
Trains and evaluates:
1. Logistic Regression
2. Decision Tree
3. Random Forest
4. XGBoost

Evaluates: Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
Saves the best-performing model as model.pkl and feature scaler as scaler.pkl.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    classification_report
)

import xgboost as xgb

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / 'data' / 'engine_data.csv'
SAVED_MODELS_DIR = BASE_DIR / 'ml_pipeline' / 'saved_models'
REPORTS_DIR = BASE_DIR / 'reports' / 'eda_figures'
STATIC_ASSETS_DIR = BASE_DIR / 'app' / 'static' / 'assets' / 'eda_charts'

SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def train_and_evaluate():
    print(f"Loading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    feature_cols = [
        'Engine rpm',
        'Lub oil pressure',
        'Fuel pressure',
        'Coolant pressure',
        'lub oil temp',
        'Coolant temp'
    ]
    target_col = 'Engine Condition'
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training samples: {len(X_train):,}, Testing samples: {len(X_test):,}")
    
    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save the fitted scaler
    scaler_path = SAVED_MODELS_DIR / 'scaler.pkl'
    scaler_copy = SAVED_MODELS_DIR / 'feature_scaler.pkl'
    joblib.dump(scaler, scaler_path)
    joblib.dump(scaler, scaler_copy)
    print(f"Fitted scaler saved to: {scaler_path}")
    
    # Define candidate models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=10, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42,
            eval_metric='logloss'
        )
    }
    
    results = []
    trained_models = {}
    roc_data = {}
    
    print("\n" + "="*80)
    print(f"{'Model':<22} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("="*80)
    
    for name, model in models.items():
        # Train
        if name in ['Logistic Regression']:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            # Tree-based algorithms can use unscaled or scaled; using unscaled for tree interpretability
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
            
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc = roc_auc_score(y_test, y_proba)
        
        results.append({
            'Model': name,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1 Score': f1,
            'ROC AUC': roc,
            'Confusion Matrix': confusion_matrix(y_test, y_pred)
        })
        
        trained_models[name] = model
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_data[name] = (fpr, tpr, roc)
        
        print(f"{name:<22} | {acc*100:6.2f}%    | {prec*100:6.2f}%    | {rec*100:6.2f}%    | {f1*100:6.2f}%    | {roc*100:6.2f}%")
        
    print("="*80)
    
    results_df = pd.DataFrame(results)
    
    # -------------------------------------------------------------
    # Select Best Model based on F1-Score & ROC-AUC
    # -------------------------------------------------------------
    # Sorting by F1 Score and ROC AUC
    results_df['Composite Score'] = (results_df['F1 Score'] + results_df['ROC AUC']) / 2
    best_row = results_df.sort_values(by='Composite Score', ascending=False).iloc[0]
    best_model_name = best_row['Model']
    best_model = trained_models[best_model_name]
    
    print(f"\n>>> Best Performing Model: {best_model_name} (Composite: {best_row['Composite Score']*100:.2f}%)")
    
    # Save the best model as model.pkl and failure_prediction_model.pkl
    model_save_path = SAVED_MODELS_DIR / 'model.pkl'
    model_copy_path = SAVED_MODELS_DIR / 'failure_prediction_model.pkl'
    
    # Save model along with metadata dictionary
    model_payload = {
        'model': best_model,
        'model_name': best_model_name,
        'feature_cols': feature_cols,
        'metrics': {
            'accuracy': float(best_row['Accuracy']),
            'precision': float(best_row['Precision']),
            'recall': float(best_row['Recall']),
            'f1_score': float(best_row['F1 Score']),
            'roc_auc': float(best_row['ROC AUC'])
        }
    }
    
    joblib.dump(best_model, model_save_path)
    joblib.dump(best_model, model_copy_path)
    joblib.dump(model_payload, SAVED_MODELS_DIR / 'model_metadata.pkl')
    print(f"Saved best model to: {model_save_path}")
    print(f"Saved duplicate to: {model_copy_path}")
    
    # -------------------------------------------------------------
    # Plot Model Comparison Bar Chart
    # -------------------------------------------------------------
    plt.figure(figsize=(12, 6))
    plot_df = results_df.melt(
        id_vars=['Model'], 
        value_vars=['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC'],
        var_name='Metric', 
        value_name='Score'
    )
    
    sns.barplot(data=plot_df, x='Model', y='Score', hue='Metric', palette='tab10')
    plt.title("Predictive Maintenance: Model Performance Comparison", fontsize=14, fontweight='bold', pad=12)
    plt.ylim(0.5, 1.02)
    plt.ylabel("Score (0.0 to 1.0)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'model_comparison.png', dpi=300)
    plt.savefig(STATIC_ASSETS_DIR / 'model_comparison.png', dpi=300)
    plt.close()
    print("Saved model_comparison.png")
    
    # -------------------------------------------------------------
    # Plot ROC Curves
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 7))
    palette_colors = {'Logistic Regression': '#64748b', 'Decision Tree': '#f59e0b', 'Random Forest': '#10b981', 'XGBoost': '#2563eb'}
    for name, (fpr, tpr, roc) in roc_data.items():
        plt.plot(fpr, tpr, label=f"{name} (AUC = {roc:.4f})", linewidth=2.2, color=palette_colors.get(name, '#000000'))
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random Chance (AUC = 0.5000)')
    plt.title("ROC Curves: Predictive Failure Classification", fontsize=14, fontweight='bold', pad=12)
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Recall / Sensitivity)")
    plt.legend(loc='lower right', frameon=True)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'roc_curves.png', dpi=300)
    plt.savefig(STATIC_ASSETS_DIR / 'roc_curves.png', dpi=300)
    plt.close()
    print("Saved roc_curves.png")
    
    # -------------------------------------------------------------
    # Plot Confusion Matrix of Best Model
    # -------------------------------------------------------------
    plt.figure(figsize=(6, 5))
    cm = best_row['Confusion Matrix']
    sns.heatmap(
        cm, 
        annot=True, 
        fmt='d', 
        cmap='Blues', 
        xticklabels=['Normal (0)', 'Fault (1)'],
        yticklabels=['Normal (0)', 'Fault (1)'],
        cbar=False
    )
    plt.title(f"Confusion Matrix - Best Model ({best_model_name})", fontsize=12, fontweight='bold', pad=12)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Ground Truth Label")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'best_model_confusion_matrix.png', dpi=300)
    plt.savefig(STATIC_ASSETS_DIR / 'best_model_confusion_matrix.png', dpi=300)
    plt.close()
    print("Saved best_model_confusion_matrix.png")
    
    return results_df, best_model_name

if __name__ == '__main__':
    train_and_evaluate()
