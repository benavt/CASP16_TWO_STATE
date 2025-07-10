import os
import pandas as pd
import csv

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
        f"Group & Group\\_Name & Two-State\\_Score & V1\\_{score_name.replace('_', r'\_')} & V2\\_{score_name.replace('_', r'\_')} & V1\\_Model & V2\\_Model \\\\ \n"
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
            f"{row_vals[0]} & {row_vals[1]} & {row_vals[2]} & {row_vals[3]} & {row_vals[4]} & {row_vals[5]} & {row_vals[6]} \\\\ \n"
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
    
    # Read the T1214 data
    t1214_data = pd.read_csv('T1214_Group_vs_Best_Composite_Score_4.csv')
    
    # Get group name lookup using the same function as process_two_state_score.py
    group_name_lookup = get_group_name_lookup()
    
    # Process the data
    processed_data = []
    for _, row in t1214_data.iterrows():
        group_ts = row['Group']  # e.g., "TS298"
        model = row['Model']
        composite_score = row['Composite_Score']
        
        # Extract group number using the same logic as process_two_state_score.py
        group_number = str(int(''.join(filter(str.isdigit, group_ts)))).zfill(3)
        group_name = group_name_lookup.get(group_number, group_ts).strip()
        
        # Parse model to get final character (e.g., T1214TS298_4 -> 4)
        model_suffix = model.split('_')[-1] if '_' in model else model[-1]
        
        # Round composite score to nearest 100th
        sigma4_score = round(composite_score, 2)
        
        processed_data.append({
            'Group': group_ts,  # Keep original TS-prefixed group name
            'Group_Name': group_name,
            'Sigma4_Score': sigma4_score,
            'Model_Suffix': model_suffix
        })
    
    # Sort by Sigma4 score in descending order
    processed_df = pd.DataFrame(processed_data)
    processed_df = processed_df.sort_values('Sigma4_Score', ascending=False)
    
    # Create LaTeX table
    header = (
        "% T1214 Sigma4 Score Table\n"
        "\\begin{table}[ht]\n"
        "\\centering\n"
        "\\caption{T1214 Sigma4 Score Results}\n"
        "\\label{tab:T1214_Sigma4_score}\n"
        "\\scriptsize\n"
        "\\resizebox{\\textwidth}{!}{%\n"
        "\\begin{tabular}{llrr}\n"
        "\\toprule\n"
        "Group & Group\\_Name & $\\sigma_4$ Score & Model \\\\ \n"
        "\\midrule\n"
    )
    
    body = ""
    for _, row in processed_df.iterrows():
        group = escape_underscores(str(row['Group']))
        group_name = escape_underscores(str(row['Group_Name']))
        sigma4_score = f"{row['Sigma4_Score']:.2f}"
        model_suffix = str(row['Model_Suffix'])
        
        body += f"{group} & {group_name} & {sigma4_score} & {model_suffix} \\\\ \n"
    
    footer = (
        "\\bottomrule\n"
        "\\end{tabular}%\n"
        "}\n"
        "\\end{table}\n"
    )
    
    latex_table = header + body + footer
    
    # Write to file
    tex_path = os.path.join(LATEX_DIR, 'T1214_Sigma4_score_table.tex')
    with open(tex_path, 'w') as f:
        f.write(latex_table)
    print(f"Wrote {tex_path}")
    
    return processed_df

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