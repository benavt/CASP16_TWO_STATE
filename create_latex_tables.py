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

def make_latex_table(df, caption, label):
    header = (
        "% In your preamble:\n"
        "\\begin{table}[ht]\n"
        "\\centering\n"
        f"\\caption{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        "\\resizebox{\\textwidth}{!}{%\n"
        "\\begin{tabular}{llrrrll}\n"
        "\\toprule\n"
        "Group & Group\\_Name & Combined\\_Score & Best\\_v1\\_ref & Best\\_v2\\_ref & V1\\_Model\\_For\\_Combined\\_Score & V2\\_Model\\_For\\_Combined\\_Score \\\\ \n"
        "\\midrule\n"
    )
    body = ""
    for _, row in df.iterrows():
        body += (
            f"{escape_underscores(row['Group'])} & {escape_underscores(row['Group_Name'])} & {row['Combined_Score']} & {row['Best_v1_ref']} & {row['Best_v2_ref']} & {escape_underscores(row['V1_Model_For_Combined_Score'])} & {escape_underscores(row['V2_Model_For_Combined_Score'])} \\\\ \n"
        )
    footer = (
        "\\bottomrule\n"
        "\\end{tabular}%\n"
        "}\n"
        "\\end{table}\n"
    )
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
        label = f"tab:{fname.replace('.csv','')}"
        latex_table = make_latex_table(df, caption, label)
        tex_path = os.path.join(LATEX_DIR, fname.replace('.csv', '.tex'))
        with open(tex_path, 'w') as f:
            f.write(latex_table)
        print(f"Wrote {tex_path}") 