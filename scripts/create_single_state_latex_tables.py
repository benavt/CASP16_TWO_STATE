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
from process_two_state_score import get_group_name_lookup

OUTPUT_DIR = './output/OUTPUT_CSVS'
LATEX_DIR = './output/SINGLE_STATE_LATEX_TABLES'
COLUMNS = [
    'Group',
    'Group_Name',
    'Best_v1_ref',
    'V1_Model_For_Combined_Score'
]

os.makedirs(LATEX_DIR, exist_ok=True)


def escape_underscores(text):
    if isinstance(text, str):
        return text.replace('_', r'\_')
    return text

def make_long_latex_table(df, caption, label, score_name):
    if score_name == 'GlobalLDDT':
        score_name = 'gLDDT'
    header = (
        "% In your document body:\n"
        "\\begin{longtable}{llll}\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}} \\\\ \n"
        "\\toprule\n"
        f"Group & Group\_Name & V1\_{score_name.replace('_', r'\_')} & V1\_Model \\\\ \n"
        "\\midrule\n"
        "\\endfirsthead\n"
        "\\multicolumn{4}{c}%\n"
        "{{\\tablename\\ \\thetable{} -- continued from previous page}} \\\\ \n"
        "\\toprule\n"
        f"Group & Group\_Name & V1\_{score_name.replace('_', r'\_')} & V1\_Model \\\\ \n"
        "\\midrule\n"
        "\\endhead\n"
        "\\bottomrule\n"
        "\\multicolumn{4}{r}{{Continued on next page}} \\\\ \n"
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
                if col in ['V1_Model_For_Combined_Score']:
                    row_vals.append(na_superscript)
                    has_na_sup = True
                else:
                    row_vals.append(val)
            else:
                if col in ['Group', 'Group_Name', 'V1_Model_For_Combined_Score']:
                    row_vals.append(escape_underscores(val))
                else:
                    # Convert string to float and format to two decimal places

                    try:
                        float_val = float(val)
                        row_vals.append(f"{float_val:.2f}")
                    except (ValueError, TypeError):
                        row_vals.append(val)
        body += (
            f"{row_vals[0]} & {row_vals[1]} & {row_vals[2]} & {row_vals[3]} \\\\ \n"
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
        "\\begin{tabular}{llrl}\n"
        "\\toprule\n"
        f"Group & Group\\_Name & V1\\_{score_name.replace('_', r'\_')} & V1\\_Model \\\\ \n"
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
                if col in ['V1_Model_For_Combined_Score']:
                    row_vals.append(na_superscript)
                    has_na_sup = True
                else:
                    row_vals.append(val)
            else:
                if col in ['Group', 'Group_Name', 'V1_Model_For_Combined_Score']:
                    row_vals.append(escape_underscores(val))
                else:
                    # Convert string to float and format to two decimal places

                    try:
                        float_val = float(val)
                        row_vals.append(f"{float_val:.2f}")
                    except (ValueError, TypeError):
                        row_vals.append(val)
        body += (
            f"{row_vals[0]} & {row_vals[1]} & {row_vals[2]} & {row_vals[3]} \\\\ \n"
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

def make_t1214_sigma4_table():
    """Create special T1214 Sigma4 score table from T1214_Group_vs_Best_Composite_Score_4.csv"""
    for score in '1', '2', '3', '4':
        print(f"Processing {score}")

        # Read the T1214 data
        t1214_data = pd.read_csv(f'T1214_v1_Composite_Score_{score}_best_scores.csv')

        # Get group name lookup using the same function as process_two_state_score.py
        group_name_lookup = get_group_name_lookup()

        # Process the data
        processed_data = []
        for _, row in t1214_data.iterrows():
            model = row['Model']
            group_ts = model.split('_')[0].split('T1214')[1]
            composite_score = row[f'Composite_Score_{score}']
            
            # Extract group number using the same logic as process_two_state_score.py
            group_number = str(int(''.join(filter(str.isdigit, group_ts)))).zfill(3)
            group_name = group_name_lookup.get(group_number, group_ts).strip()
            
            # Parse model to get final character (e.g., T1214TS298_4 -> 4)
            model_suffix = model.split('_')[-1] if '_' in model else model[-1]
            
            # Round composite score to nearest 100th
            sigma_score = round(composite_score, 2)
            
            processed_data.append({
                'Group': group_ts,  # Keep original TS-prefixed group name
                'Group_Name': group_name,
                f'Sigma{score}_Score': sigma_score,
                'Model_Suffix': model_suffix
            })

        # Sort by Sigma4 score in descending order
        processed_df = pd.DataFrame(processed_data)
        processed_df = processed_df.sort_values(f'Sigma{score}_Score', ascending=False)

        # Create LaTeX table
        header = (
             f"% T1214 Sigma{score} Score Table\n"
             "\\begin{table*}[ht]\n"
            f"\\caption{{T1214 Sigma{score} Score Results}}\n"
            f"\\label{{tab:T1214_Sigma_score_split}}\n"
            "\\scriptsize\n"
            "\\begin{minipage}[t]{0.48\\textwidth}\n"
            "\\centering\n"
            "\\begin{tabular}{llrr}\n"
            "\\toprule\n"
            "Group & Group\_Name & $\Sigma_{score}$ Score & Model \\\\ \n"
            "\\midrule\n"
        )

        body = ""
        len_df = len(processed_df)
        len_df_half = len_df // 2
        for idx, row in enumerate(processed_df.itertuples(index=False)):
            group = escape_underscores(str(getattr(row, 'Group')))
            group_name = escape_underscores(str(getattr(row, 'Group_Name')))
            sigma_score = f"{getattr(row, f'Sigma{score}_Score'):.2f}"
            model_suffix = str(getattr(row, 'Model_Suffix'))
            
            body += f"{group} & {group_name} & {sigma_score} & {model_suffix} \\\\ \n"
            
            if idx + 1 == len_df_half:
                # Add block to close first minipage/table and start a new one
                body += (
                    "\\bottomrule\n"
                    "\\end{tabular}\n"
                    "\\end{minipage}\n"
                    "\\hfill\n"
                    "\\begin{minipage}[t]{0.48\\textwidth}\n"
                    "\\centering\n"
                    "\\begin{tabular}{llrr}\n"
                    "\\toprule\n"
                    "Group & Group\_Name & $\Sigma_{score}$ Score & Model \\\\ \n"
                    "\\midrule\n"
                )

        footer = (
            "\\bottomrule\n"
            "\\end{tabular}\n"
            "\\end{minipage}\n"
            "\\end{table*}\n"
        )

        latex_table = header + body + footer

        # Write to file
        tex_path = os.path.join(LATEX_DIR, f'T1214_Sigma{score}_score_table.tex')
        with open(tex_path, 'w') as f:
            f.write(latex_table)
        print(f"Wrote {tex_path}")

    return 

for fname in os.listdir(OUTPUT_DIR):
    if fname.endswith('.csv') and fname.find('single_state') != -1:
        csv_path = os.path.join(OUTPUT_DIR, fname)
        df = pd.read_csv(csv_path)
        # Only keep the required columns, skip if not all present
        if not all(col in df.columns for col in COLUMNS):
            print(f"Skipping {fname}: missing required columns.")
            continue
        df = df[COLUMNS]
        # Format numbers for publication
        df['Best_v1_ref'] = df['Best_v1_ref'].map(lambda x: f"{x:.4f}")
        caption = f"Results for {fname.replace('_', ' ').replace('.csv', '')}"
        caption = caption.replace('two state', 'Single-State')
        label = f"tab:{fname.replace('.csv','')}"
        # Extract score_name from filename
        base = os.path.basename(fname)
        try:
            score_name = base[base.index('_')+1:base.index('_single')]
        except ValueError:
            score_name = 'score'
        latex_table = make_latex_table(df, caption, label, score_name)
        tex_path = os.path.join(LATEX_DIR, fname.replace('.csv', '.tex'))
        with open(tex_path, 'w') as f:
            f.write(latex_table)
        print(f"Wrote {tex_path}") 