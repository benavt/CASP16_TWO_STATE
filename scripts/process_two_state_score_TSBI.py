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

import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text  
from tqdm import tqdm
import csv
from os.path import exists
from process_two_state_score import get_v1_ref_df, get_v2_ref_df, frange, get_group_name_lookup, get_best_fit, create_stacked_bar


def calc_TSBI_score(v1_ref, v2_ref):
    if v1_ref == 0 or v2_ref == 0:  
        return 0, -1
    balance = 1 - abs(v1_ref - v2_ref) / (v1_ref + v2_ref)
    tsbi = balance * (v1_ref + v2_ref)
    return balance, tsbi

def get_best_fit_TSBI(ID, v1_df, v2_df, score):
    # Get the base results from the main get_best_fit function
    results_df = get_best_fit(ID, v1_df, v2_df, score)
    
    # Add TSBI-specific calculations
    results_df['Balance'] = results_df.apply(lambda row: calc_TSBI_score(row['Best_v1_ref'], row['Best_v2_ref'])[0], axis=1)
    results_df['TSBI_Score'] = results_df.apply(lambda row: calc_TSBI_score(row['Best_v1_ref'], row['Best_v2_ref'])[1], axis=1)
    
    return results_df

def create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = ""):
    import matplotlib.pyplot as plt

    # Use TSBI_Score for the bar plot
    if 'TSBI_Score' not in combined_df.columns:
        raise ValueError("TSBI_Score column not found in combined_df.")

    # Sort by TSBI_Score descending for correct bar order
    df_to_use = combined_df.sort_values(by='TSBI_Score', ascending=False).reset_index(drop=True)
    num_groups = len(df_to_use)
    per_group, min_size, max_size = 0.35, 6, 20
    dynamic_size = max(min_size, min(max_size, num_groups * per_group))

    # Prepare group labels (show group name and number if available)
    group_name_lookup = get_group_name_lookup()

    # Set TSBI_Score == -1 to 0 for plotting
    tsbi_scores_for_plot = df_to_use['TSBI_Score'].copy()
    tsbi_scores_for_plot = tsbi_scores_for_plot.apply(lambda x: 0 if x == -1 else x)

    # Plotting
    if horizontal:
        group_labels = []
        for group in df_to_use['Group']:
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            group_name = group_name_lookup.get(group_id, group).strip()
            group_labels.append(f"{group_id}")

        # Reverse the order of the data for plotting
        fig, ax = plt.subplots(figsize=(dynamic_size, 12))
        # Reverse the order of the data
        x_pos = range(num_groups)
        bars = ax.bar(x_pos, tsbi_scores_for_plot, color='#1A80BB')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(group_labels, rotation=90, fontsize=14)
        ax.set_ylabel('TSBI Score', fontsize=18)
        ax.set_xlabel('Submission Group', fontsize=18)
        ax.set_ylim(bottom=0)
    else:
        group_labels = []
        for group in df_to_use['Group']:
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            group_name = group_name_lookup.get(group_id, group).strip()
            group_labels.append(f"{group_name} ({group_id})")

        fig, ax = plt.subplots(figsize=(12, dynamic_size))
        # Order bars in decreasing order of TSBI_Score (already sorted above)
        y_pos = range(num_groups)
        tsbi_scores_for_plot_reversed = tsbi_scores_for_plot[::-1]
        bars = ax.barh(y_pos, tsbi_scores_for_plot_reversed, color='#1A80BB')
        group_labels_reversed = group_labels[::-1]
        ax.set_yticks(y_pos)
        ax.set_yticklabels(group_labels_reversed, fontsize=14)
        ax.set_xlabel('TSBI Score', fontsize=18)
        ax.set_ylabel('Submission Group', fontsize=18)
        ax.set_xlim(left=0)

    # Highlight AF3-server (group 304) if present
    if '304' in [str(int(''.join(filter(str.isdigit, g)))).zfill(3) for g in df_to_use['Group']]:
        idx_304 = None
        for idx, group in enumerate(df_to_use['Group']):
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            if group_id == '304':
                idx_304 = idx
                break
        if not(horizontal):
            idx_304 = num_groups - idx_304 - 1
        if idx_304 is not None:
            if horizontal:
                bars[idx_304].set_color('#4F81BD')
            else:
                bars[idx_304].set_color('#4F81BD')
            if star:
                # Add a gray star above (vertical) or to the right (horizontal) of the bar for group 304
                if horizontal:
                    ax.scatter(idx_304, tsbi_scores_for_plot.iloc[idx_304] + 0.02 * ax.get_ylim()[1], marker='*', s=300, color='gray', edgecolor='black', zorder=5)
                else:
                    ax.scatter(tsbi_scores_for_plot_reversed.iloc[idx_304] + 0.02 * ax.get_xlim()[1], idx_304, marker='*', s=300, color='gray', edgecolor='black', zorder=5)

                    
    # Title
    ax.set_title(f'TSBI Score for {ID}', fontsize=20)

    # Style
    plt.tight_layout()
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_edgecolor('black')

    plt.savefig(f'./output/TSBI_PLOTS/{ID}_{score}_TSBI_bar{outfile_suffix}.png', dpi=300)
    plt.close()

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit_TSBI(ID, v1_df, v2_df, score)
    
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='TSBI_Score', ascending=False)

    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        if max(combined_df['Best_v1_ref']) < 1:
            combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        if max(combined_df['Best_v2_ref']) < 1:
            combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./output/OUTPUT_CSVS/{ID}_{score}_two_state.csv', index=False)

    print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_vertical_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_horizontal_star")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = "_vertical_no_star")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=False, outfile_suffix = "_horizontal_no_star")
    print(f"Done creating stacked bar plots for {ID} {score}")



TARGET_SCORE_DICT = {"M1228": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "M1239": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "R1203": ["GDT_TS", "GlobalLDDT", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3","Composite_Score_4", "TMscore"], 
                     "T1214": ["GDT_TS", "GlobalLDDT", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3", "Composite_Score_4"],
                     "T1228": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1239": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1249": ["AvgDockQ", "GlobalLDDT", "GDT_TS", "TMscore"]}


for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        print(f"Processing {ID} {score}")
        assessment(ID, score)
        print(f"[SUCCESS] Processed {ID} {score}")
        

