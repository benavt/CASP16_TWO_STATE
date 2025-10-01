#!/usr/bin/env python3
import argparse, pandas as pd, matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--normalized", default="normalized_metrics.csv")
ap.add_argument("--scores", default="composite_scores.csv")
ap.add_argument("--x", default="Global_GDT_normalized")
ap.add_argument("--y", default="CS4", help="Any column from composite_scores.csv, e.g., CS1/CS2/CS3/CS4")
ap.add_argument("--out", default="scatter_diagnostic.png")
args = ap.parse_args()

norm = pd.read_csv(args.normalized)
sc = pd.read_csv(args.scores)
df = norm.merge(sc, on="Model", how="inner")

plt.figure(figsize=(7,6))
plt.scatter(df[args.x], df[args.y])
plt.xlabel(args.x); plt.ylabel(args.y); plt.title(f"{args.x} vs {args.y}")
plt.tight_layout(); plt.savefig(args.out)
print(f"Wrote {args.out}")
