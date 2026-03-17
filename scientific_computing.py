import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from numpy import percentile
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_data(data: list, column_names: list = None):
    print("Running statistical analysis...")

    df = pd.DataFrame(data, columns=column_names) if column_names else pd.DataFrame(data)

    analysis = {}

    for col in df.select_dtypes(include=[np.number]).columns:
        col_data = df[col].dropna()
        analysis[col] = {
            "count": len(col_data),
            "mean": round(float(col_data.mean()), 4),
            "median": round(float(col_data.median()), 4),
            "std": round(float(col_data.std()), 4),
            "min": round(float(col_data.min()), 4),
            "max": round(float(col_data.max()), 4),
            "variance": round(float(col_data.var()), 4),
            "skewness": round(float(col_data.skew()), 4),
            "kurtosis": round(float(col_data.kurtosis()), 4),
            "q25": round(float(col_data.quantile(0.25)), 4),
            "q75": round(float(col_data.quantile(0.75)), 4)
        }

    return analysis

def detect_outliers(data: list, threshold: float = 2.0):
    arr = np.array(data)
    z_scores = np.abs((arr - np.mean(arr)) / np.std(arr))
    outlier_indices = np.where(z_scores > threshold)[0].tolist()
    outlier_values = arr[outlier_indices].tolist()

    print(f"Outlier detection — threshold: {threshold} std devs")
    print(f"Found {len(outlier_indices)} outliers")

    return {
        "outlier_count": len(outlier_indices),
        "outlier_indices": outlier_indices,
        "outlier_values": outlier_values,
        "threshold": threshold,
        "total_points": len(data)
    }

def linear_regression_analysis(x_data: list, y_data: list, x_label: str = "X", y_label: str = "Y"):
    print("Running linear regression...")

    x = np.array(x_data).reshape(-1, 1)
    y = np.array(y_data)

    model = LinearRegression()
    model.fit(x, y)

    y_pred = model.predict(x)
    r_squared = model.score(x, y)

    slope = float(model.coef_[0])
    intercept = float(model.intercept_)

    residuals = y - y_pred
    rmse = float(np.sqrt(np.mean(residuals**2)))

    print(f"R² score: {round(r_squared, 4)}")
    print(f"Slope: {round(slope, 4)}")
    print(f"Intercept: {round(intercept, 4)}")

    plt.figure(figsize=(10, 6))
    plt.scatter(x_data, y_data, color='#6366f1', alpha=0.7, label='Data points')
    plt.plot(x_data, y_pred, color='#00ff88', linewidth=2, label=f'Regression line (R²={round(r_squared, 3)})')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f'Linear Regression: {y_label} vs {x_label}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    filename = f"regression_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    plt.close()
    print(f"Chart saved: {filename}")

    return {
        "r_squared": round(r_squared, 4),
        "slope": round(slope, 4),
        "intercept": round(intercept, 4),
        "rmse": round(rmse, 4),
        "equation": f"{y_label} = {round(slope, 4)} * {x_label} + {round(intercept, 4)}",
        "chart_file": filename
    }

def cluster_analysis(data: list, n_clusters: int = 3):
    print(f"Running K-means clustering with {n_clusters} clusters...")

    arr = np.array(data)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(arr)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled)

    clusters = {}
    for i in range(n_clusters):
        cluster_data = arr[labels == i]
        clusters[f"cluster_{i+1}"] = {
            "size": len(cluster_data),
            "mean": round(float(cluster_data.mean()), 4),
            "std": round(float(cluster_data.std()), 4)
        }
        print(f"  Cluster {i+1}: {len(cluster_data)} points, mean={round(float(cluster_data.mean()), 4)}")

    return {
        "n_clusters": n_clusters,
        "labels": labels.tolist(),
        "clusters": clusters,
        "inertia": round(float(kmeans.inertia_), 4)
    }

def visualize_data(data: list, chart_type: str = "histogram", title: str = "Data Visualization", labels: list = None):
    print(f"Creating {chart_type} visualization...")

    plt.figure(figsize=(10, 6))
    plt.style.use('dark_background')

    if chart_type == "histogram":
        plt.hist(data, bins=20, color='#6366f1', edgecolor='#8b5cf6', alpha=0.8)
        plt.xlabel("Value")
        plt.ylabel("Frequency")

    elif chart_type == "line":
        plt.plot(data, color='#00ff88', linewidth=2)
        plt.xlabel("Index")
        plt.ylabel("Value")

    elif chart_type == "bar":
        x = labels or list(range(len(data)))
        plt.bar(x, data, color='#6366f1', edgecolor='#8b5cf6', alpha=0.8)
        plt.xlabel("Category")
        plt.ylabel("Value")
        if labels:
            plt.xticks(rotation=45)

    elif chart_type == "scatter":
        if isinstance(data[0], (list, tuple)):
            x = [d[0] for d in data]
            y = [d[1] for d in data]
        else:
            x = list(range(len(data)))
            y = data
        plt.scatter(x, y, color='#6366f1', alpha=0.7)
        plt.xlabel("X")
        plt.ylabel("Y")

    elif chart_type == "pie":
        chart_labels = labels or [f"Item {i+1}" for i in range(len(data))]
        colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']
        plt.pie(data, labels=chart_labels, colors=colors[:len(data)],
                autopct='%1.1f%%', startangle=90)

    plt.title(title, color='white', pad=15)
    plt.tight_layout()
    filename = f"chart_{chart_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()
    print(f"Chart saved: {filename}")
    return filename

def ai_data_insights(data: list, analysis: dict):
    prompt = f"""You are a data scientist. Analyze these statistics and provide insights.

Data sample (first 10 values): {data[:10]}
Statistical analysis: {json.dumps(analysis, indent=2)[:2000]}

Provide insights about this data.

Return ONLY a JSON object:
{{
    "data_quality": "<good, fair, or poor>",
    "distribution": "<normal, skewed, bimodal, or uniform>",
    "key_insights": ["<insight1>", "<insight2>", "<insight3>"],
    "anomalies": ["<anomaly1>"],
    "recommendations": ["<recommendation1>", "<recommendation2>"],
    "business_interpretation": "<what this data means in plain English>"
}}

Return ONLY the JSON. No extra text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except:
        return {}

def automate_research(topic: str):
    print(f"Automating research on: {topic}")

    prompt = f"""You are a research assistant. Provide a comprehensive analysis of this topic.

Topic: {topic}

Return ONLY a JSON object:
{{
    "topic": "{topic}",
    "summary": "<comprehensive summary>",
    "key_findings": ["<finding1>", "<finding2>", "<finding3>"],
    "statistics": ["<stat1>", "<stat2>"],
    "methodologies": ["<method1>", "<method2>"],
    "applications": ["<application1>", "<application2>"],
    "future_directions": ["<direction1>", "<direction2>"],
    "references": ["<reference1>", "<reference2>"]
}}

Return ONLY the JSON. No extra text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except:
        return {}

if __name__ == "__main__":
    print("=" * 40)
    print("  Scientific Computing Suite")
    print("=" * 40)
    print()
    print("1. Statistical analysis")
    print("2. Linear regression")
    print("3. Cluster analysis")
    print("4. Data visualization")
    print("5. Research automation")
    print()
    choice = input("Choose (1-5): ").strip()

    if choice == "1":
        data = [23, 45, 12, 67, 34, 89, 56, 23, 45, 78,
                34, 56, 89, 23, 45, 67, 12, 89, 34, 56]
        analysis = analyze_data([data], ["values"])
        outliers = detect_outliers(data)
        insights = ai_data_insights(data, analysis)

        print("\nStatistical Analysis:")
        for col, stats_data in analysis.items():
            print(f"\n{col}:")
            for key, value in stats_data.items():
                print(f"  {key}: {value}")

        print(f"\nOutliers: {outliers['outlier_count']} found")
        if outliers['outlier_values']:
            print(f"Values: {outliers['outlier_values']}")

        print(f"\nAI Insights:")
        print(f"Distribution: {insights.get('distribution', 'unknown')}")
        print(f"Data quality: {insights.get('data_quality', 'unknown')}")
        if insights.get('key_insights'):
            print("Key insights:")
            for insight in insights['key_insights']:
                print(f"  - {insight}")

    elif choice == "2":
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2.1, 4.3, 5.8, 8.2, 9.9, 12.1, 14.3, 15.8, 18.2, 19.9]
        result = linear_regression_analysis(x, y, "Time", "Revenue")
        print(f"\nEquation: {result['equation']}")
        print(f"R² Score: {result['r_squared']}")
        print(f"RMSE: {result['rmse']}")
        print(f"Chart: {result['chart_file']}")

    elif choice == "3":
        data = [2, 3, 2.5, 8, 9, 8.5, 15, 16, 15.5,
                2.1, 8.2, 15.2, 3, 9, 16, 2.8, 8.8, 15.8]
        result = cluster_analysis(data, n_clusters=3)
        print(f"\nClusters found: {result['n_clusters']}")
        for name, info in result['clusters'].items():
            print(f"  {name}: {info['size']} points, mean={info['mean']}")

    elif choice == "4":
        data = [23, 45, 12, 67, 34, 89, 56, 23, 45, 78,
                34, 56, 89, 23, 45, 67, 12, 89, 34, 56]
        print("Chart types: histogram, line, bar, scatter, pie")
        chart_type = input("Chart type: ").strip() or "histogram"
        filename = visualize_data(data, chart_type, "Sample Data Visualization")
        print(f"Chart saved: {filename}")

    elif choice == "5":
        topic = input("Research topic: ").strip()
        result = automate_research(topic)
        print(f"\nTopic: {result.get('topic', '')}")
        print(f"Summary: {result.get('summary', '')[:200]}...")
        if result.get('key_findings'):
            print("\nKey findings:")
            for finding in result['key_findings']:
                print(f"  - {finding}")
