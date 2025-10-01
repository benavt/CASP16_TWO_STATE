#!/usr/bin/env python3
"""
Compute Local LDDT averages per model, optionally within a residue range.

Assumptions (override with flags):
  - Files are delimited (tsv/csv/space); auto-detected by extension.
  - Column 1 = residue index (1-based), Column 2 = local LDDT value (0..1).

Writes: local_lddt.csv with columns: Model,Local_LDDT

Examples:
  python extract_local_lddt.py --root /path/to/local_lddt --out local_lddt.csv
  python extract_local_lddt.py --root /path/to/local_lddt --out local_lddt_297-316.csv --start 297 --end 316
"""
import argparse, os, glob, pandas as pd

def read_any(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".tsv": return pd.read_csv(path, sep="\t", header=None)
    if ext == ".csv": return pd.read_csv(path, sep=",", header=None)
    return pd.read_csv(path, sep=r"\s+", engine="python", header=None)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Folder with per-residue Local LDDT tables")
    ap.add_argument("--out", required=True, help="Output CSV")
    ap.add_argument("--start", type=int, default=None, help="Start residue (inclusive)")
    ap.add_argument("--end", type=int, default=None, help="End residue (inclusive)")
    ap.add_argument("--res-col", type=int, default=1, help="1-based residue column (default 1)")
    ap.add_argument("--val-col", type=int, default=2, help="1-based LDDT value column (default 2)")
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
            data.columns = ["res","lddt"]
            if args.start is not None and args.end is not None:
                data = data[(data["res"]>=args.start)&(data["res"]<=args.end)]
            if data.empty: continue
            mean_val = pd.to_numeric(data["lddt"], errors="coerce").dropna().mean()  # expected 0..1
            if pd.notna(mean_val):
                name = os.path.splitext(os.path.basename(f))[0]
                if args.prefix-split and args.prefix-split in name:
                    name = name.split(args.prefix-split, 1)[0]
                rows.append((name, mean_val))
        except Exception:
            continue

    out = pd.DataFrame(rows, columns=["Model","Local_LDDT"]).groupby("Model", as_index=False).mean()
    out.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with {len(out)} rows.")

if __name__ == "__main__":
    main()
