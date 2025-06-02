import os
import pandas as pd

OUTPUT_DIR = './OUTPUT'
LATEX_DIR = './LATEX_TABLES'
COLUMNS = [
    'Group',
    'Group_Name',
    'Combined_Score',
    'Best_v1_ref',
    'Best_v2_ref',
    'V1_Model_For_Combined_Score',
    'V2_Model_For_Combined_Score'
]

os.makedirs(LATEX_DIR, exist_ok=True)

def escape_underscores(text):
    if isinstance(text, str):
        return text.replace('_', r'\_')
    return text

def make_latex_table(df, caption, label, score_name):
    header = (
        "% In your preamble:\n"
        "\\begin{table}[ht]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        "\\scriptsize\n"
        "\\resizebox{\\textwidth}{!}{%\n"
        "\\begin{tabular}{llrrrll}\n"
        "\\toprule\n"
        f"Group & Group\\_Name & Two-State\\_Score & V1\\_{score_name} & V2\\_{score_name} & V1\\_Model & V2\\_Model \\\\ \n"
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
                    row_vals.append(val)
        body += (
            f"{row_vals[0]} & {row_vals[1]} & {row_vals[2]} & {row_vals[3]} & {row_vals[4]} & {row_vals[5]} & {row_vals[6]} \\\\ \n"
        )
    footer = (
        "\\bottomrule\n"
        "\\end{tabular}%\n"
        "}\n"
    )
    if has_na_sup:
        footer += "\\begin{flushleft}\\footnotesize $^{1}$ Model either not submitted or analyzed\\end{flushleft}\n"
    footer += "\\end{table}\n"
    return header + body + footer

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