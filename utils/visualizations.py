import os
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns

def ensure_dir(path="outputs/charts/"):
    os.makedirs(path, exist_ok=True)

#histogram
def plot_hist(df, column, output_path):
    ensure_dir()
    plt.figure(figsize=(8,5))
    sns.histplot(df[column].dropna(), kde=True)
    plt.title(f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.savefig(output_path)
    plt.close()

#barplot
def plot_bar(df, column, output_path):
    ensure_dir()
    plt.figure(figsize=(8, 5))
    df[column].value_counts().plot(kind="bar")
    plt.title(f"Bar Plot of {column}")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.savefig(output_path)
    plt.close()

#genre count plot
def plot_genre_count(df, output_path):
    ensure_dir()
    #split genres into individual rows
    genre_series = (
        df["listed_in"].dropna().str.split(", ").explode()
    )
    top_genres = genre_series.value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_genres.values, y=top_genres.index)
    plt.title("Top 10 genres")
    plt.xlabel("Count")
    plt.ylabel("Genre")
    plt.savefig(output_path)
    plt.close()

#correlation heat map
def plot_corr_hm(corr, output_path):
    ensure_dir()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.savefig(output_path)
    plt.close()

#box plot
def plot_box(df, column, output_path):
    ensure_dir()
    plt.figure(figsize=(6, 5))
    sns.boxplot(x=df[column].dropna())
    plt.title(f"Boxplot of {column}")
    plt.xlabel(column)
    plt.savefig(output_path)
    plt.close()
