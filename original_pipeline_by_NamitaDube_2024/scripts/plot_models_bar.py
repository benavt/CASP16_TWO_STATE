#!/usr/bin/env python3
import argparse, pandas as pd, matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="composite_scores.csv")
ap.add_argument("--score", default="CS4", help="Which score to plot: CS1/CS2/CS3/CS4")
ap.add_argument("--out", default="models_vs_score.png")
args = ap.parse_args()

df = pd.read_csv(args.csv).sort_values(args.score, ascending=False)
plt.figure(figsize=(10,6))
plt.bar(df["Model"], df[args.score])
plt.xlabel("Model"); plt.ylabel(args.score); plt.title(f"Models vs {args.score}")
plt.xticks(rotation=90); plt.tight_layout()
plt.savefig(args.out); print(f"Wrote {args.out}")
