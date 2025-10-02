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


# get_best_fit function is now imported from process_two_state_score

# create_stacked_bar function is now imported from process_two_state_score
# Using wrapper with simple_bar_plots specific configurations
def create_stacked_bar_simple(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = ""):
    # Build special_ids configurations
    score_replaced = score.replace('Updated_','')
    if score_replaced == 'Composite_Score_4':
        score_replaced = 'Σ4'
    import matplotlib.pyplot as plt
    num_groups = len(combined_df)
    per_group, min_size, max_size = 0.35, 6, 20
    dynamic_size = max(min_size, min(max_size, num_groups * per_group))

    if horizontal:
        if ID != "M1228" and ID != "R1203":
            fig_size = (dynamic_size, 12)
        elif ID == "R1203" and score == "Σ4":
            fig_size = (20, 12)
        else:
            fig_size = (10, 15)
        bar_func, stack_param, line_func, line_param = plt.Axes.bar, 'bottom', plt.Axes.axvline, 'x'
        limit_set, label_prim, label_sec = plt.Axes.set_xlim, 'xlabel', 'ylabel'

        if ID != "M1228" and ID != "R1203":
            if ID == "T1214" and score == "Σ4":
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 18, 24, 90
            else:
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 24, 32, 90
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'upper right', 24, 32, 90
    else:
        if ID != "M1228" and ID != "R1203":
            fig_size = (12, dynamic_size)
        elif ID == "R1203" and score == "Composite_Score_4":
            fig_size = (25, 12)
        else:
            fig_size = (15, 10)
        bar_func, stack_param, line_func, line_param = plt.Axes.barh, 'left', plt.Axes.axhline, 'y'
        limit_set, label_prim, label_sec = plt.Axes.set_ylim, 'ylabel', 'xlabel'
        if ID != "M1228":
            if ID == "T1214" and score == "Σ4":
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 18, 24, 0
            else:
                legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 24, 32, 0
        else:
            legend_loc, tick_fs_prim, tick_fs_sec, rot_prim = 'lower right', 32, 32, 0
    
    fig, ax = plt.subplots(figsize=fig_size)
    group_labels_raw = combined_df['Group'].str.replace('TS', '')
    if horizontal:
        df_to_use = combined_df
        group_labels = group_labels_raw
        check_labels = group_labels.values
        bar_size_param, bar_size = 'width', 0.9
    else:
        df_to_use = combined_df.iloc[::-1]
        group_name_lookup = get_group_name_lookup()
        group_labels, check_labels = [], []
        for group in df_to_use['Group']:
            group_id = str(int(''.join(filter(str.isdigit, group)))).zfill(3)
            group_name = group_name_lookup.get(group_id, group).strip()
            group_labels.append(f"{group_name} ({group_id})")
            check_labels.append(group_id)
        bar_size_param, bar_size = 'height', 0.9
    v1_colors = ['tab:blue'] * num_groups
    v2_colors = ['#FA7E0F'] * num_groups
    
    # # Color group 304 bars with teal
    # if '304' in check_labels:
    #     idx_304 = list(check_labels).index('304')
    #     v1_colors[idx_304] = 'cyan'
    #     v2_colors[idx_304] = 'yellow'

    if num_groups > 100:

        if score != "TMscore":  
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'{score} (V1)', 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'{score} (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'TM-score (V1)', 'color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'TM-score (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    else:
        if score != "TMscore":
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'{score} (V1)','color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'{score} (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
        else:
            bar_kwargs_v1 = {bar_size_param: bar_size, 'label': f'TM-score (V1)','color': v1_colors}
            bar_kwargs_v2 = {bar_size_param: bar_size, 'label': f'TM-score (V2)', 'color': v2_colors, stack_param: df_to_use[f'Best_v1_ref']}
    bars_v1 = bar_func(ax, group_labels, df_to_use[f'Best_v1_ref'], **bar_kwargs_v1)
    bars_v2 = bar_func(ax, group_labels, df_to_use[f'Best_v2_ref'], **bar_kwargs_v2)
    
    # Add star above group 304 bar
    if '304' in check_labels:
        idx_304 = list(check_labels).index('304')
        total_score = df_to_use[f'Best_v1_ref'].iloc[idx_304] + df_to_use[f'Best_v2_ref'].iloc[idx_304]
        print("Total score for 304: ", total_score)
        
        # Calculate position for the star
        if horizontal:
            # For horizontal bars (vertical bars), star goes above the bar
            star_x = idx_304
            star_y = total_score + 1  # Slightly above the bar
            ax.plot(star_x, star_y, 'k*', markersize=15, markeredgecolor='black', markerfacecolor='yellow')
            # Draw horizontal line at y position of group 304
            ax.axhline(y=total_score, color='grey', linestyle='--', linewidth=4, label='AF3 Score')
        else:
            # For vertical bars (horizontal bars), star goes above the bar
            star_x = total_score + 1  # Slightly to the right of the bar
            star_y = idx_304
            ax.plot(star_x, star_y, 'k*', markersize=15, markeredgecolor='black', markerfacecolor='yellow')
            # Draw vertical line at x position of group 304
            ax.axvline(x=total_score, color='grey', linestyle='--', linewidth=4, label='AF3 Score')
    limit_set(ax, -0.5, len(group_labels) - 0.5)
    getattr(ax, f'set_{label_prim}')('Group', fontsize= 32)
    getattr(ax, f'set_{label_sec}')('Two-State Score', fontsize=32)
    if score != "TMscore":
        ax.set_title(f'Two-State {score} scores for \n {ID} V1 and V2 reference states', fontsize=18)
    else:
        ax.set_title(f'Two-State TM-scores for \n {ID} V1 and V2 reference states', fontsize=14)
    if ID != 'T1214':
        if ID != "M1228":
            ax.legend(loc=legend_loc, fontsize=28)
        else:
            ax.legend(loc=legend_loc, fontsize=14)
    if horizontal:
        ax.set_xticks(range(len(group_labels)))
        ax.set_xticklabels(group_labels, rotation=rot_prim, fontsize=tick_fs_prim)
        ax.set_yticks(ax.get_yticks())
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=tick_fs_sec)
    else:
        ax.set_yticks(range(len(group_labels)))
        ax.set_yticklabels(group_labels, fontsize=tick_fs_prim)
        ax.set_xticks(ax.get_xticks())
        ax.set_xticklabels(ax.get_xticklabels(), fontsize=tick_fs_sec)
    plt.tight_layout()
    for spine in ax.spines.values():
        spine.set_linewidth(3)
        spine.set_edgecolor('black')
    plt.savefig(f'./output/PLOTS/{ID}_{score}_two_state{outfile_suffix}.png', dpi=300)
    plt.close()

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, v2_df, score)
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        if max(combined_df['Best_v1_ref']) < 1:
            combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        if max(combined_df['Best_v2_ref']) < 1:
            combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./output/OUTPUT_CSVS/{ID}_{score}_two_state.csv', index=False)
  

    print("Creating stacked bar plots...")
    create_stacked_bar(combined_df, ID, score, horizontal=False, star=False, outfile_suffix = "_horizontal_simple")
    create_stacked_bar(combined_df, ID, score, horizontal=True, star=False, outfile_suffix = "_vertical_simple")
    print(f"Done creating stacked bar plots for {ID} {score}")



TARGET_SCORE_DICT = {"M1228": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "M1239": ["BestDockQ", "GDT_TS", "GlobDockQ", "GlobalLDDT", "TMscore"], 
                     "R1203": ["GDT_TS", "GlobalLDDT", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3", "Composite_Score_4", "TMscore"], 
                     "T1214": ["GDT_TS", "GlobalLDDT", "TMscore", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3", "Composite_Score_4"],
                     "T1228": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1239": ["GDT_TS", "GlobalLDDT", "TMscore"], 
                     "T1249": ["AvgDockQ", "GlobalLDDT", "GDT_TS", "TMscore"]}

for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            raise Exception("Stop here")
            continue

