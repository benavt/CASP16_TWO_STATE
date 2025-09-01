"""
MIT License

Copyright (c) 2025 Tiburon Leon Benavides

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Author: Tiburon Leon Benavides
Contribution: Main contributor
Date: 2025-09-01
"""

import os
import pandas as pd
import csv

OUTPUT_DIR = './OUTPUT'
LATEX_DIR = './LATEX_TABLES_BALANCE'
COLUMNS = [
    'Group',
    'Group_Name',
    'Combined_Score',
    'Balance',
    'Best_v1_ref',
    'Best_v2_ref',
    'V1_Model_For_Combined_Score',
    'V2_Model_For_Combined_Score'
]

os.makedirs(LATEX_DIR, exist_ok=True)

def get_group_name_lookup():
    """Get group name lookup from the correspondence CSV file"""
    lookup = {}
    with open('group_number_name_correspondance.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lookup[row['Group Number'].zfill(3)] = row['Group Name']
    return lookup

def escape_underscores(text):
    if isinstance(text, str):
        return text.replace('_', r'\_')
    return text


def make_long_latex_table(df, caption, label, score_name):
    if score_name.startswith('Composite_Score'):
        score_name = score_name.replace('Composite_Score', 'CS')
    header = (
        "% In your document body:\n"
        "\\begin{longtable}{llllllll}\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}} \\\\ \n"
        "\\toprule\n"
        f"Group & Group\_Name & Two-State\_Score & Balance & V1\_{score_name.replace('_', r'\_')} & V2\_{score_name.replace('_', r'\_')} & V1\_Model & V2\_Model \\\\ \n"
        "\\midrule\n"
        "\\endfirsthead\n"
        "\\multicolumn{8}{c}%\n"
        "{{\\tablename\\ \\thetable{} -- continued from previous page}} \\\\ \n"
        "\\toprule\n"
        f"Group & Group\_Name & Two-State\_Score & Balance & V1\_{score_name.replace('_', r'\_')} & V2\_{score_name.replace('_', r'\_')} & V1\_Model & V2\_Model \\\\ \n"
        "\\midrule\n"
        "\\endhead\n"
        "\\bottomrule\n"
        "\\multicolumn{8}{r}{{Continued on next page}} \\\\ \n"
        "\\endfoot\n"
        "\\bottomrule\n"
        # "\\multicolumn{8}{l}\\\\ \n"
        "\\endlastfoot\n"
    )
    body = ""
    na_superscript = 'N/A$^{1}$'
    has_na_sup = False
    for _, row in df.iterrows():
        row_vals = []
        for col in COLUMNS:
            val = row[col]
            if pd.isna(val) or val == 0.0 or (isinstance(val, str) and 'None' in val):
                if col in ['V1_Model_For_Combined_Score', 'V2_Model_For_Combined_Score']:
                    row_vals.append(na_superscript)
                    has_na_sup = True
                else:
                    row_vals.append(val)
            else:
                if col in ['Group', 'Group_Name', 'V1_Model_For_Combined_Score', 'V2_Model_For_Combined_Score']:
                    row_vals.append(escape_underscores(val))
                else:
                    # Convert string to float and format to two decimal places

                    try:
                        float_val = float(val)
                        row_vals.append(f"{float_val:.2f}")
                    except (ValueError, TypeError):
                        row_vals.append(val)
        body += (
            f"{row_vals[0]} & {row_vals[1]} & {row_vals[2]} & {row_vals[3]} & {row_vals[4]} & {row_vals[5]} & {row_vals[6]} & {row_vals[7]} \\\\ \n"
        )
    footer = (
        "\\end{longtable}\n"
    )
    if has_na_sup:
        footer += "\\begin{flushleft}\\footnotesize $^{1}$ Model either not submitted or not assessed\\end{flushleft}\n"
    footer += "\\end{table}\n"
    return header + body + footer


def make_latex_table(df, caption, label, score_name):
    if len(df) > 63:
        return make_long_latex_table(df, caption, label, score_name)

    header = (
        "% In your preamble:\n"
        "\\begin{table}[ht]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        "\\scriptsize\n"
        "\\resizebox{\\textwidth}{!}{%\n"
        "\\begin{tabular}{llllllll}\n"
        "\\toprule\n"
        f"Group & Group\\_Name & Two-State\\_Score & Balance & V1\\_{score_name.replace('_', r'\_')} & V2\\_{score_name.replace('_', r'\_')} & V1\\_Model & V2\\_Model \\\\ \n"
        "\\midrule\n"
    )
    body = ""
    na_superscript = 'N/A$^{1}$'
    has_na_sup = False
    for _, row in df.iterrows():
        row_vals = []
        for col in COLUMNS:
            val = row[col]
            if pd.isna(val) or val == 0.0 or (isinstance(val, str) and 'None' in val):
                if col in ['V1_Model_For_Combined_Score', 'V2_Model_For_Combined_Score']:
                    row_vals.append(na_superscript)
                    has_na_sup = True
                else:
                    row_vals.append(val)
            else:
                if col in ['Group', 'Group_Name', 'V1_Model_For_Combined_Score', 'V2_Model_For_Combined_Score']:
                    row_vals.append(escape_underscores(val))
                else:
                    # Convert string to float and format to two decimal places

                    try:
                        float_val = float(val)
                        row_vals.append(f"{float_val:.2f}")
                    except (ValueError, TypeError):
                        row_vals.append(val)
        body += (
            f"{row_vals[0]} & {row_vals[1]} & {row_vals[2]} & {row_vals[3]} & {row_vals[4]} & {row_vals[5]} & {row_vals[6]} & {row_vals[7]} \\\\ \n"
        )
    footer = (
        "\\bottomrule\n"
        "\\end{tabular}%\n"
        "}\n"
    )
    if has_na_sup:
        footer += "\\begin{flushleft}\\footnotesize $^{1}$ Model either not submitted or not assessed\\end{flushleft}\n"
    footer += "\\end{table}\n"
    return header + body + footer

from create_latex_tables import make_t1214_sigma4_table
# Create the special T1214 Sigma4 table
make_t1214_sigma4_table()

for fname in os.listdir(OUTPUT_DIR):
    if fname.endswith('.csv'):
        csv_path = os.path.join(OUTPUT_DIR, fname)
        df = pd.read_csv(csv_path)
        # Only keep the required columns, skip if not all present
        if not all(col in df.columns for col in COLUMNS):
            print(f"Skipping {fname}: missing required columns.")
            continue
        df = df[COLUMNS]
        # Format numbers for publication
        df['Combined_Score'] = df['Combined_Score'].map(lambda x: f"{x:.4f}")
        df['Best_v1_ref'] = df['Best_v1_ref'].map(lambda x: f"{x:.4f}")
        df['Best_v2_ref'] = df['Best_v2_ref'].map(lambda x: f"{x:.4f}")
        caption = f"Results for {fname.replace('_', ' ').replace('.csv', '')}"
        caption = caption.replace('two state', 'Two-State Score')
        label = f"tab:{fname.replace('.csv','')}"
        # Extract score_name from filename
        base = os.path.basename(fname)
        try:
            score_name = base[base.index('_')+1:base.index('_two')]
        except ValueError:
            score_name = 'score'
        latex_table = make_latex_table(df, caption, label, score_name)
        tex_path = os.path.join(LATEX_DIR, fname.replace('.csv', '.tex'))
        with open(tex_path, 'w') as f:
            f.write(latex_table)
        print(f"Wrote {tex_path}") 