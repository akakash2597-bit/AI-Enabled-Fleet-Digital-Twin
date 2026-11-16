"""
Exploratory Data Analysis (EDA) Script
Automotive Vehicles Engine Health Dataset
Generates comprehensive statistical summaries, charts, and quality metrics.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / 'data' / 'engine_data.csv'
OUTPUT_DIR = BASE_DIR / 'reports' / 'eda_figures'
STATIC_OUTPUT_DIR = BASE_DIR / 'app' / 'static' / 'assets' / 'eda_charts'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
STATIC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_eda():
    print(f"Loading dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    sensor_cols = [c for c in df.columns if c != 'Engine Condition']
    target_col = 'Engine Condition'
    
    print(f"Dataset shape: {df.shape}")
    
    # -------------------------------------------------------------
    # 1. Class Distribution & Imbalance Chart
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    class_counts = df[target_col].value_counts()
    class_labels = ['Fault / Maintenance Needed (1)', 'Normal / Operational (0)']
    ordered_counts = [class_counts.get(1, 0), class_counts.get(0, 0)]
    colors = ['#ef4444', '#10b981']
    
    # Bar chart
    bars = axes[0].bar(class_labels, ordered_counts, color=colors, width=0.5, edgecolor='#334155', linewidth=1.2)
    for bar in bars:
        yval = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2.0, yval + 200, f"{yval:,} ({yval/len(df)*100:.1f}%)", ha='center', va='bottom', fontweight='bold')
    axes[0].set_title("Failure Distribution (Record Count)", fontsize=13, fontweight='bold', pad=12)
    axes[0].set_ylabel("Number of Engine Records")
    axes[0].set_ylim(0, max(ordered_counts) * 1.15)
    
    # Donut chart
    wedges, texts, autotexts = axes[1].pie(
        ordered_counts, 
        labels=class_labels, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors,
        wedgeprops=dict(width=0.45, edgecolor='#ffffff', linewidth=2),
        textprops=dict(fontweight='bold')
    )
    for at in autotexts:
        at.set_color('white')
        at.set_fontsize(11)
    axes[1].set_title("Class Imbalance Ratio", fontsize=13, fontweight='bold', pad=12)
    
    plt.tight_layout()
    chart1_path = OUTPUT_DIR / 'class_imbalance.png'
    plt.savefig(chart1_path, dpi=300)
    plt.savefig(STATIC_OUTPUT_DIR / 'class_imbalance.png', dpi=300)
    plt.close()
    print("Saved class_imbalance.png")
    
    # -------------------------------------------------------------
    # 2. Correlation Matrix Heatmap
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 7))
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(
        corr, 
        mask=mask,
        annot=True, 
        fmt=".2f", 
        cmap=cmap, 
        vmax=1.0, 
        vmin=-1.0, 
        center=0,
        square=True, 
        linewidths=0.8, 
        cbar_kws={"shrink": 0.8}
    )
    plt.title("Correlation Matrix: Engine Sensors & Failure Condition", fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'correlation_matrix.png', dpi=300)
    plt.savefig(STATIC_OUTPUT_DIR / 'correlation_matrix.png', dpi=300)
    plt.close()
    print("Saved correlation_matrix.png")
    
    # -------------------------------------------------------------
    # 3. Sensor Feature Histograms (Distributions)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.flatten()
    
    palette = ['#10b981', '#ef4444']
    for idx, col in enumerate(sensor_cols):
        ax = axes[idx]
        sns.histplot(
            data=df, 
            x=col, 
            hue=target_col, 
            kde=True, 
            palette=palette, 
            ax=ax, 
            element='step', 
            stat='density',
            common_norm=False,
            alpha=0.4
        )
        ax.set_title(f"Distribution of {col}", fontsize=11, fontweight='bold')
        ax.set_xlabel(col)
        ax.set_ylabel("Density")
        # Format legend
        handles, _ = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles=handles, labels=['Fault (1)', 'Normal (0)'], title="Engine Condition")
            
    plt.suptitle("Sensor Telemetry Distributions by Engine Condition", fontsize=15, fontweight='bold', y=0.99)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'histograms.png', dpi=300)
    plt.savefig(STATIC_OUTPUT_DIR / 'histograms.png', dpi=300)
    plt.close()
    print("Saved histograms.png")
    
    # -------------------------------------------------------------
    # 4. Boxplots for Outlier & Spread Analysis
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.flatten()
    
    for idx, col in enumerate(sensor_cols):
        ax = axes[idx]
        sns.boxplot(
            data=df, 
            x=target_col, 
            y=col, 
            hue=target_col,
            palette=['#10b981', '#ef4444'], 
            ax=ax,
            legend=False,
            flierprops=dict(marker='o', markersize=3, alpha=0.3)
        )
        ax.set_title(f"{col} by Failure State", fontsize=11, fontweight='bold')
        ax.set_xticklabels(['Normal (0)', 'Fault (1)'])
        ax.set_xlabel("Engine Condition")
        ax.set_ylabel(col)
        
    plt.suptitle("Sensor Parameter Boxplots & Outliers Across Engine Health States", fontsize=15, fontweight='bold', y=0.99)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'boxplots.png', dpi=300)
    plt.savefig(STATIC_OUTPUT_DIR / 'boxplots.png', dpi=300)
    plt.close()
    print("Saved boxplots.png")
    
    # -------------------------------------------------------------
    # 5. Feature Importance Suggestions (Random Forest + Mutual Information)
    # -------------------------------------------------------------
    X = df[sensor_cols]
    y = df[target_col]
    
    # Random Forest Gini Importance
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    rf_importance = pd.Series(rf.feature_importances_, index=sensor_cols).sort_values(ascending=False)
    
    # Mutual Information Score
    mi_scores = mutual_info_classif(X, y, random_state=42)
    mi_importance = pd.Series(mi_scores, index=sensor_cols).sort_values(ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    
    sns.barplot(x=rf_importance.values, y=rf_importance.index, ax=axes[0], palette="viridis")
    axes[0].set_title("Random Forest Gini Feature Importance", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Mean Decrease in Impurity")
    for i, v in enumerate(rf_importance.values):
        axes[0].text(v + 0.005, i, f"{v*100:.1f}%", va='center', fontweight='bold', color='#1e293b')
        
    sns.barplot(x=mi_importance.values, y=mi_importance.index, ax=axes[1], palette="magma")
    axes[1].set_title("Mutual Information Score (Non-linear Dependency)", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Mutual Information Metric")
    for i, v in enumerate(mi_importance.values):
        axes[1].text(v + 0.005, i, f"{v:.3f}", va='center', fontweight='bold', color='#1e293b')
        
    plt.suptitle("Feature Importance Ranking & Breakdown for Predictive Maintenance", fontsize=14, fontweight='bold', y=0.99)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'feature_importance.png', dpi=300)
    plt.savefig(STATIC_OUTPUT_DIR / 'feature_importance.png', dpi=300)
    plt.close()
    print("Saved feature_importance.png")
    
    # -------------------------------------------------------------
    # 6. Critical Anomaly Scatter Plot: Thermal & Hydraulic Degradation
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df, 
        x='Coolant temp', 
        y='lub oil temp', 
        hue=target_col, 
        palette=['#10b981', '#ef4444'], 
        alpha=0.6,
        s=30
    )
    plt.title("Coupled Thermal Behavior: Coolant Temp vs Lubrication Oil Temp", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Coolant Temperature (°C)")
    plt.ylabel("Lubrication Oil Temperature (°C)")
    plt.legend(title="Engine Condition", labels=['Normal (0)', 'Fault (1)'])
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'thermal_anomaly_scatter.png', dpi=300)
    plt.savefig(STATIC_OUTPUT_DIR / 'thermal_anomaly_scatter.png', dpi=300)
    plt.close()
    print("Saved thermal_anomaly_scatter.png")
    
    print("EDA execution completed successfully.")

if __name__ == '__main__':
    run_eda()
