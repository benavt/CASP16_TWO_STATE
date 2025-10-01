#!/usr/bin/env python3
"""
Extract Global LDDT from files in a folder (recursive).
Looks for a line containing "Global LDDT" and takes the first float on that line.
Writes: global_lddt.csv with columns: Model,Global_LDDT (0..1)

Example:
  python extract_global_lddt.py --root /path/to/lddt --out global_lddt.csv
"""
import argparse, os, re, glob, csv

def find_float_on_line(line: str):
    m = re.search(r"([0-9]*\.[0-9]+)", line)
    return float(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Folder containing *.lddt/*.txt/*.log")
    ap.add_argument("--out", default="global_lddt.csv")
    args = ap.parse_args()

    files = []
    for ext in ("*.lddt","*.txt","*.log"):
        files += glob.glob(os.path.join(args.root, "**", ext), recursive=True)

    rows = []
    for f in files:
        try:
            with open(f, "r", errors="ignore") as fh:
                score = None
                for line in fh:
                    if "Global LDDT" in line or "global lddt" in line.lower():
                        score = find_float_on_line(line)
                        if score is not None:
                            break
                if score is not None:
                    model = os.path.splitext(os.path.basename(f))[0]
                    rows.append((model, score))
        except Exception:
            continue

    with open(args.out, "w", newline="") as w:
        cw = csv.writer(w)
        cw.writerow(["Model","Global_LDDT"])
        cw.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}")

if __name__ == "__main__":
    main()
