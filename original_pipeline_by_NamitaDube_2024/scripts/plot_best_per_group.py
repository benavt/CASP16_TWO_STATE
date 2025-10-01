#!/usr/bin/env python3
import argparse, pandas as pd, matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="composite_scores.csv")
ap.add_argument("--score", default="CS4")
ap.add_argument("--out", default="best_per_group.png")
args = ap.parse_args()

df = pd.read_csv(args.csv)
df["Group"] = df["Model"].str.extract(r"(TS\d+)_")
best = df.groupby("Group", dropna=True)[args.score].max().reset_index().sort_values(args.score, ascending=False)

plt.figure(figsize=(10,6))
plt.bar(best["Group"], best[args.score])
plt.xlabel("Group"); plt.ylabel(args.score); plt.title(f"Best {args.score} per Group")
plt.xticks(rotation=90); plt.tight_layout()
plt.savefig(args.out); print(f"Wrote {args.out}")
