"""
MIT License

Copyright (c) 2025 Tiburon Leon Benavides

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Author: Tiburon Leon Benavides
Contribution: Main contributor
Date: 2025-09-10
"""

import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text  
from tqdm import tqdm
import csv
from os.path import exists
from process_two_state_score import frange, get_group_name_lookup, get_v1_ref_df, get_v2_ref_df, get_best_fit_dual_state, create_scatter, create_stacked_bar



def get_best_fit(ID, v1_df, v2_df, score):
    return get_best_fit_dual_state(ID, v1_df, v2_df, score)

# create_stacked_bar function is now imported from process_two_state_score
# Using wrapper to adapt to dual_state version's specific parameters
def create_stacked_bar_dual_state(*args, **kwargs):
    # Set defaults specific to dual_state version
    kwargs.setdefault('v1_color', 'tab:blue')
    kwargs.setdefault('v2_color', '#FA7E0F')
    kwargs.setdefault('ylabel', 'Dual-State Score')
    kwargs.setdefault('title_prefix', 'Dual-State')
    kwargs.setdefault('output_dir', './output/PLOTS')
    
    # Set y-axis limit to maximum Combined_Score
    if len(args) >= 1:
        combined_df = args[0]
        max_combined_score = combined_df['Combined_Score'].max()
        kwargs.setdefault('ylim', (0, max_combined_score))
    
    # Special ID configurations for dual_state
    special_ids = {
        'M1228': {
            'legend_loc_horizontal': 'upper right',
            'legend_loc_vertical': 'upper right',
            'tick_fs_prim_horizontal': 24,
            'tick_fs_sec_horizontal': 32,
            'tick_fs_prim_vertical': 24,
            'tick_fs_sec_vertical': 32,
            'rot_prim_horizontal': 90,
            'rot_prim_vertical': 90,
            'legend_fontsize': 14,
            'label_fontsize': 32
        },
        'R1203': {
            'legend_loc_horizontal': 'upper right',
            'legend_loc_vertical': 'lower right',
            'tick_fs_prim_horizontal': 24,
            'tick_fs_sec_horizontal': 32,
            'tick_fs_prim_vertical': 24,
            'tick_fs_sec_vertical': 32,
            'rot_prim_horizontal': 90,
            'rot_prim_vertical': 0,
            'legend_fontsize': 28,
            'label_fontsize': 32
        },
        'T1214': {
            'legend_loc_horizontal': 'upper right',
            'legend_loc_vertical': 'lower right',
            'tick_fs_prim_horizontal': 18,
            'tick_fs_sec_horizontal': 24,
            'tick_fs_prim_vertical': 18,
            'tick_fs_sec_vertical': 24,
            'rot_prim_horizontal': 90,
            'rot_prim_vertical': 0,
            'legend_fontsize': 28,
            'label_fontsize': 32
        }
    }
    
    # Special figure size configurations
    if len(args) >= 2:
        ID = args[1]
        if len(args) >= 3:
            score = args[2]
            if ID == "R1203" and score == "Σ4":
                kwargs.setdefault('fig_width_horizontal', 20)
                kwargs.setdefault('fig_height_horizontal', 12)
            elif ID == "R1203" and score == "Composite_Score_4":
                kwargs.setdefault('fig_width_vertical', 25)
                kwargs.setdefault('fig_height_vertical', 12)
            elif ID in ["M1228", "R1203"]:
                kwargs.setdefault('fig_width_horizontal', 10)
                kwargs.setdefault('fig_height_horizontal', 15)
                kwargs.setdefault('fig_width_vertical', 15)
                kwargs.setdefault('fig_height_vertical', 10)
    
    kwargs['special_ids'] = special_ids
    return create_stacked_bar(*args, **kwargs)


# create_scatter function is now imported from process_two_state_score


def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, v2_df, score)

    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)

    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
        combined_df['v1_v1_Score'] = combined_df['v1_v1_Score'] * 100
        combined_df['v2_v2_Score'] = combined_df['v2_v2_Score'] * 100
        combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./output/OUTPUT_CSVS/{ID}_{score}_dual_state.csv', index=False)
    

    # print("Creating stacked bar plots...")
    create_stacked_bar_dual_state(combined_df, ID, score, horizontal=False, star=True, outfile_suffix = "_vertical")
    create_stacked_bar_dual_state(combined_df, ID, score, horizontal=True, star=True, outfile_suffix = "_horizontal")
    
    kwargs = {}
    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'save_path': f'./output/PLOTS/{ID}_{score}_scatter_plot_dual_state.png',
        'score': score,
        'xlabel': f'{score} (V1)',
        'ylabel': f'{score} (V2)',
        'title': f'{ID} {score} Dual-State Score',})
    
    if ID == 'T1214' and score == 'TMscore':
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'xticks': [0.80, 0.85, 0.90, 0.95, 1.00],
            'inset': True,
            'inset_position': [0.2, 0.05, 0.4, 0.4],
            'inset_xlim': [0.98, 1.00],
            'inset_ylim': [0.97, 0.99],
            'inset_xticks': [0.98, 0.99, 1.00],
            'inset_yticks': [0.97, 0.98, 0.99],
            'highlight_inset_rect': True,
            'rect_xy': (0.98, 0.97),
            'rect_width': 0.02,
            'rect_height': 0.02,
            'legend_position': 'upper left',
        })
    elif ID == 'T1214' and score == 'GDT_TS':
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'xlim': (60, 100),
            'ylim': (60, 100),
            'xticks': [60, 70, 80, 90, 100],
            'yticks': [60, 70, 80, 90, 100],
            'inset': True,
            'inset_position': [0.2, 0.05, 0.4, 0.6],
            'inset_xlim': [92, 96],
            'inset_ylim': [90, 96],
            'inset_xticks': [92, 94, 96],
            'inset_yticks': [90, 92, 94, 96],
            'highlight_inset_rect': True,
            'rect_xy': (92, 90),
            'rect_width': 4,
            'rect_height': 6,
            'legend_position': 'upper left',
        })
    elif ID == 'T1214' and score == 'GlobalLDDT':
        print(f"Creating scatter plot for {ID} {score}.")
        kwargs.update({
            'inset': True,
            'inset_position': [0.05, 0.4, 0.4, 0.4],
            'inset_xlim': [.82, .86],
            'inset_ylim': [.8, .84],
            'inset_xticks': [.82, .84, .86],
            'inset_yticks': [.80, .82, .84],
            'highlight_inset_rect': True,
            'rect_xy': (.82, .80),
            'rect_width': .04,
            'rect_height': .04,
            'legend_position': 'upper left',
        })
    create_scatter(**kwargs)
    print(f"Done creating stacked bar plots for {ID} {score}")

TARGET_SCORE_DICT = {"T1214": ["GDT_TS", "GlobalLDDT", "TMscore", "Composite_Score_1", "Composite_Score_2", "Composite_Score_3", "Composite_Score_4"]}


for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            raise Exception("Stop here")
            continue



