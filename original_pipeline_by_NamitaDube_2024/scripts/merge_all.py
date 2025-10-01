#!/usr/bin/env python3
"""
Merge global/local metrics into one CSV.

Inputs (CSV headers expected):
  --gdt_rms     : Model,Global_GDT,g_RMS
  --glddt       : Model,Global_LDDT
  --local_gdt   : Model,Local_GDT
  --local_lddt  : Model,Local_LDDT

Output:
  combined_results.csv with columns:
    Model, Global_GDT, g_RMS, Global_LDDT, Local_GDT, Local_LDDT
"""
import argparse, pandas as pd

def read_csv(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    if "Structure" in df.columns and "Model" not in df.columns:
        df.rename(columns={"Structure":"Model"}, inplace=True)
    df["Model"] = df["Model"].astype(str).str.strip()
    return df

ap = argparse.ArgumentParser()
ap.add_argument("--gdt_rms", required=True)
ap.add_argument("--glddt", required=True)
ap.add_argument("--local_gdt", required=True)
ap.add_argument("--local_lddt", required=True)
ap.add_argument("--out", default="combined_results.csv")
args = ap.parse_args()

gdt = read_csv(args.gdt_rms)
glddt = read_csv(args.glddt)
lgdt = read_csv(args.local_gdt)
lldt = read_csv(args.local_lddt)

merged = (
    gdt
    .merge(glddt[["Model","Global_LDDT"]], on="Model", how="inner")
    .merge(lgdt[["Model","Local_GDT"]], on="Model", how="inner")
    .merge(lldt[["Model","Local_LDDT"]], on="Model", how="inner")
)

merged.to_csv(args.out, index=False)
print(f"Wrote {args.out} with {len(merged)} rows.")
