#!/usr/bin/env python3
"""
Extract Global GDT_TS and g_RMS from LGA output files in a given folder (recursive).
Writes: global_gdt_rms.csv with columns: Model,Global_GDT,g_RMS

Example:
  python extract_global_gdt_rms.py --root /path/to/lga --out global_gdt_rms.csv
"""
import argparse, os, re, glob, csv
from typing import Optional, Tuple

def parse_global_gdt(line: str) -> Optional[float]:
    for pat in [r"GDT[_\s]?TS[=\s:]+([0-9]+(?:\.[0-9]+)?)", r"\bGDT[=\s:]+([0-9]+(?:\.[0-9]+)?)"]:
        m = re.search(pat, line)
        if m: return float(m.group(1))
    return None

def parse_grms(line: str) -> Optional[float]:
    for pat in [r"g[_\s]?RMS[=\s:]+([0-9]+(?:\.[0-9]+)?)", r"\bRMSD[=\s:]+([0-9]+(?:\.[0-9]+)?)"]:
        m = re.search(pat, line)
        if m: return float(m.group(1))
    return None

def extract_from_file(path: str) -> Tuple[Optional[float], Optional[float]]:
    gdt = None
    grms = None
    with open(path, "r", errors="ignore") as f:
      for line in f:
        if "GDT" in line:
            gdt = gdt or parse_global_gdt(line)
        if "RMS" in line or "RMSD" in line:
            grms = grms or parse_grms(line)
    return gdt, grms

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Folder containing LGA outputs (*.lga/*.txt)")
    ap.add_argument("--out", default="global_gdt_rms.csv")
    args = ap.parse_args()

    files = []
    for ext in ("*.lga","*.txt"):
        files += glob.glob(os.path.join(args.root, "**", ext), recursive=True)

    rows = []
    for fp in files:
        model = os.path.splitext(os.path.basename(fp))[0]
        gdt, grms = extract_from_file(fp)
        if gdt is not None and grms is not None:
            rows.append((model, gdt, grms))

    with open(args.out, "w", newline="") as w:
        cw = csv.writer(w)
        cw.writerow(["Model","Global_GDT","g_RMS"])
        cw.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}")

if __name__ == "__main__":
    main()
