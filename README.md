# CASP16 Two-State Assessment

This repository contains scripts and analysis tools for evaluating protein structure predictions in CASP16 (Critical Assessment of Structure Prediction) targets with two-state conformations. The analysis focuses on comparing predictions against two different reference structures (V1A and V1B) for various targets.

## Overview

The repository implements a comprehensive analysis pipeline for CASP16 targets that exhibit two-state conformations. It processes and combines scores from different reference structures and model versions, generating both quantitative metrics and visualizations for assessment.

### Key Features

- Analysis of multiple CASP16 targets (T1228, T1239, T1249, M1228, M1239)
- Support for various assessment metrics:
  - Global GDT (Global Distance Test)
  - lDDT (local Distance Difference Test)
  - TM-score
  - TM-align
- Generation of combined scores for two-state conformations
- Visualization tools for comparing predictions against different reference structures
- Automated plotting of scatter plots and stacked bar charts

## Repository Structure

```
.
├── PLOTS/                  # Directory containing generated plots
├── T1228/                  # Analysis for target T1228
│   ├── get_global_gdt.py   # Global GDT score analysis
│   ├── get_lddt.py         # lDDT score analysis
│   └── get_combined_metric.py  # Combined metric analysis
├── T1239/                  # Analysis for target T1239
├── T1249/                  # Analysis for target T1249
├── M1228/                  # Analysis for target M1228
├── M1239/                  # Analysis for target M1239
└── run_all_scripts.py      # Main script to run all analyses
```

## Analysis Pipeline

Each target directory contains scripts that:

1. Load prediction scores from CSV files
2. Process scores for different model versions (v1 and v2)
3. Combine scores from different reference structures
4. Generate visualizations:
   - Scatter plots comparing V1A vs V1B scores
   - Stacked bar charts showing combined scores
5. Save results as CSV files and plots

### Key Metrics

- **Global GDT**: Measures structural similarity between predicted and reference structures
- **lDDT**: Local Distance Difference Test for evaluating local structure quality
- **TM-score**: Template Modeling score for structural similarity
- **Combined Score**: Sum of best scores from both reference structures

## Usage

1. Ensure all required Python packages are installed:
   ```bash
   pip install pandas matplotlib adjustText
   ```

2. Run the analysis for all targets:
   ```bash
   python run_all_scripts.py
   ```

3. For individual target analysis, navigate to the target directory and run the specific script:
   ```bash
   cd T1228
   python get_global_gdt.py
   ```

## Output

The analysis generates:

1. CSV files containing:
   - Combined scores for each group
   - Best scores against each reference structure
   - Model versions used for best predictions

2. Visualization plots in the `PLOTS/` directory:
   - Scatter plots comparing V1A vs V1B scores
   - Stacked bar charts showing combined scores
   - All plots include proper labeling and legends

## Dependencies

- Python 3.x
- pandas
- matplotlib
- adjustText
