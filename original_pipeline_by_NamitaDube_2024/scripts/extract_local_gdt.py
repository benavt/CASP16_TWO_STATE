#!/usr/bin/env python3
"""
Compute Local GDT averages per model, optionally within a residue range.
Assumptions (override with flags):
  - Files are delimited (tsv/csv/space); auto-detected by extension.
  - Column 3 = residue index (1-based), Column 6 = local GDT metric to average.

Writes: local_gdt.csv with columns: Model,Local_GDT

Examples:
  python extract_local_gdt.py --root /path/to/local_gdt_tables --out local_gdt.csv
  python extract_local_gdt.py --root /path/to/local_gdt_tables --out local_gdt_297-316.csv --start 297 --end 316
"""
import argparse, os, glob, pandas as pd

def read_any(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".tsv": return pd.read_csv(path, sep="\t", header=None)
    if ext == ".csv": return pd.read_csv(path, sep=",", header=None)
    return pd.read_csv(path, sep=r"\s+", engine="python", header=None)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Folder with per-residue local GDT tables")
    ap.add_argument("--out", required=True, help="Output CSV")
    ap.add_argument("--start", type=int, default=None, help="Start residue (inclusive)")
    ap.add_argument("--end", type=int, default=None, help="End residue (inclusive)")
    ap.add_argument("--res-col", type=int, default=3, help="1-based residue column (default 3)")
    ap.add_argument("--val-col", type=int, default=6, help="1-based value column to average (default 6)")
    ap.add_argument("--glob", default="*.*", help="Glob pattern (default '*.*')")
    ap.add_argument("--prefix-split", default=None, help="Split filename on this char; use prefix as Model")
    args = ap.parse_args()

    files = glob.glob(os.path.join(args.root, "**", args.glob), recursive=True)
    rcol = args.res-col - 1
    vcol = args.val-col - 1

    rows = []
    for f in files:
        try:
            df = read_any(f)
            if max(rcol, vcol) >= df.shape[1]:
                continue
            data = df[[rcol, vcol]].copy()
            data.columns = ["res","val"]
            if args.start is not None and args.end is not None:
                data = data[(data["res"]>=args.start)&(data["res"]<=args.end)]
            if data.empty: continue
            mean_val = pd.to_numeric(data["val"], errors="coerce").dropna().mean()
            if pd.notna(mean_val):
                name = os.path.splitext(os.path.basename(f))[0]
                if args.prefix-split and args.prefix-split in name:
                    name = name.split(args.prefix-split, 1)[0]
                rows.append((name, mean_val))
        except Exception:
            continue

    out = pd.DataFrame(rows, columns=["Model","Local_GDT"]).groupby("Model", as_index=False).mean()
    out.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with {len(out)} rows.")

if __name__ == "__main__":
    main()
