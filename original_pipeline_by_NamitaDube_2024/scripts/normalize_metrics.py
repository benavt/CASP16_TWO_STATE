#!/usr/bin/env python3
import argparse, pandas as pd, numpy as np

def sigmoid_normalize(value, L=105.0, k=-0.77, x0=3.77):
    try:
        v = float(value)
    except:
        return np.nan
    return L / (1 + np.exp(-k * (v - x0)))

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", default="combined_results.csv")
ap.add_argument("--out", default="normalized_metrics.csv")
args = ap.parse_args()

df = pd.read_csv(args.inp)
for col in ["g_RMS","Local_GDT","Global_LDDT","Global_GDT","Local_LDDT"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["g_RMS_normalized"]       = df["g_RMS"].apply(sigmoid_normalize)
df["Local_GDT_normalized"]   = df["Local_GDT"].apply(sigmoid_normalize)
df["Global_LDDT_normalized"] = df["Global_LDDT"] * 100.0     # expect 0..1 → 0..100
df["Local_LDDT_normalized"]  = df["Local_LDDT"] * 100.0      # expect 0..1 → 0..100
df["Global_GDT_normalized"]  = df["Global_GDT"]               # usually already 0..100

out = df[["Model",
          "Global_GDT_normalized",
          "g_RMS_normalized",
          "Global_LDDT_normalized",
          "Local_GDT_normalized",
          "Local_LDDT_normalized"]]

out.to_csv(args.out, index=False)
print(f"Wrote {args.out}")
