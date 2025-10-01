# Original Modular Composite Score 4 Pipeline (Namita Dube, 2024)

This folder contains the **original modular pipeline** for computing **Composite Score 4 (CS4)** across predicted protein structures.  

**Author:** Namita Dube (2024)  
**Design:** Modular (extract → merge → normalize → score → plot) for clarity and reproducibility.

## Steps (Makefile targets)
1. `make gdt` – parse **Global GDT_TS** and **g_RMS** from LGA outputs.
2. `make glddt` – parse **Global LDDT** from `.lddt` outputs.
3. `make localgdt` – compute **Local GDT** averages for a residue range.
4. `make locallddt` – compute **Local LDDT** averages for a residue range.
5. `make merge` – merge metrics into `combined_results.csv`.
6. `make normalize` – apply sigmoid scaling (g_RMS, Local GDT) and ×100 scaling (LDDT).
7. `make composite` – compute **Composite_Score_4** (mean of 5 parts: Local_LDDT, Local_GDT, binary(Global_LDDT>80), binary(Global_GDT>80), g_RMS).
8. `make plots` – generate bar plots.

> Thresholds (default 80 for Global_GDT and Global_LDDT) are configurable via CLI flags in `compositescores.py`.

## Minimal run order (manual, step-by-step)
```bash
# 1) Extract
python scripts/extract_global_gdt_rms.py --root path/to/LGA_outputs --out global_gdt_rms.csv
python scripts/extract_global_lddt.py    --root path/to/GlobalLDDT_logs --out global_lddt.csv
python scripts/extract_local_gdt.py      --root path/to/local_gdt_tables --out local_gdt.csv --start 23 --end 34
python scripts/extract_local_lddt.py     --root path/to/local_lddt_tables --out local_lddt.csv --start 23 --end 34

# 2) Merge
python scripts/merge_all.py \
  --gdt_rms global_gdt_rms.csv \
  --glddt   global_lddt.csv \
  --local_gdt  local_gdt.csv \
  --local_lddt local_lddt.csv \
  --out combined_results.csv

# 3) Normalize
python scripts/normalize_metrics.py --in combined_results.csv --out normalized_metrics.csv

# 4) Composite scores (CS1–CS4)
python scripts/compositescores.py --in normalized_metrics.csv --out composite_scores.csv --gdt-cutoff 80 --lddt-cutoff 80

# 5) Plots
python scripts/plot_models_bar.py      --csv composite_scores.csv --score CS4 --out models_vs_CS4.png
python scripts/plot_best_per_group.py  --csv composite_scores.csv --score CS4 --out best_per_group_CS4.png
python scripts/plot_scatter_diagnostic.py --normalized normalized_metrics.csv --scores composite_scores.csv \
# Inputs/Outputs
Inputs: LGA outputs (global & local), .lddt outputs
Outputs: CSVs and PNG plots in the working directory (see Makefile and scripts)
# Folder Structure
original_pipeline_by_NamitaDube_2024/
├─ README.md             ← explanation: what this is, how to run
├─ LICENSE               ← license (MIT, with your name + year)
├─ requirements.txt      ← dependencies (pandas, numpy, matplotlib)
├─ Makefile              ← run the full pipeline with make all
├─ scripts/              ← all Python + shell scripts
│   ├─ extract_global_gdt_rms.py
│   ├─ extract_global_lddt.py
│   ├─ extract_local_gdt.py
│   ├─ extract_local_lddt.py
│   ├─ merge_all.py
│   ├─ normalize_metrics.py
│   ├─ compositescores.py
│   ├─ plot_models_bar.py
│   ├─ plot_best_per_group.py
│   └─ plot_scatter_diagnostic.py
├─ data/                 ← (optional) raw inputs
├─ outputs/              ← (optional) generated results (CSVs, PNGs)
└─ .gitignore            ← ignore caches/outputs when committing
#Reproducibility Note
Python ≥3.8 recommended
Requires: pandas, numpy, matplotlib
Local GDT/LDDT residue ranges configurable via CLI (--start, --end)
Composite score thresholds configurable (--gdt-cutoff, --lddt-cutoff)
#License
MIT License
Copyright (c) 2024 Namita Dube
Permission is hereby granted, free of charge, to any person obtaining a copy of this work and associated documentation files (the "Work"), to deal in the Work without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Work, and to permit persons to whom the Work is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Work.
THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS IN THE WORK.
     --x Global_GDT_normalized --y CS4 --out scatter_GGDT_vs_CS4.png
