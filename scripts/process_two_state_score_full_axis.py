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
from process_two_state_score import get_v1_ref_df, get_v2_ref_df, frange, get_group_name_lookup, get_best_fit, create_scatter



# get_best_fit function is now imported from process_two_state_score

# create_scatter function is now imported from process_two_state_score
# Using wrapper to adapt to full_axis version's specific parameters
def create_scatter_full_axis(*args, **kwargs):
    # Set defaults specific to full_axis version
    kwargs.setdefault('figsize', (8, 8))
    kwargs.setdefault('diagonal_line_color', 'black')
    kwargs.setdefault('diagonal_line_style', '--')
    kwargs.setdefault('scatter_size', 100)
    kwargs.setdefault('show_grid', True)
    kwargs.setdefault('xlabel_fontsize', 30)
    kwargs.setdefault('ylabel_fontsize', 30)
    kwargs.setdefault('title_fontsize', 20)
    kwargs.setdefault('tick_labelsize', 25)
    kwargs.setdefault('text_fontsize', 12)
    kwargs.setdefault('adjust_texts', False)
    kwargs.setdefault('show_group_labels', False)  # Don't show group labels by default for full_axis plots
    kwargs.setdefault('show_legend', False)  # Don't show legend by default for full_axis plots
    return create_scatter(*args, **kwargs)

def assessment(ID, score):
    
    v1_df = get_v1_ref_df(ID, score)
    v2_df = get_v2_ref_df(ID, score)
    combined_df = get_best_fit(ID, v1_df, v2_df, score)
    # Sort the combined_df by 'Combined_Score' in descending order
    combined_df = combined_df.sort_values(by='Combined_Score', ascending=False)
    # Convert GDT_TS scores to percentage
    if score == 'GDT_TS':
        if max(combined_df['Best_v1_ref']) <= 1:
            combined_df['Best_v1_ref'] = combined_df['Best_v1_ref'] * 100
        if max(combined_df['Best_v2_ref']) <= 1:
            combined_df['Best_v2_ref'] = combined_df['Best_v2_ref'] * 100
        if max(combined_df['Combined_Score']) <= 2:
            combined_df['Combined_Score'] = combined_df['Combined_Score'] * 100

    # Save the combined metric to a CSV file
    combined_df.to_csv(f'./output/OUTPUT_CSVS/{ID}_{score}_two_state.csv', index=False)
    
    kwargs = {}
    # Set text fontsize for specific IDs
    if ID in ["M1239", "M1228"]:
        kwargs['text_fontsize'] = 16
    if score == 'TMscore':
        label = 'TM-score'
    else:
        label = score

    # Default scatter plot parameters
    kwargs.update({
        'x': combined_df[f"Best_v1_ref"],
        'y': combined_df[f"Best_v2_ref"],
        'group_labels': combined_df['Group'],
        'xlabel': f'{label} (V1)',
        'ylabel': f'{label} (V2)',
        'title': f'{ID} {label}',
        'save_path': f'./output/PLOTS/{ID}_{score}_scatter_plot_full_axis.png',
        'score': score
    })

    if score == 'TMscore':
        kwargs.update({
            'xlim': (0.0, 1.0),
            'ylim': (0.0, 1.0),
            'xticks': [0.0, 0.5, 1.0],
            'yticks': [0.0, 0.5, 1.0],
        })
    elif score == 'GDT_TS':
        kwargs.update({
            'xlim': (0.0, 100.0),
            'ylim': (0.0, 100.0),
            'xticks': [0, 50, 100],
            'yticks': [0, 50, 100],
        })
    # Call create_scatter once with all kwargs
    result = create_scatter(**kwargs)
    return

TARGET_SCORE_DICT = {"M1228": ["GDT_TS", "TMscore"], 
                     "M1239": ["GDT_TS", "TMscore"], 
                     "R1203": ["GDT_TS", "TMscore"], 
                     "T1228": ["GDT_TS", "TMscore"], 
                     "T1239": ["GDT_TS", "TMscore"],
                     "T1249": ["GDT_TS", "TMscore"],
                     "T1214": ["GDT_TS", "TMscore"]}


for ID, scores in TARGET_SCORE_DICT.items():
    for score in scores:
        try:
            assessment(ID, score)
            print(f"[SUCCESS] Processed {ID} {score}")
        except Exception as e:
            print(f"[ERROR] Error processing {ID} {score}: {e}")
            raise Exception("Stop here")
            continue

