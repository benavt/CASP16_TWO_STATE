#!/usr/bin/env python3
import argparse, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", default="normalized_metrics.csv")
ap.add_argument("--out", default="composite_scores.csv")
ap.add_argument("--gdt-cutoff", type=float, default=80.0)
ap.add_argument("--lddt-cutoff", type=float, default=80.0)
args = ap.parse_args()

df = pd.read_csv(args.inp)

def bin_score(x, cutoff):
    try:
        return 100.0 if float(x) > cutoff else 0.0
    except:
        return 0.0

# CS-1
df["CS1"] = df[["Local_LDDT_normalized","Local_GDT_normalized"]].mean(axis=1, skipna=True)

# CS-2
df["CS2"] = df[["Local_LDDT_normalized","Local_GDT_normalized","Global_LDDT_normalized"]].mean(axis=1, skipna=True)

# CS-3
df["CS3"] = df[["Local_LDDT_normalized","Local_GDT_normalized","Global_LDDT_normalized","Global_GDT_normalized"]].mean(axis=1, skipna=True)

# CS-4 (your original logic)
df["CS4_part_local_lddt"]  = df["Local_LDDT_normalized"]
df["CS4_part_local_gdt"]   = df["Local_GDT_normalized"]
df["CS4_part_global_lddt"] = df["Global_LDDT_normalized"].apply(lambda v: bin_score(v, args.lddt_cutoff))
df["CS4_part_global_gdt"]  = df["Global_GDT_normalized"].apply(lambda v: bin_score(v, args.gdt_cutoff))
df["CS4_part_grms"]        = df["g_RMS_normalized"]

cs4_parts = ["CS4_part_local_lddt","CS4_part_local_gdt","CS4_part_global_lddt","CS4_part_global_gdt","CS4_part_grms"]
df["CS4"] = df[cs4_parts].mean(axis=1, skipna=True)

out = df[["Model","CS1","CS2","CS3","CS4"]]
out.to_csv(args.out, index=False)
print(f"Wrote {args.out}")
